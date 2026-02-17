"""Multi-server MCP configuration for RAG Interview Agent.

This module manages connections to multiple MCP servers for enhanced
interview capabilities with real-time data from various sources.
"""
import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class MCPServerConfig:
    """Configuration for a single MCP server."""
    name: str
    command: str
    args: List[str] = field(default_factory=list)
    env: Optional[Dict[str, str]] = None
    enabled: bool = True
    timeout: int = 30
    description: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP client."""
        return {
            "name": self.name,
            "command": self.command,
            "args": self.args,
            "env": self.env,
        }


# Pre-configured MCP servers
DEFAULT_MCP_SERVERS = {
    "python_docs": MCPServerConfig(
        name="python_docs",
        command="python",
        args=["-m", "mcp_server_fetch"],
        description="Fetch Python documentation from docs.python.org",
        enabled=True
    ),
    
    "github_api": MCPServerConfig(
        name="github_api",
        command="python",
        args=["-m", "mcp_server_github"],
        description="Access GitHub repositories, issues, and trending repos",
        enabled=False  # Requires GITHUB_TOKEN
    ),
    
    "stackoverflow": MCPServerConfig(
        name="stackoverflow",
        command="python",
        args=["-m", "mcp_server_fetch"],
        description="Search Stack Overflow for code examples and solutions",
        enabled=True
    ),
    
    "internal_kb": MCPServerConfig(
        name="internal_kb",
        command="python",
        args=["-m", "mcp_server_filesystem"],
        description="Access internal knowledge base and company documentation",
        enabled=False  # Requires path configuration
    ),
    
    "code_executor": MCPServerConfig(
        name="code_executor",
        command="python",
        args=["-m", "mcp_server_code_executor"],
        description="Execute and validate code in sandboxed environment",
        enabled=False  # Requires secure sandbox setup
    ),
}


class MCPServerRegistry:
    """Registry for managing multiple MCP servers."""
    
    def __init__(self):
        self.servers: Dict[str, MCPServerConfig] = {}
        self._load_default_servers()
        self._load_env_config()
    
    def _load_default_servers(self):
        """Load default server configurations."""
        for name, config in DEFAULT_MCP_SERVERS.items():
            self.servers[name] = config
    
    def _load_env_config(self):
        """Load server configurations from environment variables."""
        # Enable/disable servers via env vars
        for name in self.servers.keys():
            env_key = f"MCP_SERVER_{name.upper()}_ENABLED"
            if env_key in os.environ:
                self.servers[name].enabled = os.environ[env_key].lower() == "true"
        
        # GitHub token for GitHub API server
        if os.environ.get("GITHUB_TOKEN"):
            self.servers["github_api"].enabled = True
            if not self.servers["github_api"].env:
                self.servers["github_api"].env = {}
            self.servers["github_api"].env["GITHUB_TOKEN"] = os.environ["GITHUB_TOKEN"]
    
    def get_enabled_servers(self) -> List[MCPServerConfig]:
        """Get list of enabled server configurations."""
        return [config for config in self.servers.values() if config.enabled]
    
    def get_server(self, name: str) -> Optional[MCPServerConfig]:
        """Get specific server configuration."""
        return self.servers.get(name)
    
    def enable_server(self, name: str) -> bool:
        """Enable a specific server."""
        if name in self.servers:
            self.servers[name].enabled = True
            return True
        return False
    
    def disable_server(self, name: str) -> bool:
        """Disable a specific server."""
        if name in self.servers:
            self.servers[name].enabled = False
            return True
        return False
    
    def add_custom_server(self, config: MCPServerConfig) -> bool:
        """Add a custom MCP server configuration."""
        self.servers[config.name] = config
        return True
    
    def get_server_status(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all servers."""
        return {
            name: {
                "enabled": config.enabled,
                "description": config.description,
                "command": f"{config.command} {' '.join(config.args)}"
            }
            for name, config in self.servers.items()
        }


# Global registry instance
_mcp_registry: Optional[MCPServerRegistry] = None


def get_mcp_registry() -> MCPServerRegistry:
    """Get or create global MCP server registry."""
    global _mcp_registry
    if _mcp_registry is None:
        _mcp_registry = MCPServerRegistry()
    return _mcp_registry
