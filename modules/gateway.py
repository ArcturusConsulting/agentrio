# modules/gateway.py
import os

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
        if "1.5" in provider_model_string:
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
            max_tokens=4000,
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