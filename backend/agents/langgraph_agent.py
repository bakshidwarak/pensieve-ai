import os
import json
import logging
from typing import List, Dict, Any, Optional, TypedDict, Annotated
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from services.vector_db import VectorDBService
from services.web_search import WebSearchService
from models.schemas import AgentAnalysis, SearchResult, WebSearchResult

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State schema for the LangGraph agent system"""
    # Input
    query: str
    context: str
    
    # Analysis
    analysis: Optional[AgentAnalysis]
    
    # Agent results
    meeting_results: List[SearchResult]
    web_results: List[WebSearchResult]
    
    # Final response
    response: str
    error: Optional[str]
    
    # Metadata
    messages: Annotated[List[BaseMessage], "add_messages"]

class LangGraphAgentSystem:
    """LangGraph-based agent system for RAG orchestration"""
    
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4",
            temperature=0.7
        )
        
        self.vector_db = VectorDBService()
        self.web_search = WebSearchService()
        
        # Create the graph
        self.graph = self._create_graph()
        
        # Memory for conversation state
        self.memory = MemorySaver()
    
    def _create_graph(self) -> StateGraph:
        """Create the LangGraph workflow"""
        
        # Create the state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("analyze", self._analyze_node)
        workflow.add_node("meeting_agent", self._meeting_agent_node)
        workflow.add_node("web_agent", self._web_agent_node)
        workflow.add_node("synthesize", self._synthesize_node)
        workflow.add_node("error_handler", self._error_handler_node)
        
        # Add edges
        workflow.set_entry_point("analyze")
        
        # Conditional routing from analyze
        workflow.add_conditional_edges(
            "analyze",
            self._route_from_analysis,
            {
                "meeting_agent": "meeting_agent",
                "web_agent": "web_agent", 
                "both": "meeting_agent",  # Start with meeting, then web
                "synthesize": "synthesize",
                "error": "error_handler"
            }
        )
        
        # From meeting agent
        workflow.add_conditional_edges(
            "meeting_agent",
            self._route_from_meeting,
            {
                "web_agent": "web_agent",
                "synthesize": "synthesize",
                "error": "error_handler"
            }
        )
        
        # From web agent
        workflow.add_edge("web_agent", "synthesize")
        
        # From synthesize
        workflow.add_edge("synthesize", END)
        
        # From error handler
        workflow.add_edge("error_handler", END)
        
        return workflow.compile(checkpointer=self.memory)
    
    async def _analyze_node(self, state: AgentState) -> AgentState:
        """Analyze the query to determine which agents to run"""
        try:
            logger.info("🔍 Analyzing query...")
            
            analysis = await self._analyze_query(state["query"], state["context"])
            
            return {
                **state,
                "analysis": analysis
            }
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            return {
                **state,
                "error": f"Analysis failed: {str(e)}"
            }
    
    async def _meeting_agent_node(self, state: AgentState) -> AgentState:
        """Run the meeting notes agent"""
        try:
            logger.info("📝 Running meeting agent...")
            
            # Initialize vector DB if needed
            await self.vector_db.initialize()
            
            # Search meeting notes
            search_results = await self.vector_db.search_documents(
                query=state["query"],
                limit=5
            )
            
            if search_results["success"]:
                meeting_results = self._process_meeting_notes_search_results(search_results)
            else:
                meeting_results = []
            
            return {
                **state,
                "meeting_results": meeting_results
            }
        except Exception as e:
            logger.error(f"❌ Meeting agent error: {e}")
            return {
                **state,
                "meeting_results": [],
                "error": f"Meeting search failed: {str(e)}"
            }
    
    async def _web_agent_node(self, state: AgentState) -> AgentState:
        """Run the web search agent"""
        try:
            logger.info("🌐 Running web agent...")
            
            # Perform web search
            web_results = await self.web_search.search(state["query"])
            
            return {
                **state,
                "web_results": web_results
            }
        except Exception as e:
            logger.error(f"❌ Web agent error: {e}")
            return {
                **state,
                "web_results": [],
                "error": f"Web search failed: {str(e)}"
            }
    
    async def _synthesize_node(self, state: AgentState) -> AgentState:
        """Synthesize results from all agents into final response"""
        try:
            logger.info("🧠 Synthesizing results...")
            
            # Prepare context for synthesis
            context_parts = []
            
            if state.get("context"):
                context_parts.append(f"User Context: {state['context']}")
            
            if state.get("meeting_results"):
                meeting_context = self._format_meeting_results(state["meeting_results"])
                context_parts.append(f"Meeting Notes:\n{meeting_context}")
            
            if state.get("web_results"):
                web_context = self._format_web_results(state["web_results"])
                context_parts.append(f"Web Search Results:\n{web_context}")
            
            full_context = "\n\n".join(context_parts) if context_parts else "No additional context available."
            
            # Generate response
            messages = [
                SystemMessage(content="""You are a helpful AI assistant that can answer questions based on meeting notes and web search results.

When responding:
1. Use the meeting notes and web search results to provide accurate, helpful answers
2. If you don't have relevant information, say so clearly
3. Cite sources when possible (e.g., "Based on your meeting notes..." or "According to recent information...")
4. Be concise but comprehensive
5. If the query is vague, ask for clarification

Format your response in markdown for better readability."""),
                HumanMessage(content=f"Query: {state['query']}\n\nContext:\n{full_context}")
            ]
            
            response = await self.llm.ainvoke(messages)
            
            return {
                **state,
                "response": response.content,
                "messages": messages + [response]
            }
        except Exception as e:
            logger.error(f"❌ Synthesis error: {e}")
            return {
                **state,
                "response": f"Sorry, I encountered an error while processing your request: {str(e)}",
                "error": f"Synthesis failed: {str(e)}"
            }
    
    async def _error_handler_node(self, state: AgentState) -> AgentState:
        """Handle errors gracefully"""
        error_msg = state.get("error", "Unknown error occurred")
        logger.error(f"❌ Error in agent system: {error_msg}")
        
        return {
            **state,
            "response": f"Sorry, there was an error processing your request: {error_msg}"
        }
    
    def _route_from_analysis(self, state: AgentState) -> str:
        """Route based on analysis results"""
        analysis = state.get("analysis")
        if not analysis:
            return "error"
        
        if analysis.needs_meeting_search and analysis.needs_web_search:
            return "both"
        elif analysis.needs_meeting_search:
            return "meeting_agent"
        elif analysis.needs_web_search:
            return "web_agent"
        else:
            return "synthesize"
    
    def _route_from_meeting(self, state: AgentState) -> str:
        """Route from meeting agent based on analysis"""
        analysis = state.get("analysis")
        if not analysis:
            return "synthesize"
        
        if analysis.needs_web_search:
            return "web_agent"
        else:
            return "synthesize"
    
    async def _analyze_query(self, query: str, context: str = "") -> AgentAnalysis:
        """Analyze the query to determine which agents to run"""
        try:
            analysis_prompt = f"""Analyze this query and determine what type of search is needed:

Query: "{query}"
Context: "{context}"

Determine if this query needs:
1. Meeting notes search (for information from past meetings, notes, documents)
2. Web search (for current information, news, general knowledge)
3. Both
4. Neither (general conversation)

Respond with JSON in this format:
{{
    "needs_meeting_search": true/false,
    "needs_web_search": true/false,
    "search_strategy": "brief explanation",
    "priority": "meeting_search" or "web_search"
}}"""

            messages = [
                SystemMessage(content="You are an expert at analyzing queries to determine the best search strategy. Always respond with valid JSON."),
                HumanMessage(content=analysis_prompt)
            ]
            
            response = await self.llm.ainvoke(messages)
            
            # Parse JSON response
            analysis_data = json.loads(response.content)
            
            return AgentAnalysis(
                needs_meeting_search=analysis_data.get("needs_meeting_search", False),
                needs_web_search=analysis_data.get("needs_web_search", False),
                search_strategy=analysis_data.get("search_strategy", ""),
                priority=analysis_data.get("priority", "meeting_search")
            )
        except Exception as e:
            logger.error(f"❌ Query analysis error: {e}")
            # Default to both searches if analysis fails
            return AgentAnalysis(
                needs_meeting_search=True,
                needs_web_search=True,
                search_strategy="Default to both searches due to analysis error",
                priority="meeting_search"
            )
    
    def _process_meeting_notes_search_results(self, search_results: Dict[str, Any]) -> List[SearchResult]:
        """Process search results from the vector database"""
        processed_results = []
        for doc in search_results["documents"]:
            processed_results.append(SearchResult(
                content=doc["content"],
                metadata=doc["metadata"],
                relevance=doc["score"],
                source="meeting_notes"
            ))
        return processed_results
    
    def _format_meeting_results(self, results: List[SearchResult]) -> str:
        """Format meeting results for synthesis"""
        if not results:
            return "No relevant meeting notes found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.content[:200]}...")
            if result.metadata:
                formatted.append(f"   Source: {result.metadata.get('source', 'Unknown')}")
        
        return "\n".join(formatted)
    
    def _format_web_results(self, results: List[WebSearchResult]) -> str:
        """Format web results for synthesis"""
        if not results:
            return "No web search results found."
        
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result.title}")
            formatted.append(f"   {result.snippet}")
            formatted.append(f"   URL: {result.url}")
        
        return "\n".join(formatted)
    
    async def process_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """Process query through the LangGraph agent system"""
        try:
            logger.info("🚀 Processing query through LangGraph agent system...")
            
            # Initialize vector DB if needed
            await self.vector_db.initialize()
            
            # Create initial state
            initial_state = AgentState(
                query=query,
                context=context,
                analysis=None,
                meeting_results=[],
                web_results=[],
                response="",
                error=None,
                messages=[]
            )
            
            # Run the graph
            result = await self.graph.ainvoke(initial_state)
            
            # Extract results
            meeting_count = len(result.get("meeting_results", []))
            web_count = len(result.get("web_results", []))
            
            return {
                "success": True,
                "response": result.get("response", "No response generated"),
                "meeting_results": result.get("meeting_results", []),
                "web_results": result.get("web_results", []),
                "sources": {
                    "meeting_notes": meeting_count,
                    "web_results": web_count
                },
                "analysis": result.get("analysis")
            }
            
        except Exception as e:
            logger.error(f"❌ LangGraph agent system error: {e}")
            return {
                "success": False,
                "response": f"Sorry, there was an error processing your request: {str(e)}",
                "error": str(e),
                "meeting_results": [],
                "web_results": [],
                "sources": {"meeting_notes": 0, "web_results": 0}
            }
