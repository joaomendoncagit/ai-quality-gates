def ai_review(code_change_description):
    """
    Simulated AI decision
    """
    if "divide" in code_change_description:
        return {
            "risk": "HIGH",
            "decision": "REJECT",
            "reason": "Potential division by zero"
        }
    
    return {
        "risk": "LOW",
        "decision": "APPROVE",
        "reason": "No obvious issues"
    }


if __name__ == "__main__":
    example = "Added divide function"
    result = ai_review(example)
    print(result)