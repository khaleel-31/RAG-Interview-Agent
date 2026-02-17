"""Demo script for multi-server MCP functionality.

Run this to test the advanced MCP features:
    python examples/mcp_multi_demo.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import asyncio


def demo_server_registry():
    """Demo 1: Show MCP server registry."""
    print("\n" + "="*60)
    print("DEMO 1: MCP Server Registry")
    print("="*60)
    
    from rag_interviewer.mcp_config import get_mcp_registry
    
    registry = get_mcp_registry()
    status = registry.get_server_status()
    
    print("\nAvailable MCP Servers:")
    for name, info in status.items():
        enabled = "✓" if info["enabled"] else "✗"
        print(f"  {enabled} {name:15} - {info['description']}")
    
    enabled_servers = registry.get_enabled_servers()
    print(f"\nEnabled Servers: {len(enabled_servers)}")


def demo_multi_server_client():
    """Demo 2: Multi-server client connections."""
    print("\n" + "="*60)
    print("DEMO 2: Multi-Server MCP Client")
    print("="*60)
    
    from rag_interviewer.mcp_multi_client import MultiServerMCPClient
    
    async def test_multi():
        print("\nConnecting to multiple MCP servers...")
        client = MultiServerMCPClient()
        
        async with client.connect_all(timeout=5.0):
            connected = client.get_connected_servers()
            print(f"✓ Connected to: {connected}")
            
            if connected:
                print("\nQuerying all connected servers...")
                results = await client.query_all(
                    "get_info",
                    {},
                    timeout=3.0
                )
                
                for server_name, result in results:
                    print(f"  • {server_name}: {result}")
    
    try:
        asyncio.run(test_multi())
    except Exception as e:
        print(f"! Multi-server test: {e}")
        print("  (This is expected if MCP servers are not running)")


def demo_documentation_fetch():
    """Demo 3: Fetch documentation from multiple sources."""
    print("\n" + "="*60)
    print("DEMO 3: Multi-Source Documentation Fetch")
    print("="*60)
    
    from rag_interviewer.mcp_multi_client import fetch_documentation
    
    async def test_docs():
        print("\nFetching 'python async/await' documentation...")
        docs = await fetch_documentation(
            "python async await best practices",
            sources=["python_docs", "stackoverflow"]
        )
        
        for source, content in docs.items():
            print(f"\n  Source: {source}")
            if content:
                preview = content[0]["content"][:200]
                print(f"    Preview: {preview}...")
            else:
                print("    No content retrieved")
    
    try:
        asyncio.run(test_docs())
    except Exception as e:
        print(f"! Documentation fetch: {e}")


def demo_code_examples():
    """Demo 4: Search code examples across sources."""
    print("\n" + "="*60)
    print("DEMO 4: Multi-Source Code Examples")
    print("="*60)
    
    from rag_interviewer.mcp_multi_client import search_code_examples
    
    async def test_code():
        print("\nSearching for 'FastAPI authentication' examples...")
        examples = await search_code_examples(
            "fastapi authentication",
            language="python"
        )
        
        print(f"\n  Found {len(examples)} examples:")
        for i, ex in enumerate(examples[:3], 1):
            print(f"\n  Example {i} from {ex['source']}:")
            code_preview = ex['content'][:150]
            print(f"    {code_preview}...")
    
    try:
        asyncio.run(test_code())
    except Exception as e:
        print(f"! Code search: {e}")


def demo_advanced_researcher():
    """Demo 5: Advanced researcher with multi-MCP."""
    print("\n" + "="*60)
    print("DEMO 5: Advanced Multi-MCP Researcher Node")
    print("="*60)
    
    from rag_interviewer.nodes.researcher_multi_mcp import (
        researcher_node_multi_mcp,
        extract_tech_keywords
    )
    
    # Test keyword extraction
    jd = """
    Senior Python Developer with FastAPI, Kubernetes, and PostgreSQL experience.
    Must have knowledge of Docker, CI/CD, and machine learning.
    """
    
    print("\nExtracting keywords from job description...")
    keywords = extract_tech_keywords(jd)
    print(f"  Found: {', '.join(keywords)}")
    
    # Test researcher node
    print("\nRunning advanced researcher node...")
    state = {
        "job_description": jd,
        "messages": [],
        "level": "intermediate"
    }
    
    result = researcher_node_multi_mcp(state)
    context = result['tech_context']
    
    print(f"\n  Generated context: {len(context)} characters")
    
    if context != "FALLBACK_TO_GENERAL":
        print("  ✓ Combined local + MCP context generated!")
        
        # Show context sections
        if "Internal Knowledge Base" in context:
            print("    • Local ChromaDB included")
        if "Documentation from MCP Sources" in context:
            print("    • MCP documentation included")
        if "Code Examples from MCP Sources" in context:
            print("    • MCP code examples included")
    else:
        print("  ⚠ Using fallback (no context available)")


def demo_configuration():
    """Demo 6: Server configuration."""
    print("\n" + "="*60)
    print("DEMO 6: Server Configuration")
    print("="*60)
    
    from rag_interviewer.mcp_config import get_mcp_registry
    
    registry = get_mcp_registry()
    
    print("\nCurrent Configuration:")
    print(f"  Servers: {len(registry.servers)}")
    
    print("\nEnabling Python Docs server...")
    registry.enable_server("python_docs")
    
    print("Disabling GitHub API server...")
    registry.disable_server("github_api")
    
    enabled = registry.get_enabled_servers()
    print(f"\nNow {len(enabled)} servers enabled")


def main():
    """Run all demos."""
    print("\n" + "="*70)
    print("  ADVANCED MULTI-SERVER MCP DEMO")
    print("  Model Context Protocol - Multiple Server Configuration")
    print("="*70)
    
    demos = [
        ("Server Registry", demo_server_registry),
        ("Multi-Server Client", demo_multi_server_client),
        ("Documentation Fetch", demo_documentation_fetch),
        ("Code Examples", demo_code_examples),
        ("Advanced Researcher", demo_advanced_researcher),
        ("Configuration", demo_configuration),
    ]
    
    for name, demo_func in demos:
        try:
            demo_func()
        except Exception as e:
            print(f"\n! Demo '{name}' failed: {e}")
    
    print("\n" + "="*70)
    print("  All demos completed!")
    print("\n  Next steps:")
    print("    1. Enable servers: Set env vars or use UI")
    print("    2. Run app: streamlit run main.py")
    print("    3. Configure MCP: Use the MCP Config page")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
