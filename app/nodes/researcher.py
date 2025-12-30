import os
from firecrawl import FirecrawlApp

def researcher_node(state):
    app = FirecrawlApp(api_key=os.getenv("FIRECRAWL_API_KEY"))
    
    # Scrape the top tech blogs or documentation for the current level
    search_query = f"latest {state['level']} level technical interview questions 2025"
    results = app.search(search_query, params={'limit': 3})
    
    # Convert results into a clean string for Gemini
    context = "\n".join([f"{res['title']}: {res['description']}" for res in results['data']])
    
    return {"tech_context": context}