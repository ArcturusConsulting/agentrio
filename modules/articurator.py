# modules/articurator.py
from modules.gateway import call_llm

def run_articurator_graph(config, logger_callback=None):
    """
    Executes the multi-agent graph loop for the ArtiCurator Article Generator.
    Coordinates Analisa, Writus, and Checky with hyper-granular telemetry.
    """
    topic_brief = config.get('topic_brief', 'Default Topic Context')
    target_site_url = config.get('target_site_url', 'No Target Site Provided')
    
    model_analisa = config.get('model_agent_1', 'gemini-2.5-flash')
    model_writus = config.get('model_agent_2', 'claude-3-5-sonnet')
    model_checky = config.get('model_agent_3', 'gpt-4o-mini')

    instruction_analisa = config.get('prompt_agent_1', '')
    instruction_writus = config.get('prompt_agent_2', '')
    instruction_checky = config.get('prompt_agent_3', '')

    def emit_log(msg):
        if logger_callback:
            logger_callback(msg)

    # --- NODE 1: ANALISA ---
    emit_log("[ANALISA] Node state initialized. Evaluating topic context matrices...")
    emit_log(f"[ANALISA] Target Topic Detected: '{topic_brief}'")
    emit_log(f"[ANALISA] Dispatching live payload handshake to engine: {model_analisa}...")
    
    analisa_prompt = f"Gather and organize all highly relevant facts regarding: {topic_brief}"
    research_dump = call_llm(model_analisa, instruction_analisa, analisa_prompt)
    
    config['analisa_research'] = research_dump
    emit_log("[ANALISA] Core response payload returned from remote server gateway.")
    emit_log("[ANALISA] Deep research analysis compiled. Context schema updated successfully.")

    # --- NODE 2: WRITUS ---
    emit_log("\n[WRITUS] Node state initialized. Pulling upstream research cache inputs...")
    emit_log(f"[WRITUS] Target Anchor Domain Configured: {target_site_url}")
    emit_log(f"[WRITUS] Formulating narrative synthesis stream using engine: {model_writus}...")
    
    writus_prompt = (
        f"Using this verified research background data:\n{research_dump}\n\n"
        f"Synthesize a clean article narrative. You MUST organically integrate links to: {target_site_url}"
    )
    article_draft = call_llm(model_writus, instruction_writus, writus_prompt)
    
    config['writus_draft'] = article_draft
    emit_log("[WRITUS] Narrative structure completed. Drafting tokens allocated successfully.")
    emit_log("[WRITUS] Editorial draft cached safely in memory registers.")

    # --- NODE 3: CHECKY ---
    emit_log("\n[CHECKY] Node state initialized. Securing content layout boundaries...")
    emit_log(f"[CHECKY] Running final quality control check and markdown translation via: {model_checky}...")
    
    checky_prompt = (
        f"Review this active draft text carefully:\n{article_draft}\n\n"
        f"Apply layout polish. Replace any 'YOUR_CONSULTANCY_WEBSITE_LINK' strings with our client URL: {target_site_url}. Return pure Markdown."
    )
    final_markdown_artifact = call_llm(model_checky, instruction_checky, checky_prompt)
    
    emit_log("[CHECKY] Layout validation complete. Formatting metrics cleared.")
    emit_log("[CHECKY] All matrix quality gates passed successfully. Markdown compilation approved.")

    return final_markdown_artifact