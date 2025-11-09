"""AI service for RAG and agent operations."""

from typing import Dict, Any, List
from app.rag import retrieve_information, _get_rag_graph
from app.graphs.simple_agent import graph as simple_agent_graph
from app.graphs.agent_with_helpfulness import graph as helpfulness_agent_graph
from langchain_core.messages import HumanMessage


class AIService:
    """Service for AI operations including RAG and agents."""

    def __init__(self):
        """Initialize AI service."""
        self.rag_graph = _get_rag_graph()
        self.simple_agent = simple_agent_graph
        self.helpfulness_agent = helpfulness_agent_graph

    async def query_rag(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """
        Query the RAG system.

        Args:
            query: User query
            top_k: Number of documents to retrieve

        Returns:
            Dict with answer and source documents
        """
        try:
            # Use the RAG tool
            result = retrieve_information.invoke({"query": query})

            # For now, we'll return a simplified response
            # You can enhance this to include source documents
            return {
                "answer": result if isinstance(result, str) else str(result),
                "sources": [],  # TODO: Extract source documents from retriever
            }

        except Exception as e:
            raise Exception(f"RAG query failed: {str(e)}")

    async def run_agent(self, task: str, agent_type: str = "simple") -> Dict[str, Any]:
        """
        Run an AI agent.

        Args:
            task: Task description for the agent
            agent_type: Type of agent ('simple' or 'helpfulness')

        Returns:
            Dict with agent result, steps, and tool calls
        """
        try:
            # Select agent graph
            if agent_type == "helpfulness":
                graph = self.helpfulness_agent
            else:
                graph = self.simple_agent

            # Execute agent
            result = graph.invoke({"messages": [HumanMessage(content=task)]})

            # Extract information from result
            messages = result.get("messages", [])
            last_message = messages[-1] if messages else None

            # Build response
            return {
                "result": last_message.content if last_message else "No response",
                "steps": self._extract_steps(messages),
                "tool_calls": self._extract_tool_calls(messages),
            }

        except Exception as e:
            raise Exception(f"Agent execution failed: {str(e)}")

    def _extract_steps(self, messages: List) -> List[Dict[str, Any]]:
        """Extract execution steps from messages."""
        steps = []
        for i, msg in enumerate(messages):
            steps.append(
                {
                    "step": i + 1,
                    "type": msg.__class__.__name__,
                    "content": msg.content[:100] if msg.content else "",
                }
            )
        return steps

    def _extract_tool_calls(self, messages: List) -> List[Dict[str, Any]]:
        """Extract tool calls from messages."""
        tool_calls = []
        for msg in messages:
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                for tc in msg.tool_calls:
                    tool_calls.append(
                        {
                            "name": tc.get("name", ""),
                            "args": tc.get("args", {}),
                        }
                    )
        return tool_calls if tool_calls else None
