"""Example usage of MCP (Model Context Protocol) in RAG Interview Agent.

This file demonstrates how to use MCP features:
1. Fetch live tech documentation
2. Get current industry trends
3. Evaluate code with MCP-enhanced tools

Usage:
    python examples/mcp_demo.py
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from rag_interviewer.mcp_client import (
    MCPInterviewClient,
    get_tech_trends_sync,
    search_documentation_sync
)
from rag_interviewer.mcp_evaluator import MCPEvaluator, evaluate_with_mcp


def demo_mcp_client():
    """Demonstrate MCP client capabilities."""
    print("🚀 MCP Client Demo")
    print("=" * 50)
    
    # Demo 1: Get tech trends
    print("\n1. Fetching tech trends for 'Python':")
    trends = get_tech_trends_sync("python")
    print(f"   Trends: {', '.join(trends)}")
    
    # Demo 2: Get tech trends for AI
    print("\n2. Fetching tech trends for 'AI':")
    trends = get_tech_trends_sync("AI")
    print(f"   Trends: {', '.join(trends)}")
    
    print("\n✅ MCP Client Demo Complete")


def demo_mcp_evaluator():
    """Demonstrate MCP-enhanced code evaluation."""
    print("\n\n🧪 MCP Evaluator Demo")
    print("=" * 50)
    
    # Demo 1: Evaluate code with syntax errors
    print("\n1. Evaluating Python code with syntax error:")
    code_with_error = """
def calculate_sum(a, b
    return a + b
"""
    result = evaluate_with_mcp(
        question="Write a function to calculate sum",
        answer=f"```python\n{code_with_error}\n```",
        level="beginner"
    )
    print(f"   Score: {result['score']}/10")
    print(f"   Has Code: {result['has_code']}")
    print(f"   Notes: {result['evaluation_notes']}")
    
    # Demo 2: Evaluate good code
    print("\n2. Evaluating good Python code:")
    good_code = """
def calculate_sum(a: int, b: int) -> int:
    \"\"\"Calculate the sum of two numbers.\"\"\"
    return a + b
"""
    result = evaluate_with_mcp(
        question="Write a function to calculate sum",
        answer=f"```python\n{good_code}\n```",
        level="beginner"
    )
    print(f"   Score: {result['score']}/10")
    print(f"   Code Analysis: {result['code_analysis']}")
    
    print("\n✅ MCP Evaluator Demo Complete")


def demo_mcp_researcher():
    """Demonstrate MCP-enhanced researcher."""
    print("\n\n🔍 MCP Researcher Demo")
    print("=" * 50)
    
    from rag_interviewer.nodes.researcher_mcp import (
        researcher_node_enhanced,
        extract_tech_keywords
    )
    
    # Demo 1: Extract tech keywords
    print("\n1. Extracting tech keywords from job description:")
    jd = """
    Senior Python Developer with experience in FastAPI, Kubernetes, 
    and Machine Learning. Must know PostgreSQL and Docker.
    """
    keywords = extract_tech_keywords(jd)
    print(f"   Detected: {', '.join(keywords)}")
    
    # Demo 2: Researcher node with MCP
    print("\n2. Running MCP-enhanced researcher node:")
    state = {
        "job_description": "Looking for a Python developer with FastAPI experience",
        "messages": [],
        "level": "intermediate"
    }
    result = researcher_node_enhanced(state)
    print(f"   Context length: {len(result['tech_context'])} characters")
    print(f"   Contains trends: {'Trends' in result['tech_context']}")
    
    print("\n✅ MCP Researcher Demo Complete")


def demo_async_mcp():
    """Demonstrate async MCP operations."""
    print("\n\n⚡ Async MCP Demo")
    print("=" * 50)
    
    import asyncio
    
    async def async_demo():
        """Async MCP demo."""
        client = MCPInterviewClient()
        
        print("\n1. Async tech trends fetch:")
        async with client.connect():
            trends = await client.get_current_tech_trends("kubernetes")
            print(f"   Trends: {', '.join(trends)}")
        
        return "Async demo complete"
    
    try:
        result = asyncio.run(async_demo())
        print(f"\n   ✅ {result}")
    except Exception as e:
        print(f"\n   ⚠️  Async demo skipped: {e}")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("  MCP (Model Context Protocol) Demo for RAG Interview Agent")
    print("=" * 60 + "\n")
    
    # Run all demos
    demo_mcp_client()
    demo_mcp_evaluator()
    demo_mcp_researcher()
    
    # Optional async demo (may fail if MCP server not running)
    try:
        demo_async_mcp()
    except Exception as e:
        print(f"\n⚠️  Async demo failed (expected if MCP server not running): {e}")
    
    print("\n" + "=" * 60)
    print("  All MCP demos complete!")
    print("=" * 60 + "\n")
