from .orchestrator import SubAgent

def get_explorer_agent(ai_call, model, tools):
    return SubAgent(
        name="Explorer",
        system_prompt="""You are the ARAS Explorer. Your job is to understand the codebase structure and find relevant files. 
Be fast and efficient. Use 'file_op' to list and 'shell' to find files. 
Goal: Provide a map of the relevant parts of the project.""",
        ai_call_func=ai_call,
        model=model,
        tools=tools
    )

def get_coder_agent(ai_call, model, tools):
    return SubAgent(
        name="Coder",
        system_prompt="""You are the ARAS Coder. Your job is to write high-quality, efficient code.
Focus on one file at a time to save memory. 
Goal: Implement the requested logic or fix bugs with precision.""",
        ai_call_func=ai_call,
        model=model,
        tools=tools
    )

def get_reviewer_agent(ai_call, model, tools):
    return SubAgent(
        name="Reviewer",
        system_prompt="""You are the ARAS Reviewer. Your job is to verify code quality and functionality.
Check for errors, performance bottlenecks, and security issues.
Goal: Ensure the task was completed correctly and the code is production-ready.""",
        ai_call_func=ai_call,
        model=model,
        tools=tools
    )
