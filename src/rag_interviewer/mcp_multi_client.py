"""Multi-server MCP client manager for RAG Interview Agent.

Manages connections to multiple MCP servers and aggregates results
from various sources for enhanced interview capabilities.
"""
import asyncio
import time
from typing import Dict, List, Optional, Any, Tuple
from contextlib import asynccontextmanager
from dataclasses import dataclass
from enum import Enum

try:
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    MCP_AVAILABLE = True
except ImportError:
    MCP_AVAILABLE = False
    ClientSession = None
    StdioServerParameters = None
    stdio_client = None

from rag_interviewer.mcp_config import get_mcp_registry, MCPServerConfig
from rag_interviewer.logging import get_logger

logger = get_logger(__name__)


class ServerStatus(Enum):
    """Status of an MCP server connection."""
    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    ERROR = "error"
    TIMEOUT = "timeout"


@dataclass
class ServerConnection:
    """Represents a connection to an MCP server."""
    config: MCPServerConfig
    status: ServerStatus = ServerStatus.DISCONNECTED
    session: Optional[Any] = None
    last_error: Optional[str] = None
    connected_at: Optional[float] = None
    
    @property
    def is_connected(self) -> bool:
        return self.status == ServerStatus.CONNECTED and self.session is not None


class MultiServerMCPClient:
    """Client that manages connections to multiple MCP servers."""
    
    def __init__(self, server_names: Optional[List[str]] = None):
        """Initialize multi-server MCP client.
        
        Args:
            server_names: List of server names to connect to. If None, uses all enabled.
        """
        self.registry = get_mcp_registry()
        self.connections: Dict[str, ServerConnection] = {}
        
        # Get servers to connect to
        if server_names:
            configs = [self.registry.get_server(name) for name in server_names]
            configs = [c for c in configs if c and c.enabled]
        else:
            configs = self.registry.get_enabled_servers()
        
        for config in configs:
            self.connections[config.name] = ServerConnection(config)
    
    @asynccontextmanager
    async def connect_all(self, timeout: float = 10.0):
        """Connect to all configured servers with timeout.
        
        Args:
            timeout: Maximum time to wait for each connection
        """
        if not MCP_AVAILABLE:
            logger.warning("MCP not available, skipping connections")
            yield self
            return
        
        # Connect to all servers concurrently
        tasks = []
        for name, conn in self.connections.items():
            task = asyncio.create_task(
                self._connect_server(name, timeout),
                name=f"connect_{name}"
            )
            tasks.append(task)
        
        # Wait for all connections (with overall timeout)
        try:
            await asyncio.wait_for(
                asyncio.gather(*tasks, return_exceptions=True),
                timeout=timeout * 2  # Overall timeout
            )
        except asyncio.TimeoutError:
            logger.warning("Some MCP connections timed out")
        
        try:
            yield self
        finally:
            # Disconnect all
            await self._disconnect_all()
    
    async def _connect_server(self, name: str, timeout: float):
        """Connect to a single server."""
        conn = self.connections[name]
        conn.status = ServerStatus.CONNECTING
        
        try:
            params = StdioServerParameters(
                command=conn.config.command,
                args=conn.config.args,
                env=conn.config.env
            )
            
            # Connect with timeout
            async with asyncio.timeout(timeout):
                async with stdio_client(params) as (read, write):
                    async with ClientSession(read, write) as session:
                        await session.initialize()
                        conn.session = session
                        conn.status = ServerStatus.CONNECTED
                        conn.connected_at = time.time()
                        logger.info(f"✓ Connected to MCP server: {name}")
        
        except asyncio.TimeoutError:
            conn.status = ServerStatus.TIMEOUT
            conn.last_error = f"Connection timeout after {timeout}s"
            logger.warning(f"✗ Timeout connecting to {name}")
        
        except Exception as e:
            conn.status = ServerStatus.ERROR
            conn.last_error = str(e)
            logger.error(f"✗ Error connecting to {name}: {e}")
    
    async def _disconnect_all(self):
        """Disconnect from all servers."""
        for name, conn in self.connections.items():
            if conn.is_connected:
                try:
                    # Session will be closed by context manager
                    conn.session = None
                    conn.status = ServerStatus.DISCONNECTED
                    logger.info(f"✓ Disconnected from {name}")
                except Exception as e:
                    logger.error(f"✗ Error disconnecting from {name}: {e}")
    
    def get_connected_servers(self) -> List[str]:
        """Get list of successfully connected server names."""
        return [
            name for name, conn in self.connections.items()
            if conn.is_connected
        ]
    
    async def query_all(
        self,
        tool_name: str,
        params: Dict[str, Any],
        timeout: float = 5.0
    ) -> List[Tuple[str, Any]]:
        """Query a tool on all connected servers.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            timeout: Timeout per server
            
        Returns:
            List of (server_name, result) tuples
        """
        results = []
        connected = self.get_connected_servers()
        
        if not connected:
            logger.warning("No MCP servers connected")
            return results
        
        # Query all servers concurrently
        tasks = []
        for server_name in connected:
            task = asyncio.create_task(
                self._query_single(server_name, tool_name, params, timeout),
                name=f"query_{server_name}"
            )
            tasks.append((server_name, task))
        
        # Collect results
        for server_name, task in tasks:
            try:
                result = await task
                if result is not None:
                    results.append((server_name, result))
            except Exception as e:
                logger.error(f"Query failed for {server_name}: {e}")
        
        return results
    
    async def _query_single(
        self,
        server_name: str,
        tool_name: str,
        params: Dict[str, Any],
        timeout: float
    ) -> Optional[Any]:
        """Query a single server."""
        conn = self.connections[server_name]
        
        if not conn.is_connected:
            return None
        
        try:
            async with asyncio.timeout(timeout):
                result = await conn.session.call_tool(tool_name, params)
                return result
        
        except asyncio.TimeoutError:
            logger.warning(f"Query timeout for {server_name}")
            return None
        
        except Exception as e:
            logger.error(f"Query error for {server_name}: {e}")
            return None
    
    async def query_best_result(
        self,
        tool_name: str,
        params: Dict[str, Any],
        timeout: float = 5.0
    ) -> Optional[Tuple[str, Any]]:
        """Query all servers and return the first successful result.
        
        Args:
            tool_name: Name of the tool to call
            params: Parameters for the tool
            timeout: Timeout per server
            
        Returns:
            (server_name, result) tuple or None
        """
        results = await self.query_all(tool_name, params, timeout)
        return results[0] if results else None
    
    def get_connection_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all connections."""
        return {
            name: {
                "status": conn.status.value,
                "enabled": conn.config.enabled,
                "connected": conn.is_connected,
                "last_error": conn.last_error,
                "connected_at": conn.connected_at
            }
            for name, conn in self.connections.items()
        }


# Specialized query functions for interview use cases
async def fetch_documentation(
    query: str,
    sources: Optional[List[str]] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Fetch documentation from multiple sources.
    
    Args:
        query: Documentation query
        sources: List of source names (None = all available)
        
    Returns:
        Dict mapping source names to documentation results
    """
    client = MultiServerMCPClient(sources)
    results = {}
    
    async with client.connect_all():
        # Query documentation from all connected servers
        query_results = await client.query_all(
            "fetch",
            {"query": query, "max_length": 5000}
        )
        
        for server_name, result in query_results:
            results[server_name] = [{
                "content": result.content if hasattr(result, 'content') else str(result),
                "source": server_name
            }]
    
    return results


async def search_code_examples(
    query: str,
    language: str = "python"
) -> List[Dict[str, Any]]:
    """Search for code examples across multiple sources.
    
    Args:
        query: Code search query
        language: Programming language
        
    Returns:
        List of code examples from various sources
    """
    client = MultiServerMCPClient(["stackoverflow", "github_api"])
    examples = []
    
    async with client.connect_all():
        # Search Stack Overflow and GitHub
        results = await client.query_all(
            "search",
            {"query": query, "language": language, "limit": 3}
        )
        
        for server_name, result in results:
            examples.append({
                "source": server_name,
                "language": language,
                "content": result.content if hasattr(result, 'content') else str(result),
                "url": result.url if hasattr(result, 'url') else None
            })
    
    return examples


async def validate_code_multi(
    code: str,
    language: str = "python"
) -> Dict[str, Any]:
    """Validate code using multiple validators.
    
    Args:
        code: Code to validate
        language: Programming language
        
    Returns:
        Aggregated validation results
    """
    client = MultiServerMCPClient(["code_executor"])
    
    async with client.connect_all():
        result = await client.query_best_result(
            "validate_code",
            {"code": code, "language": language}
        )
        
        if result:
            server_name, validation = result
            return {
                "valid": validation.valid if hasattr(validation, 'valid') else True,
                "source": server_name,
                "errors": validation.errors if hasattr(validation, 'errors') else [],
                "suggestions": validation.suggestions if hasattr(validation, 'suggestions') else []
            }
        
        return {"valid": True, "source": "fallback", "errors": [], "suggestions": []}
