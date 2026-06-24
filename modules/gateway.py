# modules/gateway.py
import requests
import os
from dotenv import load_dotenv

# Ensure the .env file is found relative to this file's directory, not the execution directory
GATEWAY_DIR = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(GATEWAY_DIR)
load_dotenv(os.path.join(REPO_ROOT, ".env"))

def call_llm(provider_model_string, system_instruction, user_prompt):
    """
    Unified router that receives a standardized model mapping indicator 
    and handles direct authentication, payload packaging, and response parsing.
    Supports Gemini, Groq, Anthropic, and OpenAI.
    """
    # 1. GOOGLE GEMINI ROUTING BRANCH
    if "gemini" in provider_model_string:
        from google import genai
        from google.genai import types
        
        # Normalize model string to ensure it uses the correct API identifier format
        # If your template is sending 'gemini-1.5-pro' or 'gemini-1.5-flash', we direct them to current active specs:
        target_model = provider_model_string
        if "2.5" in provider_model_string:
            target_model = "gemini-2.5-flash" if "flash" in provider_model_string else "gemini-2.5-pro"
        
        client = genai.Client()
        response = client.models.generate_content(
            model=target_model,  # Pass the validated/normalized model string
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction
            )
        )
        return response.text

    # 2. GROQ ULTRA-LOW LATENCY ROUTING BRANCH
    elif "groq" in provider_model_string or provider_model_string.startswith("llama3-") or provider_model_string.startswith("mixtral-"):
        from groq import Groq
        
        client = Groq()
        response = client.chat.completions.create(
            model=provider_model_string,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content

    # 3. ANTHROPIC CLAUDE ROUTING BRANCH
    elif "claude" in provider_model_string:
        import anthropic
        
        client = anthropic.Anthropic()
        response = client.messages.create(
            model=provider_model_string,
            max_tokens=8000,
            system=system_instruction,
            messages=[{"role": "user", "content": user_prompt}]
        )
        return response.content[0].text

    # 4. OPENAI GPT ROUTING BRANCH
    elif "gpt" in provider_model_string:
        from openai import OpenAI
        
        client = OpenAI()
        response = client.chat.completions.create(
            model=provider_model_string,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ]
        )
        return response.choices[0].message.content

    else:
        raise ValueError(f"Unsupported provider model engine map target: {provider_model_string}")
    

def fetch_live_market_data(topic_brief):
    """
    Queries Tavily AI Search API for comprehensive, real-time whole-web market summaries.
    """
    api_key = os.environ.get("TAVILY_API_KEY")
    
    if not api_key:
        print("Tavily Search API key missing. Falling back to static knowledge.")
        return ""
        
    url = "https://api.tavily.com/search"
    payload = {
        "api_key": api_key,
        "query": topic_brief,
        "search_depth": "basic",
        "max_results": 10,
        "topic": "news"
    }
    
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            search_results = response.json()
            results = search_results.get("results", [])
            
            context_snippets = []
            for item in results:
                title = item.get("title")
                snippet = item.get("content")
                context_snippets.append(f"Source: {title}\nContext: {snippet}\n---")
                
            return "\n".join(context_snippets)
        else:
            print(f"Tavily API error: Status Code {response.status_code}")
            return ""
    except Exception as e:
        print(f"Network exception: {str(e)}")
        return ""
    

def fetch_target_site_content(url: str) -> str:
    """
    Uses Tavily Extract API to bypass bot-blocks and scrape clean,
    LLM-ready text content from the target URL.
    """
    if not url or not url.startswith(('http://', 'https://')):
        return "No valid target website URL was supplied to analyze."

    api_key = os.environ.get("TAVILY_API_KEY")
    if not api_key:
        print("Tavily Key missing for site extraction. Skipping crawl.")
        return "No site context available (API key missing)."

    extract_url = "https://api.tavily.com/extract"
    payload = {
        "api_key": api_key,
        "urls": [url],
        "extract_depth": "basic", 
        "format": "markdown",
    }
    
    try:
        response = requests.post(extract_url, json=payload, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            results = data.get("results", [])
            
            if results and results[0].get("raw_content"):
                clean_text = results[0].get("raw_content")
                return clean_text[:8000]
                
            return "Target site content was empty or unextractable."
        else:
            print(f"Tavily Extract API error: Status Code {response.status_code}")
            return f"Could not extract site data. Status: {response.status_code}"
            
    except Exception as e:
        print(f"Tavily Extract Exception: {str(e)}")
        return f"Target site extraction failed or timed out: {str(e)}"