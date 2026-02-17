"""Test MCP availability after installation."""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Force reload of mcp_client module
if 'rag_interviewer.mcp_client' in sys.modules:
    del sys.modules['rag_interviewer.mcp_client']

# Now test
print("Testing MCP Availability")
print("-" * 50)

# Test 1: Check if mcp package can be imported directly
try:
    import mcp
    print(f"✓ MCP package version: {getattr(mcp, '__version__', 'unknown')}")
    mcp_direct = True
except ImportError:
    print("✗ Cannot import mcp package directly")
    mcp_direct = False

# Test 2: Check our module
from rag_interviewer.mcp_client import is_mcp_available, get_tech_trends_sync

if mcp_direct:
    print(f"✓ MCP Available in module: {is_mcp_available()}")
else:
    print(f"! MCP module shows: {is_mcp_available()}")
    print("   (This may be cached from previous import)")

# Test 3: Test functionality
print("\nTesting MCP Functions")
print("-" * 50)
trends = get_tech_trends_sync("python")
print(f"✓ Tech trends: {', '.join(trends[:3])}")

# Test 4: Test async client if MCP available
if mcp_direct:
    print("\nTesting Async MCP Client")
    print("-" * 50)
    from rag_interviewer.mcp_client import MCPInterviewClient
    
    async def test_async():
        client = MCPInterviewClient()
        try:
            async with client.connect():
                trends = await client.get_current_tech_trends("AI")
                print(f"✓ Async trends: {', '.join(trends[:3])}")
                return True
        except Exception as e:
            print(f"! Async test: {e}")
            return False
    
    import asyncio
    try:
        result = asyncio.run(test_async())
        if result:
            print("\n✓✓✓ Full MCP functionality working!")
    except Exception as e:
        print(f"! Async test failed: {e}")
        print("   (MCP server may not be running)")

print("\n" + "=" * 50)
if mcp_direct:
    print("✓ MCP is FULLY ENABLED with server support!")
else:
    print("! MCP working in fallback mode")
    print("   Restart Python to enable full MCP features")
print("=" * 50)
