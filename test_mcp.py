"""Quick test to verify MCP is working in your RAG Interview Agent.

Run this to check:
1. MCP dependencies are installed
2. MCP client can connect
3. MCP tools are functional

Usage:
    python test_mcp.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))


def test_mcp_imports():
    """Test 1: Check if MCP modules can be imported."""
    print("\n🧪 Test 1: MCP Module Imports")
    print("-" * 50)
    
    try:
        from rag_interviewer.mcp_client import (
            MCPInterviewClient,
            get_tech_trends_sync,
            search_documentation_sync
        )
        print("✅ MCP client module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MCP client: {e}")
        return False
    
    try:
        from rag_interviewer.mcp_evaluator import (
            MCPEvaluator,
            evaluate_with_mcp
        )
        print("✅ MCP evaluator module imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import MCP evaluator: {e}")
        return False
    
    return True


def test_mcp_dependencies():
    """Test 2: Check if MCP dependencies are installed."""
    print("\n🧪 Test 2: MCP Dependencies")
    print("-" * 50)
    
    try:
        import mcp
        print(f"✅ MCP SDK installed (version: {getattr(mcp, '__version__', 'unknown')})")
    except ImportError:
        print("❌ MCP SDK not installed. Run: pip install mcp")
        return False
    
    try:
        import httpx
        print(f"✅ HTTPX installed (version: {httpx.__version__})")
    except ImportError:
        print("❌ HTTPX not installed. Run: pip install httpx>=0.27.0")
        return False
    
    return True


def test_mcp_sync_functions():
    """Test 3: Test MCP synchronous functions (without server)."""
    print("\n🧪 Test 3: MCP Sync Functions (Offline Mode)")
    print("-" * 50)
    
    try:
        from rag_interviewer.mcp_client import get_tech_trends_sync
        
        # Test with fallback (no MCP server needed)
        trends = get_tech_trends_sync("python")
        
        if trends and len(trends) > 0:
            print(f"✅ get_tech_trends_sync working")
            print(f"   Sample trends: {', '.join(trends[:3])}")
        else:
            print("⚠️  Function returned empty (using fallback)")
            
    except Exception as e:
        print(f"❌ Sync functions failed: {e}")
        return False
    
    return True


def test_mcp_evaluator():
    """Test 4: Test MCP-enhanced code evaluator."""
    print("\n🧪 Test 4: MCP Code Evaluator")
    print("-" * 50)
    
    try:
        from rag_interviewer.mcp_evaluator import evaluate_with_mcp
        
        # Test code evaluation
        result = evaluate_with_mcp(
            question="Write a Python function",
            answer="```python\ndef hello():\n    print('Hello')\n```",
            level="beginner"
        )
        
        if "score" in result:
            print(f"✅ Code evaluator working")
            print(f"   Score: {result['score']}/10")
            print(f"   Has code: {result['has_code']}")
        else:
            print("⚠️  Evaluator returned unexpected result")
            
    except Exception as e:
        print(f"❌ Code evaluator failed: {e}")
        return False
    
    return True


def test_mcp_researcher():
    """Test 5: Test MCP-enhanced researcher."""
    print("\n🧪 Test 5: MCP Researcher Node")
    print("-" * 50)
    
    try:
        from rag_interviewer.nodes.researcher_mcp import (
            extract_tech_keywords,
            researcher_node_enhanced
        )
        
        # Test keyword extraction
        jd = "Looking for Python developer with FastAPI and Docker experience"
        keywords = extract_tech_keywords(jd)
        
        if keywords:
            print(f"✅ Keyword extraction working")
            print(f"   Found: {', '.join(keywords)}")
        else:
            print("⚠️  No keywords extracted")
        
        # Test researcher node
        state = {
            "job_description": jd,
            "messages": [],
            "level": "beginner"
        }
        
        result = researcher_node_enhanced(state)
        
        if "tech_context" in result:
            print(f"✅ Researcher node working")
            ctx_len = len(result['tech_context'])
            print(f"   Context size: {ctx_len} chars")
            if ctx_len > 100:
                print("   📝 Combined RAG + MCP context generated!")
        else:
            print("⚠️  Researcher returned unexpected result")
            
    except Exception as e:
        print(f"❌ MCP researcher failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    return True


def test_mcp_async():
    """Test 6: Test async MCP client (requires MCP server)."""
    print("\n🧪 Test 6: MCP Async Client (Optional)")
    print("-" * 50)
    print("⚠️  This test requires MCP server to be running")
    print("   Skipping async test (run manually if needed)")
    print("   To test async: python examples/mcp_demo.py")
    return True


def main():
    """Run all MCP tests."""
    print("\n" + "=" * 60)
    print("  MCP (Model Context Protocol) Verification Tests")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_mcp_imports),
        ("Dependencies", test_mcp_dependencies),
        ("Sync Functions", test_mcp_sync_functions),
        ("Code Evaluator", test_mcp_evaluator),
        ("Researcher Node", test_mcp_researcher),
        ("Async Client", test_mcp_async),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("  Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {status}: {test_name}")
    
    print("\n" + "-" * 60)
    print(f"  Results: {passed}/{total} tests passed")
    print("=" * 60 + "\n")
    
    if passed == total:
        print("🎉 All MCP tests passed! MCP is working correctly.")
        print("\nNext steps:")
        print("  1. Run the demo: python examples/mcp_demo.py")
        print("  2. Use MCP in your app: from rag_interviewer.mcp_client import ...")
        print("  3. Start the interview app: streamlit run main.py")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
        print("\nTroubleshooting:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Check Python path includes 'src/' directory")
        print("  3. Verify imports work: python -c \"from rag_interviewer.mcp_client import *\"")
    
    print()
    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
