import json
from openai import OpenAI

MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = """You are an AI quality gate for a CI/CD pipeline.

Analyze the provided Python code and tests.

Decision criteria:
- Correctness
- Safety (e.g., division by zero)
- Test coverage
- Code risks

Return STRICT JSON only in this format:

{
  "decision": "APPROVE" or "REJECT",
  "risk": "LOW" or "HIGH",
  "reasons": ["short reasons"]
}
"""

def read_file(path):
    try:
        with open(path, "r") as f:
            return f.read()
    except FileNotFoundError:
        return ""

def analyze_with_ai():
    client = OpenAI()

    code = read_file("calculator.py")
    tests = read_file("test_calculator.py")

    user_prompt = f"""
Analyze the following Python project.

calculator.py:
{code}

test_calculator.py:
{tests}
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0,
        response_format={"type": "json_object"},  # ensures valid JSON
    )

    content = response.choices[0].message.content.strip()

    try:
        result = json.loads(content)
    except json.JSONDecodeError:
        result = {
            "decision": "REJECT",
            "risk": "HIGH",
            "reasons": ["Invalid JSON response from model"]
        }

    print(result)
    return result


if __name__ == "__main__":
    result = analyze_with_ai()

    if result["decision"] == "REJECT":
        exit(1)