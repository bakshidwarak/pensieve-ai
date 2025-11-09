"""Toolbelt assembly for agents.

Collects third-party tools and local tools (like RAG) into a single list that
graphs can bind to their language models.
"""
from __future__ import annotations

from typing import List

import os
# from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_community.tools.arxiv.tool import ArxivQueryRun
from app.rag import retrieve_information


def get_tool_belt() -> List:
    """Return the list of tools available to agents (Arxiv, RAG).

    Note: Tavily disabled for now - enable when you have TAVILY_API_KEY.
    """
    tools = [ArxivQueryRun(), retrieve_information]

    # Only add Tavily if API key is available
    # if os.getenv("TAVILY_API_KEY") and os.getenv("TAVILY_API_KEY") != "your_tavily_api_key_here":
    #     from langchain_community.tools.tavily_search import TavilySearchResults
    #     tools.insert(0, TavilySearchResults(max_results=5))

    return tools


