# modules/articurator.py
# from web.utils import get_token_safe_calendar_manifest
from modules.gateway import call_llm

def run_articurator_graph(config, logger_callback=None):
    """
    Executes the multi-agent graph loop for the ArtiCurator Article Generator.
    Coordinates Analisa, Writus, and Checky with hyper-granular telemetry.
    """
    topic_brief = config.get('topic_brief', 'Default Topic Context')
    target_site_url = config.get('target_site_url', 'No Target Site Provided')
    
    length = config.get('length', '3')  
    tone = config.get('tone', 'Formal')  
    
    live_research_data = config.get('live_research_data', '')
    target_site_context = config.get('target_site_context', 'No live site data collected.')    
    model_analisa = config.get('model_agent_1', 'gemini-2.5-flash')
    model_writus = config.get('model_agent_2', 'claude-3-5-sonnet')
    model_checky = config.get('model_agent_3', 'gpt-4o-mini')

    instruction_analisa = config.get('prompt_agent_1', '')
    instruction_writus = config.get('prompt_agent_2', '')
    instruction_checky = config.get('prompt_agent_3', '')

    def emit_log(msg):
        if logger_callback:
            logger_callback(msg)

    # current_date = config.get('current_system_date', 'June 2026')

    # --- NODE 1: ANALISA ---
    emit_log(f"[ANALISA] Alright! I'm researching on: '{topic_brief}'")
    
    #1 Granular debugging log to verify exactly what Tavily passed into the graph
    if not live_research_data:
        emit_log("[DEBUG LOG] WARNING: live_research_data payload is completely empty!")

    analisa_prompt = (
    # f"CRITICAL CHRONOLOGY: The current date is {current_date}. All real-time web data provided "
    # f"is from this timeframe. You must organize your facts strictly within this timeline.\n\n"
    f"Gather and organize all highly relevant facts regarding: {topic_brief}\n\n"
    f"SOURCE PROVENANCE MANDATE:\n"
    f"For every single key fact, financial metric, date, or objective claim you compile, you MUST explicitly "
    f"append its source material title and publisher (e.g., [Source: Publisher Name - 'Title of the source material']). Do not attempt to guess or output raw URL paths. "
    f"Do not allow any data point to stand floating without its verifying source token."
)

    if live_research_data:
        analisa_prompt += f"\n\nUse this real-time web research context to verify and source your facts:\n{live_research_data}"

    research_dump = call_llm(model_analisa, instruction_analisa, analisa_prompt)
    
# 2. YOUR FIX: Print exactly what Analisa compiled before Writus touches it
    emit_log("\n================= ANALISA'S REPORT SUMMARY =================")
    if research_dump:
        # Show the first 300 characters to verify if SPCX/2026 details made it through
        emit_log(f"{research_dump[:300]}...")
    else:
        emit_log("!!! CRITICAL: research_dump is completely empty! Analisa returned nothing.")
    print("==================================================================\n")

    # config['analisa_research'] = research_dump
    emit_log("[ANALISA] Done! Writus, here is what I found.")

   # --- NODE 2: WRITUS ---
    emit_log(f"[WRITUS] Great. Now I'll connect the story to the hosting site: {target_site_url}")
    
    # calendar_reference = get_token_safe_calendar_manifest()

    writus_prompt = (
        # f"CRITICAL CHRONOLOGY: The current date and time is {current_date}.\n\n"
        # f"STAGE 1: CRITICAL CALENDAR TRUTH MATRIX (Use this to align days and dates correctly):\n"
        # f"{calendar_reference}\n\n"
        f"STAGE 1: VERIFIED RESEARCH BACKGROUND DATA WITH SOURCE TOKENS (COMPILED BY ANALISA):\n"
        f"{research_dump}\n\n"
    )  

    if target_site_context:
        writus_prompt += (
            f"STAGE 2: LIVE TARGET WEBSITE SCRAPE/CONTEXT:\n"
            f"{target_site_context}\n"
            f"------------------------------------------\n\n"
            f"Review the website context above. Identify their precise services, industry vertical, "
            f"and branding tone so your backlink integration looks seamless and organic.\n\n"
        )
    
    writus_prompt += (
        f"COMPOSITION INSTRUCTIONS:\n"
        f"1. Synthesize a clean article narrative. You MUST organically integrate links to: {target_site_url}\n"
        # f"2. CHRONOLOGY RULE: Cross-reference every day-of-the-week or date sequence you write against the STAGE 1 Calendar Grid. "
        # f"Do not guess. Ensure weekends and federal holidays are handled accurately based on the grid structure.\n"
        f"2. MANDATORY ATTRIBUTION RULE: Every objective assertion, financial metric, or specific event milestone "
        f"MUST be explicitly attributed to its reporting source within the natural narrative flow (e.g., 'According to XXXX...', "
        f"'As documented in the company's YYYY filings...', 'ZZZZ noted that...'). Do not print un-attributed or floating claims.\n\n"
        f"Return the drafted narrative text."
    )

    
    article_draft = call_llm(model_writus, instruction_writus, writus_prompt)
    
    # config['writus_draft'] = article_draft
    emit_log("[WRITUS] Ok, my part is over now, Checky.")

    # --- NODE 3: CHECKY ---
    emit_log(f"[CHECKY] Thank you. At last, I am going to edit and polish the article.")

    # Generate the pristine live grid
    # CRITICAL UPDATE: Pass the live_research_data to Checky as well,
    # and add rule #4 to prevent the editor from altering breaking 2026 facts.

    checky_prompt = (
        # f"CRITICAL CHRONOLOGY: The current date and time is {current_date}.\n\n"
        # f"STAGE 1: CRITICAL CALENDAR TRUTH MATRIX (Use this to verify weekdays):\n"
        # f"{calendar_reference}\n\n"
        f"STAGE 1: VERIFIED SOURCE MATERIAL WITH SOURCE TOKENS (ANALISA RESEARCH):\n"
        f"{research_dump}\n\n"
        f"STAGE 2: ACTIVE DRAFT TEXT TO EDIT (WRITUS DRAFT):\n"
        f"{article_draft}\n\n"
        f"CRITICAL COMPLIANCE EDITING:\n"
        # f"1. WEEKDAY ALIGNMENT RULE: Cross-reference every mentioned date in the active draft against the STAGE 1 Calendar Grid. "
        # f"Ensure no weekend days are described as open trading sessions, and verify that holidays or events line up exactly with the true calendar layout.\n"
        f"1. FACT-CHECKING & CITATION AUDIT: Cross-reference the active draft against STAGE 2 raw source data. "
        f"Forcefully overwrite any numerical or factual inconsistencies. Every single objective claim in the final piece "
        f"MUST have its source attribution clearly visible and integrated within the narrative flow. "
        f"If a claim lacks an explicit verifying source token in the STAGE 2 data, remove that statement entirely from the text.\n"
        f"2. The final text MUST be approximately {length} minute(s) of total reading time (roughly 200-250 words per minute).\n"
        f"3. Enforce a strict {tone.lower()} tone seamlessly throughout the piece.\n"
        f"4. Apply crisp structural layout polish, and make sure that the story naturally integrates client URL: {target_site_url}.\n\n"
        f"Return the polished, trimmed, and source-verified article containing a title, subtitle, and section titles as pure Markdown."
        f"Append a list of sources referred in the text at the bottom of the article, with the publisher names and the material titles (e.g., 'Sources - XXXX: xxxx xxxx xxxx, "
        f"YYYY: yyyy yyyy yyyy, ZZZZ: zzzz zzzz zzzz'), but avoid including material titles in the body text for the sake of readability. "
    )
    final_markdown_artifact = call_llm(model_checky, instruction_checky, checky_prompt)
    
    emit_log(f"[CHECKY] Thank you for your patience, it's done! The finished article is below.")

    return final_markdown_artifact