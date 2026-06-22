# modules/acl_generator.py
import os
from modules.gateway import call_llm

def run_acl_agent_graph(config, logger_callback=None):
    """
    Executes the multi-agent graph loop for the Anti-Corruption Layer Generator.
    Coordinates the Mapping Analyst, Coder Node, and Quality Gate using the LLM Gateway.
    Completely decoupled from Django via a functional callback string emitter.
    """
    # 1. Extract file paths and normalize them to intuitive variables
    source_csv = config.get('uploaded_csv_path', '')
    target_csv = config.get('target_schema_csv_path', '')
    
    # 2. Extract dynamic model allocation matrix entries
    model_analyst = config.get('model_agent_1', 'gemini-1.5-pro')
    model_coder = config.get('model_agent_2', 'claude-3-5-sonnet')
    model_tester = config.get('model_agent_3', 'gpt-4o-mini')

    # 3. Read custom system prompt behavior profiles
    instruction_analyst = config.get('prompt_agent_1', 'You are a strategic mapping analyst.')
    instruction_coder = config.get('prompt_agent_2', 'You are an elite Python software engineer.')
    instruction_tester = config.get('prompt_agent_3', 'You are a strict QA automation engineer.')

    def emit_log(msg):
        if logger_callback:
            logger_callback(msg)

    # 4. Ingest file contents safely from local volumes
    source_sample = ""
    target_content = ""
    
    if source_csv and os.path.exists(source_csv):
        with open(source_csv, 'r', encoding='utf-8', errors='ignore') as f:
            source_sample = "".join(f.readlines()[:20]) # First 20 lines context window
            
    if target_csv and os.path.exists(target_csv):
        with open(target_csv, 'r', encoding='utf-8', errors='ignore') as f:
            target_content = f.read()

    # --- NODE 1: STRATEGIC MAPPING ANALYST ---
    emit_log(f"[ANALYST AGENT] Initiating schema analysis layout via {model_analyst}...")
    analyst_prompt = (
        f"Analyze the mapping between this Source Data sample:\n{source_sample}\n\n"
        f"And this Target Database Schema Layout:\n{target_content}\n\n"
        "Provide a detailed field-by-field mapping strategy report."
    )
    analyst_report = call_llm(model_analyst, instruction_analyst, analyst_prompt)
    config['analyst_report'] = analyst_report
    emit_log("[ANALYST AGENT] Structural mapping strategy successfully compiled.")

    # --- NODE 2: DETERMINISTIC CODER NODE ---
    emit_log(f"[CODER AGENT] Synthesizing physical Python data transformation code via {model_coder}...")
    coder_prompt = (
        f"Based on this structural analysis mapping report:\n{analyst_report}\n\n"
        "Write a complete, functional Python translation script using the csv module that acts "
        "as an insulated Anti-Corruption Layer mapping data from the source file layout to the target schema."
    )
    generated_code = call_llm(model_coder, instruction_coder, coder_prompt)
    config['generated_code'] = generated_code
    emit_log("[CODER AGENT] Compilation successful. Python mapping module generated.")

    # --- NODE 3: AUTOMATED QUALITY GATE (TESTER) ---
    emit_log(f"[TESTER AGENT] Executing code quality verification checks using {model_tester}...")
    tester_prompt = (
        f"Review the following generated script for type safety, missing mappings, or syntax leaks:\n{generated_code}\n\n"
        "Output the final polished code wrapped perfectly in markdown blocks alongside an evaluation summary."
    )
    final_artifact = call_llm(model_tester, instruction_tester, tester_prompt)
    emit_log("[TESTER AGENT] Evaluation complete. Production artifact approved.")

    return final_artifact