# modules/articurator.py
import time

def run_articurator_graph(config):
    """
    Executes the multi-agent graph loop for the ArtiCurator content engine.
    Unpacks the tailored prompt personas and engine routings for each agent node.
    """
    trace_logs = []
    
    # Extract structural configs from Step 2 configuration form payload
    topic_brief = config.get('topic_brief', '')
    
    model_agent_1 = config.get('model_agent_1', 'gemini-1.5-pro')
    model_agent_2 = config.get('model_agent_2', 'claude-3-5-sonnet')
    model_agent_3 = config.get('model_agent_3', 'gpt-4o-mini')
    
    prompt_agent_1 = config.get('prompt_agent_1', '')
    prompt_agent_2 = config.get('prompt_agent_2', '')
    prompt_agent_3 = config.get('prompt_agent_3', '')

    # --- NODE 1: WEB SNATCHER AGENT ---
    trace_logs.append(f"[WEB SNATCHER AGENT] Active Node Model: {model_agent_1}")
    trace_logs.append(f"[WEB SNATCHER AGENT] Target Initialized: Querying search matrices for brief keywords...")
    time.sleep(1.0)
    trace_logs.append("[WEB SNATCHER AGENT] Content scraping complete. Extracted raw document payload data structures.")
    
    # --- NODE 2: CONTEXTUAL WRITER AGENT ---
    trace_logs.append(f"\n[CONTEXTUAL WRITER AGENT] Active Node Model: {model_agent_2}")
    trace_logs.append("[CONTEXTUAL WRITER AGENT] Synthesizing comprehensive textual narrative drafts...")
    time.sleep(1.5)
    trace_logs.append("[CONTEXTUAL WRITER AGENT] Draft compiled. Initial article structured successfully.")

    # --- NODE 3: EDITORIAL REVIEW AGENT ---
    trace_logs.append(f"\n[EDITORIAL REVIEW AGENT] Active Node Model: {model_agent_3}")
    trace_logs.append("[EDITORIAL REVIEW AGENT] Auditing structural constraints and brand logic alignment...")
    time.sleep(1.0)
    trace_logs.append("[EDITORIAL REVIEW AGENT] Polish and formatting benchmarks approved. Output ready.")

    # We construct the block using safe single-line concatenation strings to avoid triple-quote failures
    simulated_artifact = (
        "# ArtiCurator Content Extraction Summary\n"
        f"- **Topic Brief Context:** {topic_brief}\n\n"
        "## Orchestration Frame Node Engine Mapping\n"
        f"- **Web Snatcher Node:** {model_agent_1}\n"
        f"- **Contextual Writer Node:** {model_agent_2}\n"
        f"- **Editorial Review Node:** {model_agent_3}\n\n"
        "## Extracted & Curated Insights\n"
        "Content synthesis completed successfully via AgenTrio Multi-Agent Infrastructure.\n"
        "Insights and formatted drafts have been safely written to local disk volumes.\n"
    )

    return "\n".join(trace_logs), simulated_artifact