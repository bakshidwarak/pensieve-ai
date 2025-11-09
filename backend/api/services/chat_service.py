"""Chat service for conversational AI."""

from typing import List, Dict, Any
from app.graphs.simple_agent import graph as simple_agent_graph
from app.models import get_chat_model


class ChatService:
    """Service for handling chat interactions."""

    def __init__(self):
        """Initialize chat service."""
        self.agent_graph = simple_agent_graph
        self.chat_model = get_chat_model()

    async def process_chat(
        self,
        messages: List[Dict[str, str]],
        use_rag: bool = False,
    ) -> Dict[str, Any]:
        """
        Process chat messages and return response.

        Args:
            messages: List of message dicts with 'role' and 'content'
            use_rag: Whether to use RAG-enhanced responses

        Returns:
            Dict with response message and optional tool calls
        """
        try:
            # Convert messages to LangChain format
            from langchain_core.messages import HumanMessage, AIMessage, SystemMessage

            lc_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")

                if role == "system":
                    lc_messages.append(SystemMessage(content=content))
                elif role == "assistant":
                    lc_messages.append(AIMessage(content=content))
                else:
                    lc_messages.append(HumanMessage(content=content))

            # Use agent graph if tools might be needed, else direct model call
            if use_rag or any(
                keyword in messages[-1].get("content", "").lower()
                for keyword in ["search", "find", "lookup", "research"]
            ):
                # Use agent with tools
                result = self.agent_graph.invoke({"messages": lc_messages})
                last_message = result["messages"][-1]

                return {
                    "message": {
                        "role": "assistant",
                        "content": last_message.content,
                    },
                    "tool_calls": getattr(last_message, "tool_calls", None),
                }
            else:
                # Direct model call for simple conversation
                response = self.chat_model.invoke(lc_messages)

                return {
                    "message": {
                        "role": "assistant",
                        "content": response.content,
                    },
                    "tool_calls": None,
                }

        except Exception as e:
            raise Exception(f"Chat processing failed: {str(e)}")
