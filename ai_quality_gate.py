import ast


def analyze_file(filename):
    with open(filename, "r") as file:
        code = file.read()

    risks = []

    if "return a / b" in code and "b == 0" not in code:
        risks.append("Division operation without explicit zero-division check")

    if "return a - b" in code:
        risks.append("Suspicious subtraction found in add-like logic")

    if "def multiply" in code:
        try:
            with open("test_calculator.py", "r") as test_file:
                tests = test_file.read()
            if "test_multiply" not in tests:
                risks.append("New multiply function has no corresponding test")
        except FileNotFoundError:
            risks.append("Test file missing")

    try:
        ast.parse(code)
    except SyntaxError:
        risks.append("Python syntax error detected")

    if risks:
        return {
            "risk": "HIGH",
            "decision": "REJECT",
            "reasons": risks
        }

    return {
        "risk": "LOW",
        "decision": "APPROVE",
        "reasons": ["No major risk detected"]
    }


if __name__ == "__main__":
    result = analyze_file("calculator.py")
    print(result)

    if result["decision"] == "REJECT":
        exit(1)