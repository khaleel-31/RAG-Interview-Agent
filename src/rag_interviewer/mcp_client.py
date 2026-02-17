"""MCP (Model Context Protocol) integration for RAG Interview Agent.

This module provides MCP client and server functionality to enhance
the interview system with external tools and real-time context.
"""
import json
import asyncio
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


class MCPInterviewClient:
    """MCP client for interview enhancement tools."""
    
    def __init__(self, server_params: Optional[StdioServerParameters] = None):
        self.server_params = server_params or self._default_server_params()
        self.session: Optional[ClientSession] = None
        self._client = None
    
    def _default_server_params(self) -> StdioServerParameters:
        """Default MCP server configuration."""
        return StdioServerParameters(
            command="python",
            args=["-m", "mcp_server_fetch"],
            env=None
        )
    
    @asynccontextmanager
    async def connect(self):
        """Async context manager for MCP connection."""
        async with stdio_client(self.server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                await session.initialize()
                yield self
    
    async def search_tech_docs(self, query: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Search technical documentation using MCP.
        
        Args:
            query: Search query for tech documentation
            limit: Maximum number of results
            
        Returns:
            List of documentation snippets
        """
        if not self.session:
            raise RuntimeError("MCP client not connected. Use 'async with client.connect()'")
        
        try:
            result = await self.session.call_tool(
                "fetch",
                {
                    "url": f"https://docs.python.org/3/search.html?q={query}",
                    "max_length": 5000
                }
            )
            return [{"content": result.content, "source": "python-docs"}]
        except Exception as e:
            return [{"content": f"Error fetching docs: {e}", "source": "error"}]
    
    async def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Execute code safely using MCP.
        
        Args:
            code: Code to execute
            language: Programming language
            
        Returns:
            Execution results
        """
        # This is a placeholder - in production, use a sandboxed environment
        return {
            "output": "Code execution not implemented in basic MCP setup",
            "success": False,
            "language": language
        }
    
    async def get_current_tech_trends(self, topic: str) -> List[str]:
        """Fetch current technology trends for a topic.
        
        Args:
            topic: Technology topic (e.g., 'AI', 'cloud', 'kubernetes')
            
        Returns:
            List of current trends
        """
        if not self.session:
            return ["MCP not connected"]
        
        # Placeholder for tech trends
        trends = {
            "AI": ["LLMs", "RAG", "Agent frameworks", "MCP"],
            "cloud": ["Kubernetes", "Serverless", "Multi-cloud"],
            "python": ["Async/await", "Type hints", "Pattern matching"]
        }
        return trends.get(topic.lower(), ["General best practices"])


# Synchronous wrapper for use in non-async contexts
def search_documentation_sync(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """Synchronous wrapper for MCP documentation search.
    
    Args:
        query: Search query
        limit: Maximum results
        
    Returns:
        List of documentation results
    """
    client = MCPInterviewClient()
    
    async def _search():
        async with client.connect():
            return await client.search_tech_docs(query, limit)
    
    try:
        return asyncio.run(_search())
    except Exception as e:
        # Fallback if MCP is not available
        return [{"content": f"Documentation search unavailable: {e}", "source": "fallback"}]


def get_tech_trends_sync(topic: str) -> List[str]:
    """Synchronous wrapper for getting tech trends.
    
    Args:
        topic: Technology topic
        
    Returns:
        List of trends
    """
    client = MCPInterviewClient()
    
    async def _get_trends():
        async with client.connect():
            return await client.get_current_tech_trends(topic)
    
    try:
        return asyncio.run(_get_trends())
    except Exception:
        # Return default trends if MCP fails
        return [f"Current trends in {topic}", "Best practices", "Industry standards"]
