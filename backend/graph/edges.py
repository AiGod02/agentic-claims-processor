def route_after_documents(state: dict) -> str:
    """
    Conditional routing after document_agent.
    Returns 'exit_early' if blocking error, else 'continue'.
    """
    if state.get("blocking_error"):
        return "exit_early"
    if not state.get("document_agent_passed"):
        return "exit_early"
    return "continue"
