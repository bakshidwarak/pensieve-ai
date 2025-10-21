import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional, TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage

from services.vector_db import VectorDBService
from services.web_search import WebSearchService
from models.schemas import AgentAnalysis, SearchResult, WebSearchResult

logger = logging.getLogger(__name__)

class AgentState(TypedDict):
    """State schema for the graph-based agent system"""
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
    messages: List[BaseMessage]

class GraphAgentSystem:
    
    def __init__(self, retriever=None):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4",
            temperature=0.7
        )
        
        # Allow custom retriever or use default
        self.retriever = retriever or VectorDBService()
        self.web_search = WebSearchService()
    
    def set_retriever(self, retriever):
        """Change the retriever at runtime"""
        self.retriever = retriever
        logger.info(f"✅ Retriever changed to: {type(retriever).__name__}")
    
    def get_retriever(self):
        """Get the current retriever"""
        return self.retriever
    
    async def process_query(self, query: str, context: str = "") -> Dict[str, Any]:
       
        try:
            logger.info("🚀 Processing query ...")
            
            # Initialize retriever if needed
            await self.retriever.initialize()
            
            # Create initial state
            state = AgentState(
                query=query,
                context=context,
                analysis=None,
                meeting_results=[],
                web_results=[],
                response="",
                error=None,
                messages=[]
            )
            
            # Execute the graph workflow
            final_state = await self._execute_graph(state)
            
            # Extract results
            meeting_count = len(final_state.get("meeting_results", []))
            web_count = len(final_state.get("web_results", []))
            
            return {
                "success": True,
                "response": final_state.get("response", "No response generated"),
                "meeting_results": final_state.get("meeting_results", []),
                "web_results": final_state.get("web_results", []),
                "sources": {
                    "meeting_notes": meeting_count,
                    "web_results": web_count
                },
                "analysis": final_state.get("analysis").dict() if final_state.get("analysis") else None
            }
            
        except Exception as e:
            logger.error(f"❌ Graph agent system error: {e}")
            return {
                "success": False,
                "response": f"Sorry, there was an error processing your request: {str(e)}",
                "error": str(e),
                "meeting_results": [],
                "web_results": [],
                "sources": {"meeting_notes": 0, "web_results": 0}
            }
    
    async def _execute_graph(self, state: AgentState) -> AgentState:
        """Execute the graph workflow"""
        try:
            # Step 1: Analyze query
            logger.info("🔍 Step 1: Analyzing query...")
            state = await self._analyze_node(state)
            
            if state.get("error"):
                return await self._error_handler_node(state)
            
            # Step 2: Execute agents based on analysis
            analysis = state.get("analysis")
            if not analysis:
                return await self._error_handler_node(state)
            
            # Run meeting agent if needed
            if analysis.needs_meeting_search:
                logger.info("📝 Step 2a: Running meeting agent...")
                state = await self._meeting_agent_node(state)
            
            # Run web agent if needed
            if analysis.needs_web_search:
                logger.info("🌐 Step 2b: Running web agent...")
                state = await self._web_agent_node(state)
            
            # Step 3: Synthesize results
            logger.info("🧠 Step 3: Synthesizing results...")
            state = await self._synthesize_node(state)
            
            return state
            
        except Exception as e:
            logger.error(f"❌ Graph execution error: {e}")
            state["error"] = f"Graph execution failed: {str(e)}"
            return await self._error_handler_node(state)
    
    async def _analyze_node(self, state: AgentState) -> AgentState:
        """Analyze the query to determine which agents to run"""
        try:
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
            # Search using the configured retriever
            search_results = await self.retriever.search_documents(
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
            # Perform web search
            web_results = await self.web_search.search_technical_content(state["query"], state["context"])
            
            if web_results["success"]:
                processed_results = []
                for result in web_results["results"]:
                    processed_results.append(WebSearchResult(
                        title=result.get("title", ""),
                        content=result.get("snippet", "") or result.get("detailed_content", ""),
                        url=result.get("url", ""),
                        source="web_search",
                        relevance=0.8
                    ))
                web_results = processed_results
            else:
                web_results = []
            
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
            formatted.append(f"   {result.content}")
            formatted.append(f"   URL: {result.url}")
        
        return "\n".join(formatted)
