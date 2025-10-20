import aiohttp
import asyncio
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
import logging
import os

logger = logging.getLogger(__name__)

class WebSearchService:
    def __init__(self):
        self.serp_api_key = os.getenv("SERP_API_KEY")
        self.search_engines = ["google", "bing", "duckduckgo"]
    
    async def search_web(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search the web for information"""
        try:
            if not self.serp_api_key:
                logger.warning("⚠️ SERP_API_KEY not configured, using mock search results")
                return await self.get_mock_search_results(query, num_results)
            
            # Use SERP API for web search
            async with aiohttp.ClientSession() as session:
                url = "https://serpapi.com/search"
                params = {
                    "api_key": self.serp_api_key,
                    "q": query,
                    "engine": "google",
                    "num": num_results
                }
                
                async with session.get(url, params=params) as response:
                    data = await response.json()
                    results = self.parse_search_results(data)
                    
                    return {
                        "success": True,
                        "results": results,
                        "query": query
                    }
                    
        except Exception as e:
            logger.error(f"❌ Web search error: {e}")
            # Fallback to mock results
            return await self.get_mock_search_results(query, num_results)
    
    def parse_search_results(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse search results from SERP API"""
        results = []
        
        if "organic_results" in data:
            for result in data["organic_results"]:
                results.append({
                    "title": result.get("title", ""),
                    "url": result.get("link", ""),
                    "snippet": result.get("snippet", ""),
                    "source": "web"
                })
        
        return results
    
    async def get_mock_search_results(self, query: str, num_results: int) -> Dict[str, Any]:
        """Mock search results for development"""
        mock_results = [
            {
                "title": f"Technical insights about {query}",
                "url": "https://example.com/technical-guide",
                "snippet": f"This is a comprehensive guide about {query} covering best practices and implementation details.",
                "source": "mock"
            },
            {
                "title": f"{query} - Industry Best Practices",
                "url": "https://example.com/best-practices",
                "snippet": f"Learn about industry best practices for {query} and how to implement them effectively.",
                "source": "mock"
            },
            {
                "title": f"Advanced {query} Techniques",
                "url": "https://example.com/advanced-techniques",
                "snippet": f"Explore advanced techniques and strategies for {query} in modern development.",
                "source": "mock"
            }
        ]
        
        return {
            "success": True,
            "results": mock_results[:num_results],
            "query": query,
            "source": "mock"
        }
    
    async def scrape_web_page(self, url: str) -> Dict[str, Any]:
        """Scrape content from a web page"""
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
                }
                
                async with session.get(url, headers=headers, timeout=10) as response:
                    if response.status == 200:
                        html = await response.text()
                        soup = BeautifulSoup(html, 'html.parser')
                        
                        # Remove script and style elements
                        for script in soup(["script", "style"]):
                            script.decompose()
                        
                        # Extract main content
                        title = soup.find('title')
                        title_text = title.get_text().strip() if title else ""
                        
                        # Get body text
                        body = soup.find('body')
                        if body:
                            content = body.get_text()
                            # Clean up whitespace
                            content = ' '.join(content.split())
                        else:
                            content = ""
                        
                        return {
                            "success": True,
                            "title": title_text,
                            "content": content[:5000],  # Limit content length
                            "url": url
                        }
                    else:
                        return {
                            "success": False,
                            "error": f"HTTP {response.status}"
                        }
                        
        except Exception as e:
            logger.error(f"❌ Error scraping web page: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def search_technical_content(self, query: str, context: str = "") -> Dict[str, Any]:
        """Search for technical content with enhanced query"""
        try:
            # Enhance query with technical context
            enhanced_query = self.enhance_query(query, context)
            
            # Search for technical content
            search_results = await self.search_web(enhanced_query, 3)
            
            if not search_results["success"]:
                return search_results
            
            # Scrape top results for detailed content
            detailed_results = []
            for result in search_results["results"][:2]:
                if result["url"] and result["url"].startswith("http"):
                    scraped = await self.scrape_web_page(result["url"])
                    if scraped["success"]:
                        detailed_results.append({
                            **result,
                            "detailed_content": scraped["content"],
                            "scraped_title": scraped["title"]
                        })
            
            return {
                "success": True,
                "results": detailed_results,
                "query": enhanced_query,
                "context": context
            }
            
        except Exception as e:
            logger.error(f"❌ Error searching technical content: {e}")
            raise e
    
    def enhance_query(self, query: str, context: str) -> str:
        """Enhance query with technical terms and context"""
        technical_terms = [
            "best practices", "implementation", "architecture", "design patterns",
            "performance", "scalability", "security", "testing", "deployment"
        ]
        
        enhanced_query = query
        
        # Add technical context if present
        if context and len(context) > 10:
            enhanced_query += f" {context}"
        
        # Add relevant technical terms
        relevant_terms = [
            term for term in technical_terms 
            if term in query.lower() or term in context.lower()
        ]
        
        if relevant_terms:
            enhanced_query += f" {' '.join(relevant_terms)}"
        
        return enhanced_query
