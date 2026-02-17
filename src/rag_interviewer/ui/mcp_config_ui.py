"""Streamlit UI component for managing MCP servers.

Provides a user interface to:
- View MCP server status
- Enable/disable servers
- Configure server parameters
- Test connections
"""
import streamlit as st
from typing import Dict, Any

def render_mcp_config_ui():
    """Render MCP server configuration UI in Streamlit."""
    st.header("🔌 MCP Server Configuration")
    st.markdown("""
    Configure Model Context Protocol (MCP) servers to enhance interviews 
    with real-time data from external sources.
    """)
    
    # Import here to avoid issues if MCP not available
    try:
        from rag_interviewer.mcp_config import get_mcp_registry
        registry = get_mcp_registry()
        status = registry.get_server_status()
    except Exception as e:
        st.error(f"Failed to load MCP configuration: {e}")
        return
    
    # Server status overview
    st.subheader("Server Status")
    
    col1, col2, col3 = st.columns(3)
    total = len(status)
    enabled = sum(1 for s in status.values() if s["enabled"])
    
    col1.metric("Total Servers", total)
    col2.metric("Enabled", enabled)
    col3.metric("Disabled", total - enabled)
    
    # Individual server controls
    st.subheader("Configure Servers")
    
    for name, info in status.items():
        with st.expander(f"{'✅' if info['enabled'] else '⏸️'} {name.title()}", expanded=False):
            st.markdown(f"**Description:** {info['description']}")
            st.code(info["command"], language="bash")
            
            col1, col2 = st.columns([1, 3])
            
            with col1:
                if info["enabled"]:
                    if st.button(f"Disable {name}", key=f"disable_{name}"):
                        registry.disable_server(name)
                        st.rerun()
                else:
                    if st.button(f"Enable {name}", key=f"enable_{name}"):
                        registry.enable_server(name)
                        st.rerun()
            
            with col2:
                if info["enabled"]:
                    st.success("Server enabled - will be used in interviews")
                else:
                    st.info("Server disabled - enable to use in interviews")
    
    # Environment variables info
    st.subheader("Environment Setup")
    st.info("""
    **Required Environment Variables:**
    
    - `HUGGINGFACEHUB_API_TOKEN` - For embeddings (required)
    - `GITHUB_TOKEN` - For GitHub API access (optional)
    - `MCP_SERVER_<NAME>_ENABLED` - Enable/disable specific servers
    
    Set these in your `.env` file or environment before starting the app.
    """)
    
    # Quick test
    st.subheader("Test MCP Connection")
    if st.button("Test All Enabled Servers"):
        with st.spinner("Testing MCP connections..."):
            try:
                from rag_interviewer.mcp_multi_client import MultiServerMCPClient
                import asyncio
                
                async def test_connections():
                    client = MultiServerMCPClient()
                    async with client.connect_all(timeout=5.0):
                        connected = client.get_connected_servers()
                        return connected, client.get_connection_status()
                
                connected, all_status = asyncio.run(test_connections())
                
                if connected:
                    st.success(f"✅ Connected to: {', '.join(connected)}")
                else:
                    st.warning("⚠️ No servers connected. Check configuration.")
                
                # Show detailed status
                with st.expander("Connection Details"):
                    for name, conn_status in all_status.items():
                        st.write(f"**{name}:** {conn_status['status']}")
                        if conn_status.get('last_error'):
                            st.error(f"  Error: {conn_status['last_error']}")
                        
            except Exception as e:
                st.error(f"Test failed: {e}")


def render_mcp_info_sidebar():
    """Render MCP info in sidebar."""
    try:
        from rag_interviewer.mcp_config import get_mcp_registry
        registry = get_mcp_registry()
        enabled = registry.get_enabled_servers()
        
        if enabled:
            st.sidebar.markdown("---")
            st.sidebar.subheader("🔌 MCP Servers")
            st.sidebar.caption(f"{len(enabled)} server(s) active")
            
            for server in enabled:
                st.sidebar.text(f"• {server.name}")
        
    except Exception:
        pass  # Silent fail if MCP not available
