import os
import json
import logging
import asyncio
from typing import List, Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

from services.vector_db import VectorDBService
from services.web_search import WebSearchService
from models.schemas import AgentAnalysis, SearchResult, WebSearchResult

logger = logging.getLogger(__name__)

class AgentSystem:
    def __init__(self):
        self.llm = ChatOpenAI(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model_name="gpt-4",
            temperature=0.7
        )
        
        self.vector_db = VectorDBService()
        self.web_search = WebSearchService()
    
    async def process_query(self, query: str, context: str = "") -> Dict[str, Any]:
        """Process query through the agent system"""
        try:
            logger.info("🚀 Processing query through agent system...")
            
            # Initialize vector DB if needed
            await self.vector_db.initialize()
            
            # Step 1: Supervisor analysis
            analysis = await self.analyze_query(query, context)
            
            # Step 2: Run agents in parallel based on analysis
            tasks = []
            
            if analysis.needs_meeting_search:
                tasks.append(self.meeting_agent(query))
            else:
                async def empty_meeting():
                    return []
                tasks.append(empty_meeting())
            
            if analysis.needs_web_search:
                tasks.append(self.web_agent(query, context))
            else:
                async def empty_web():
                    return []
                tasks.append(empty_web())
            
            meeting_results, web_results = await asyncio.gather(*tasks)
            
            # Step 3: Synthesis
            final_response = await self.synthesis_agent(query, meeting_results, web_results)
            
            return {
                "success": True,
                "response": final_response,
                "meeting_results": meeting_results,
                "web_results": web_results,
                "analysis": analysis.dict()
            }
            
        except Exception as e:
            logger.error(f"❌ Agent system error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "I apologize, but I encountered an error while processing your request."
            }
    
    async def analyze_query(self, query: str, context: str) -> AgentAnalysis:
        """Analyze query to determine search strategy"""
        try:
            logger.info("🤖 Supervisor Agent analyzing query...")
            
            system_prompt = f"""You are a supervisor agent that analyzes user queries and determines the best approach for answering them.

Your job is to:
1. Understand the user's query and context
2. Determine if the query is about meeting notes, technical topics, or both
3. Route the query to appropriate agents

Query: {query}
Context: {context or 'No additional context'}

Respond with a JSON object containing:
- needs_meeting_search: boolean (whether to search meeting notes)
- needs_web_search: boolean (whether to search the web)
- search_strategy: string (brief description of search approach)
- priority: string (which search to prioritize)"""

            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ])
            
            analysis_data = json.loads(response.content)
            return AgentAnalysis(**analysis_data)
            
        except Exception as e:
            logger.error(f"❌ Supervisor agent error: {e}")
            return AgentAnalysis(
                needs_meeting_search=True,
                needs_web_search=True,
                search_strategy="comprehensive",
                priority="meeting"
            )
    
    async def meeting_agent(self, query: str) -> List[SearchResult]:
        """Search meeting notes using vector database"""
        try:
            logger.info("📝 Meeting Agent searching notes...")
            
            # Search vector database for relevant meeting notes
            search_results = await self.vector_db.search_documents(
                query=query,
                limit=5,
                filter_metadata={"type": {"$in": ["meeting", "note", "general"]}}
            )
            
            if not search_results["success"]:
                return []
            
            # Process and rank results
            processed_results = []
            for doc in search_results["documents"]:
                processed_results.append(SearchResult(
                    content=doc["content"],
                    metadata=doc["metadata"],
                    relevance=doc["score"],  # Use score directly
                    source="meeting_notes"
                ))
            
            return processed_results
            
        except Exception as e:
            logger.error(f"❌ Meeting agent error: {e}")
            return []
    
    async def web_agent(self, query: str, context: str) -> List[WebSearchResult]:
        """Search web for technical information"""
        try:
            logger.info("🌐 Web Agent searching online...")
            
            # Search web for technical information
            web_results = await self.web_search.search_technical_content(query, context)
            
            if not web_results["success"]:
                return []
            
            # Process web results
            processed_results = []
            for result in web_results["results"]:
                processed_results.append(WebSearchResult(
                    title=result["title"],
                    content=result.get("snippet", "") or result.get("detailed_content", ""),
                    url=result["url"],
                    source="web_search",
                    relevance=0.8  # Default relevance for web results
                ))
            
            return processed_results
            
        except Exception as e:
            logger.error(f"❌ Web agent error: {e}")
            return []
    
    async def synthesis_agent(
        self, 
        query: str, 
        meeting_results: List[SearchResult], 
        web_results: List[WebSearchResult]
    ) -> str:
        """Synthesize information from all sources"""
        try:
            logger.info("🧠 Synthesis Agent creating response...")
            
            meeting_context = "\n".join([
                f"{i+1}. {result.content}" 
                for i, result in enumerate(meeting_results)
            ])
            
            web_context = "\n".join([
                f"{i+1}. {result.title}: {result.content}" 
                for i, result in enumerate(web_results)
            ])
            
            system_prompt = f"""You are a synthesis agent that combines information from meeting notes and web search to provide comprehensive answers.

Meeting Notes Context:
{meeting_context}

Web Search Context:
{web_context}

User Query: {query}

Create a comprehensive response that:
1. Directly answers the user's question
2. Combines relevant information from both sources
3. Provides actionable insights
4. Cites sources when appropriate
5. Maintains a professional, helpful tone

Format your response as a clear, well-structured answer."""

            response = await self.llm.ainvoke([
                SystemMessage(content=system_prompt),
                HumanMessage(content=query)
            ])
            
            return response.content
            
        except Exception as e:
            logger.error(f"❌ Synthesis agent error: {e}")
            return f"I apologize, but I encountered an error while processing your request: {e}"
