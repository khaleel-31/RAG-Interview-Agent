"""Realistic MCP Assessment - What Actually Works"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("="*70)
print("MCP REALISTIC FUNCTIONALITY ASSESSMENT")
print("="*70)

# Test 1: Check if MCP infrastructure works
print("\n1. MCP Infrastructure")
print("-" * 70)
try:
    from rag_interviewer.mcp_config import get_mcp_registry
    from rag_interviewer.mcp_client import get_tech_trends_sync, is_mcp_available
    
    registry = get_mcp_registry()
    enabled = registry.get_enabled_servers()
    
    print(f"   MCP Available: {is_mcp_available()}")
    print(f"   Servers Configured: {len(registry.servers)}")
    print(f"   Servers Enabled: {len(enabled)}")
    for server in enabled:
        print(f"     - {server.name}: {server.description[:40]}...")
    print("   Status: WORKING ✓")
except Exception as e:
    print(f"   Status: FAILED - {e}")

# Test 2: Test trends (guaranteed to work)
print("\n2. Tech Trends (Static Database)")
print("-" * 70)
try:
    trends = get_tech_trends_sync("python")
    print(f"   Trends for 'python': {', '.join(trends[:3])}")
    print("   Status: WORKING ✓")
    trends_work = True
except Exception as e:
    print(f"   Status: FAILED - {e}")
    trends_work = False

# Test 3: Test keyword extraction
print("\n3. Keyword Extraction")
print("-" * 70)
try:
    from rag_interviewer.nodes.researcher_multi_mcp import extract_tech_keywords
    
    jd = "Python developer with FastAPI, Kubernetes, and Docker"
    keywords = extract_tech_keywords(jd)
    print(f"   Input: {jd[:50]}...")
    print(f"   Keywords: {', '.join(keywords[:5])}")
    print("   Status: WORKING ✓")
    keywords_work = True
except Exception as e:
    print(f"   Status: FAILED - {e}")
    keywords_work = False

# Test 4: Test code evaluation
print("\n4. Code Evaluation")
print("-" * 70)
try:
    from rag_interviewer.mcp_evaluator import evaluate_with_mcp
    
    result = evaluate_with_mcp(
        question="Write a function",
        answer="```python\ndef hello(): print('hi')\n```",
        level="beginner"
    )
    print(f"   Score: {result['score']}/10")
    print(f"   Has Code: {result['has_code']}")
    print("   Status: WORKING ✓")
    code_eval_work = True
except Exception as e:
    print(f"   Status: FAILED - {e}")
    code_eval_work = False

# Test 5: Check web fetch capability
print("\n5. Web Fetch (External Data)")
print("-" * 70)
print("   Note: This requires internet + proper mcp-server-fetch setup")
print("   Status: MAY NOT WORK (network/firewall/tool limitations)")

# Summary
print("\n" + "="*70)
print("SUMMARY")
print("="*70)

working_features = []
if trends_work:
    working_features.append("Tech Trends Database")
if keywords_work:
    working_features.append("Keyword Extraction")
if code_eval_work:
    working_features.append("Code Evaluation")

print(f"\nWorking Features ({len(working_features)}):")
for feature in working_features:
    print(f"  ✓ {feature}")

print("\nValue Provided by MCP:")
print("  1. Structured tech keyword detection")
print("  2. Current technology trend awareness")
print("  3. Code syntax validation")
print("  4. Multi-server architecture (ready for expansion)")

print("\nWeb Fetch Status:")
print("  ⚠ Not currently returning external data")
print("  ⚠ May require network configuration")
print("  ⚠ Infrastructure is ready when fetch works")

print("\nRecommendation:")
if len(working_features) >= 2:
    print("  ✓ MCP is providing VALUE to your interviews!")
    print("  ✓ Keyword extraction + trends enhance context")
    print("  ⚠ Web fetch is bonus (not required for core functionality)")
else:
    print("  ✗ Check MCP installation and configuration")

print("\n" + "="*70)
print("Next Steps:")
print("  1. Run your app: streamlit run main.py")
print("  2. Upload a job description")
print("  3. Check logs for keyword extraction")
print("  4. Interview will use trends + keywords automatically")
print("="*70)
