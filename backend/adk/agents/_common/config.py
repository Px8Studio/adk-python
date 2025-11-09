import os

DEFAULT_LLM_MODEL = "gemini-2.5-flash"

def get_llm_model() -> str:
    # Priority: ORKHON_LLM_MODEL > ROOT_AGENT_MODEL > GOOGLE_GEMINI_MODEL > default
    return (
        os.getenv("ORKHON_LLM_MODEL")
        or os.getenv("ROOT_AGENT_MODEL")
        or os.getenv("GOOGLE_GEMINI_MODEL")
        or DEFAULT_LLM_MODEL
    )