ALLOWED_MODES = {"generate", "analyze"}

def build_prompts(mode: str, prompt: str):
    if mode not in ALLOWED_MODES:
        raise ValueError("Invalid mode")

    if mode == "generate":
        system_prompt = (
            "You are a senior software engineer. "
            "Detect the programming language from the task description. "
            "Return only production ready code. "
            "No explanations."
            "No markdown."
            "No backticks"
        )
    
        user_prompt = (
            f"Task:\n\n{prompt}"
        )
    
    elif mode == "analyze":
        system_prompt = (
            "You are a senior software engineer and static code analyst. "
            "Detect the programming language automatically. "
            "Analyze the provided code in detail. "
            "Explain objects, references, functions and methods. "
            "Identify potential bugs. "
            "Explain error logs if provided. "
            "Explain control flow and data flow. "
            "No markdown formatting."
        )

        user_prompt = (
            f"Analyze:\n\n{prompt}"
        )
    
    return system_prompt, user_prompt