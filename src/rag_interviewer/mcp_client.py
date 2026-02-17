"""MCP (Model Context Protocol) integration for RAG Interview Agent.

This module provides MCP client and server functionality to enhance
the interview system with external tools and real-time context.
"""
import json
import asyncio
from typing import Any, Dict, List, Optional
from contextlib import asynccontextmanager

# Try to import MCP, but provide fallbacks if not available
try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None


class MCPInterviewClient:
    """MCP client for interview enhancement tools."""
    
    def __init__(self, server_params: Optional[Any] = None):
        if not MCP_AVAILABLE:
            self._mcp_enabled = False
            return
            
        self.server_params = server_params or self._default_server_params()
        self.session: Optional[Any] = None
        self._client = None
        self._mcp_enabled = True
    
    def _default_server_params(self):
        """Default MCP server configuration."""
        if not MCP_AVAILABLE:
            return None
        return StdioServerParameters(
            command="python",
            args=["-m", "mcp_server_fetch"],
            env=None
        )
    
    @asynccontextmanager
    async def connect(self):
        """Async context manager for MCP connection."""
        if not MCP_AVAILABLE or not self._mcp_enabled:
            yield self
            return
            
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
        if not MCP_AVAILABLE or not self.session:
            return [{"content": f"MCP not available. Query: {query}", "source": "fallback"}]
        
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
        # Return static trends (works with or without MCP)
        trends = {
            "AI": ["LLMs", "RAG", "Agent frameworks", "MCP"],
            "cloud": ["Kubernetes", "Serverless", "Multi-cloud"],
            "python": ["Async/await", "Type hints", "Pattern matching"],
            "javascript": ["ES2024", "TypeScript", "React Server Components"],
            "devops": ["GitOps", "Platform Engineering", "SRE"],
        }
        return trends.get(topic.lower(), ["General best practices", "Industry standards"])


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


def is_mcp_available() -> bool:
    """Check if MCP is available and installed.
    
    Returns:
        True if MCP SDK is installed
    """
    return MCP_AVAILABLE
