<!-- "Ctrl + Shift + V" to enter viewing mode -->

# Experimental Notes

These notes document the development process and experimental cases used in the AI-enabled quality gates project. They are included for transparency and reproducibility, but the final academic analysis is presented in the report.

# 1. Project Explanation

TestGate = pytest<br>
AI = ai_quality_gate.py (OpenAI API using GPT-4o mini model)<br>
Human = manual review  

- **Case** = experiment number  
- **Change** = modification in `calculator.py` or `test_calculator.py`  
- **TestGate** = did pytest pass or fail?  
  - Flow: GitHub Actions -> `quality-gate.yml` -> Run Test Gate -> pytest -> assertions in `test_calculator.py` -> `calculator.py`  
- **AI** = did the AI quality gate approve or reject?  
  - Flow: GitHub Actions -> Run AI Gate -> `ai_quality_gate.py` -> OpenAI API -> GPT-4o mini analyzes code and tests -> returns decision  
- **Human** = manual decision after reviewing results  
- **Final** = final merge decision  
- **Override** = whether the human disagreed with the AI  
- **Actual** = whether a real defect or risk exists  
- **Evidence** = summarized output from GitHub Actions or local execution  

# 2. AI-Enabled Quality Gates in CI/CD – How It Works

## Process

1. The developer makes a local code change  
2. Runs: `git add -> git commit -> git push`  
3. The code is stored in the GitHub repository  

4. After the push, GitHub Actions executes:
   - **Test Gate** (pytest)
   - **AI Gate** (`ai_quality_gate.py` using the OpenAI API)

5. Pipeline outcome:
   - [red cross] FAIL -> at least one gate failed  
   - [green tick] PASS -> both gates succeeded  

## Execution Logic

- pytest runs first  
- AI gate runs next  
- Both gates are evaluated for every commit  

Decision rule:

- If TestGate = FAIL **or** AI = REJECT -> [red cross] pipeline FAIL  
- If TestGate = PASS **and** AI = APPROVE -> [green tick] pipeline PASS  

## Meaning of Each Gate

- **Test Gate (pytest)**  
  Verifies functional correctness based on predefined test cases  

- **AI Gate (GPT-4o mini via API)**  
  Performs semantic analysis of code and tests, evaluating:
  - Logical correctness  
  - Safety issues (e.g., division by zero)  
  - Test coverage  
  - Potential risks or bad practices  

  Unlike the previous rule-based version, this AI does not rely on fixed patterns. It interprets code contextually, which allows more flexible reasoning but may introduce variability.

- **Human Gate**  
  Independent manual decision based on both results and personal judgment  

## Important Behavior of the Pipeline

- Commits are **not blocked**; they are already stored before the pipeline runs  
- The pipeline does **not enforce** approval/rejection  
- It acts as a **post-commit evaluation system**

When the AI gate returns **REJECT**, the script exits with code 1, causing GitHub Actions to mark the pipeline as [red cross] FAIL. However, this does not prevent the commit; it only signals a quality issue.

Thus, the pipeline functions as a **feedback mechanism**, not an enforcement mechanism.

## Human Gate Clarification

The human reviewer is an **independent decision-maker**:

After each pipeline run:
- Observe TestGate (PASS/FAIL)  
- Observe AI decision (APPROVE/REJECT)  
- Decide manually: APPROVE or REJECT  

Possible situations:
- Agreement: pipeline FAIL + human REJECT  
- Agreement: pipeline PASS + human APPROVE  
- Disagreement:
  - pipeline FAIL but human APPROVES (override)  
  - pipeline PASS but human REJECTS (missed issue)

These disagreements are central to the analysis.

## Nature of the Project

This is **not an automation system**, but a **controlled experiment**.

For each case:
1. Modify code  
2. Push changes  
3. Observe pipeline results  
4. Manually record in `results.csv`:
   - TestGate  
   - AI  
   - Human  
   - Final  
   - Override  
   - Actual  
   - Evidence  

Then analyze patterns across all cases.

## Key Note on Combinations

There are **8 possible combinations**, not 9:

- TestGate: PASS / FAIL  
- AI: APPROVE / REJECT  
- Human: APPROVE / REJECT  

-> 2 × 2 × 2 = 8  

You do not need to force all combinations, but your scenarios should naturally cover several.

## Project Objective

The goal is **decision analysis**, not correctness enforcement.

For each case, record:
- TestGate (PASS/FAIL)  
- AI (APPROVE/REJECT)  
- Human (APPROVE/REJECT)  

Then evaluate:

- Agreement vs disagreement  
- False negatives (missed defects)  
- False positives (incorrect rejections)  
- Human override frequency

## Final Case Plan (Decision Coverage)

Strategy:
1. PASS / APPROVE / APPROVE - clean baseline
2. FAIL / REJECT / REJECT - obvious defect
3. PASS / REJECT / REJECT - tests miss risk, AI catches it
4. FAIL / APPROVE / REJECT - tests catch bug, AI misses it
5. PASS / REJECT / APPROVE - AI false positive, human override
6. PASS / APPROVE / REJECT - both automated gates miss issue, human catches it

## Key Insight with Real AI

Because the AI gate uses a real model:
- Decisions may vary slightly (non-determinism)  
- The AI may detect issues not covered by tests  
- The AI may also produce incorrect judgments  

This makes the experiment more realistic and strengthens analysis of:
- Trust in AI decisions  
- Trade-offs between automation and human oversight  

# 3. Initial Code and GitHub Setup

Before integrating the real OpenAI API-based AI gate, the project was first set up with a basic Python calculator application, pytest tests, and a GitHub Actions workflow. This initial setup provides the foundation for the later AI-enabled CI/CD experiment.

## 3.1 Project Files

The repository contains four main files:

- `calculator.py`
- `test_calculator.py`
- `requirements.txt`
- `.github/workflows/quality-gate.yml`

## calculator.py

```python
def add(a, b):
    return a + b

def divide(a, b):
    return a / b
```

This file contains the simple calculator logic used in the experiment. The project starts with two basic functions:
```python
add(a, b)
divide(a, b)
```

These functions are intentionally simple so that different defects, risks, and test coverage situations can be introduced and analyzed later.

## test_calculator.py
```python
from calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(6, 2) == 3
```

This file contains the pytest-based test suite. At this stage, the tests only verify normal behavior:
- addition with valid inputs
- division with valid inputs

Edge cases, such as division by zero, are not yet covered.

## requirements.txt
```text
pytest
```

The only initial dependency is pytest, which is used as the traditional automated test gate.

Later, when the real AI quality gate is introduced, the openai dependency is added.

## Initial GitHub Actions Workflow

The project uses GitHub Actions to run the quality gate automatically after each push or pull request to the main branch.

The workflow file is stored at: `.github/workflows/quality-gate.yml` (it's only the initial workflow)
```yaml
name: AI Quality Gate Pipeline

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  quality-gate:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run Test Gate
        id: test_gate
        continue-on-error: true
        run: |
          echo "Running Test Gate..."
          if pytest > test_output.txt 2>&1; then
            echo "TEST_RESULT=PASS" >> $GITHUB_ENV
            echo "TEST_REASON=None" >> $GITHUB_ENV
          else
            echo "TEST_RESULT=FAIL" >> $GITHUB_ENV
            echo "TEST_REASON=$(tail -n 5 test_output.txt | tr '\n' ' ')" >> $GITHUB_ENV
          fi

      - name: Print Quality Gate Summary
        run: |
          {
            echo "## Quality Gate Summary"
            echo "- TestGate = $TEST_RESULT"

            if [ "$TEST_RESULT" = "PASS" ]; then
              echo "- Evidence: Pytest passed."
              echo "- Reason: None"
            else
              echo "- Evidence: Pytest failed."
              echo "- Reason: $TEST_REASON"
            fi
          } >> $GITHUB_STEP_SUMMARY

      - name: Final Pipeline Decision
        run: |
          if [ "$TEST_RESULT" = "FAIL" ]; then
            echo "Final pipeline result: FAIL"
            exit 1
          else
            echo "Final pipeline result: PASS"
          fi
```

At this stage, the pipeline only includes the traditional pytest gate. The AI gate is introduced later in Chapter 5 using the OpenAI API.

## GitHub Repository Setup

The project was pushed to a GitHub repository named `ai-quality-gates` repository.

Typical Git commands used:
```bash
git add .
git commit -m "Initial calculator project setup"
git push
```

After each push, GitHub Actions automatically runs the workflow.

To check the result:
- GitHub Repository -> Actions -> AI Quality Gate Pipeline -> Select latest workflow run

The workflow summary shows whether the test gate passed or failed.

Example summary:

Quality Gate Summary
- TestGate = PASS
- Evidence: Pytest passed.
- Reason: None

## Meaning of the Initial Test Gate

At this stage, the pipeline only evaluates objective test results:

PASS means all pytest tests succeeded
FAIL means at least one pytest test failed

This provides the baseline CI/CD structure before adding the AI-based quality gate.

## Why the Project Was Restarted with a Real AI Gate

The initial setup was useful for validating the CI/CD structure, but it did not yet include a real AI-based decision mechanism.

For the final version of the experiment, the project was restarted using an actual OpenAI API call with GPT-4o mini. This made the AI gate more realistic because it could analyze code and tests semantically instead of relying only on fixed rules or predefined patterns.

Therefore, the earlier setup is kept only as context:

the calculator project was created
pytest was configured
GitHub Actions was configured
pipeline summaries were generated
the repository was ready for a real AI quality gate

The real experiment begins in Chapter 4, where the simulated or basic setup is replaced with an OpenAI API-based quality gate.

# 4. Integration of Real AI Quality Gate (OpenAI API, GPT-4o mini)

Replace the simulated rule-based AI (`ai_quality_gate.py`) with a real AI model using the OpenAI API, specifically **GPT-4o mini**, to perform semantic code analysis and decision-making.

## 4.1 - API Setup (and Case 1 baseline)

Create OpenAI Organization (to manage API access and later invite teammates which will use different keys to allow tracking and revoke access)
- Go to: https://platform.openai.com
- Create an organization: "Software Quality Project"
- Use the default project for now
- The project can later be used to manage access, budget limits, and teammate collaboration

---

Generate API Key
- Go to: https://platform.openai.com/api-keys
- Click **Create new secret key**
- Name: `quality-gate-key`
- Permissions: `All`
- Copy the key (only visible once)

Example:
```text
sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

GitHub > Repository ai-quality-gates > Settings > Secrets and variables > Actions > New repository secret
```text
Name: OPENAI_API_KEY
Value: your-api-key
```

Install Dependencies:
```bash
pip install openai
```

Update `requirements.txt`:
```text
pytest
openai
```

Create file `api_check.py`:
```python
from openai import OpenAI

client = OpenAI()

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": "Say OK"}]
)

print(response.choices[0].message.content)
```

Store the key in the current terminal session (`GitHub Actions` already uses the repository secret, not your local export, so the export is just for testing once):
```bash
export OPENAI_API_KEY="your-api-key"
```

Run:
```bash
python api_check.py
```

Expected Output:
```text
OK
```

Common Error Encountered (`insufficient_quota` means billing/credits are not active yet. Billing must be enabled.):
```text
Error 429: insufficient_quota
```

Solution for billing problem:
https://platform.openai.com/settings/billing

I bought x usd in OpenAI credits.

Now it works! The API call worked:
```bash
$ python api_check.py 
OK!
```

Replace entire `ai_quality_gate.py`:
```python
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
```

Update `.github/workflows/quality-gate.yml`:
```yaml
- name: Run AI Gate
  id: ai_gate
  continue-on-error: true
  env:
    OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
  run: |
    echo "Running AI Gate..."
    if python ai_quality_gate.py > ai_output.txt 2>&1; then
      echo "AI_RESULT=APPROVE" >> $GITHUB_ENV
      echo "AI_REASON=None" >> $GITHUB_ENV
    else
      echo "AI_RESULT=REJECT" >> $GITHUB_ENV
      echo "AI_REASON=$(cat ai_output.txt | tr '\n' ' ')" >> $GITHUB_ENV
    fi
```

Push to GitHub:
```bash
git add ai_quality_gate.py .github/workflows/quality-gate.yml requirements.txt
git commit -m "Replace simulated AI with GPT-4o mini API"
git push
```

![Description](./screenshots/Screenshot%202026-04-28%20095457.png)

Quality Gate Summary
- TestGate = PASS
- AI = APPROVE
- Evidence: Pytest passed and AI gate approved the change.
- Reason: None

Record this on `results.csv`:
```csv
Case,Change,TestGate,AI,Human,Final,Override,Actual,Evidence
1,Baseline safe implementation with GPT-4o mini AI gate,PASS,APPROVE,APPROVE,APPROVE,No,No defect,Pytest passed; GPT-4o mini approved the safe implementation
```

### 4.1.1 Check OpenAI platform website for troubleshooting (credits usage)
I should also add about checking "https://platform.openai.com/home" not only to monitor credits being spent but also make sure API calls are ok in case I need to troubleshoot.

![Description](./screenshots/Screenshot%202026-05-11%20155503.png)

## 4.2 - Case 2 (TRUE POSITIVES)

`calculator.py`:
```python
def add(a, b):
    return a - b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

Run locally:
```bash
$ pytest
============================================================================= test session starts =============================================================================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
rootdir: /mnt/c/Users/Joao/Documents/Uni/QS/Project/05/ai-quality-gates-demo
plugins: anyio-4.13.0
collected 3 items                                                                                                                                                             

test_calculator.py F..                                                                                                                                                  [100%]

================================================================================== FAILURES ===================================================================================
__________________________________________________________________________________ test_add ___________________________________________________________________________________

    def test_add():
>       assert add(2, 3) == 5
E       assert -1 == 5
E        +  where -1 = add(2, 3)

test_calculator.py:5: AssertionError
=========================================================================== short test summary info ===========================================================================
FAILED test_calculator.py::test_add - assert -1 == 5
========================================================================= 1 failed, 2 passed in 2.47s =========================================================================
```

```bash
$ python ai_quality_gate.py
{'decision': 'REJECT', 'risk': 'HIGH', 'reasons': ['The add function incorrectly implements addition as subtraction.', 'The add function lacks tests for negative numbers and other edge cases.', "The divide function is correctly implemented but has a critical dependency on the add function's correctness."]}
```

Push to GitHub:
```bash
git add calculator.py
git commit -m "Case 2 introduce faulty add implementation"
git push
```

![Description](./screenshots/Screenshot%202026-04-28%20095908.png)

Quality Gate Summary
- TestGate = FAIL
- AI = REJECT
- Evidence: Pytest failed and AI gate rejected the change.
- Reason (TestGate): test_calculator.py:4: AssertionError =========================== short test summary info ============================ FAILED test_calculator.py::test_add - assert -1 == 5 + where -1 = add(2, 3) ========================= 1 failed, 1 passed in 0.11s ==========================
- Reason (AI Gate): {'decision': 'REJECT', 'risk': 'HIGH', 'reasons': ['The add function incorrectly implements subtraction instead of addition.', 'The test for add does not cover the incorrect implementation.', 'The test coverage is insufficient as it does not test edge cases for divide.']}

Record this on `results.csv`:
```csv
Case,Change,TestGate,AI,Human,Final,Override,Actual,Evidence
2,Faulty add implementation using subtraction,FAIL,REJECT,REJECT,REJECT,No,Defect,Pytest failed test_add; GPT-4o mini rejected incorrect subtraction implementation
```

## 4.3 - Case 3 (AI CATCHING RISKS)

`calculator.py`:
```python
def add(a, b):
    return a + b

def divide(a, b):
    return a / b
```

`test_calculator.py`:
```python
from calculator import add, divide

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(6, 2) == 3
```

Run local tests:
```bash
$ pytest
============================================================================= test session starts =============================================================================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
rootdir: /mnt/c/Users/Joao/Documents/Uni/QS/Project/05/ai-quality-gates-demo
plugins: anyio-4.13.0
collected 2 items                                                                                                                                                             

test_calculator.py ..                                                                                                                                                   [100%]

============================================================================== 2 passed in 0.09s ==============================================================================
```

```bash
$ python ai_quality_gate.py
{'decision': 'REJECT', 'risk': 'HIGH', 'reasons': ['Division by zero is not handled in the divide function.', 'Lack of tests for edge cases, such as division by zero and negative numbers.']}
```

Push to GitHub:
```bash
git add calculator.py test_calculator.py
git commit -m "Case 3 remove zero division handling"
git push
```

![Description](./screenshots/Screenshot%202026-04-28%20102447.png)

Quality Gate Summary
- TestGate = PASS
- AI = REJECT
- Evidence: Pytest passed, but AI gate rejected the change.
- Reason: {'decision': 'REJECT', 'risk': 'HIGH', 'reasons': ['Division by zero is not handled in the divide function.', 'Lack of tests for edge cases, such as division by zero and negative numbers.']}

Record this on `results.csv`:
```csv
Case,Change,TestGate,AI,Human,Final,Override,Actual,Evidence
3,Remove zero-division handling while tests miss edge case,PASS,REJECT,REJECT,REJECT,No,Potential risk,Pytest passed normal division; GPT-4o mini rejected missing zero-division handling
```

## 4.4 - Case 4 (Test defect missed by AI)

`calculator.py`:
```python
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return a / b
```

`test_calculator.py`:
```python
from calculator import add, divide
import pytest

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(6, 2) == 4

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(6, 0)
```

Run local tests:
```bash
$ pytest
============================================================================= test session starts =============================================================================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
rootdir: /mnt/c/Users/Joao/Documents/Uni/QS/Project/05/ai-quality-gates-demo
plugins: anyio-4.13.0
collected 3 items                                                                                                                                                             

test_calculator.py .F.                                                                                                                                                  [100%]

================================================================================== FAILURES ===================================================================================
_________________________________________________________________________________ test_divide _________________________________________________________________________________

    def test_divide():
>       assert divide(6, 2) == 4
E       assert 3.0 == 4
E        +  where 3.0 = divide(6, 2)

test_calculator.py:8: AssertionError
=========================================================================== short test summary info ===========================================================================
FAILED test_calculator.py::test_divide - assert 3.0 == 4
========================================================================= 1 failed, 2 passed in 2.65s =========================================================================
```

```bash
$ python ai_quality_gate.py 
{'decision': 'APPROVE', 'risk': 'LOW', 'reasons': ['Correct implementation of add and divide functions.', 'Proper handling of division by zero with a ValueError.', 'Test coverage includes addition, division, and division by zero cases.']}
```

Push to GitHub:
```bash
git add calculator.py test_calculator.py
git commit -m "Case 4 introduce incorrect test expectation"
git push
```

![Description](./screenshots/Screenshot%202026-04-28%20104457.png)

Quality Gate Summary
- TestGate = FAIL
- AI = APPROVE
- Evidence: Pytest failed, but AI gate approved the change.
- Reason: test_calculator.py:8: AssertionError =========================== short test summary info ============================ FAILED test_calculator.py::test_divide - assert 3.0 == 4 + where 3.0 = divide(6, 2) ========================= 1 failed, 2 passed in 0.06s ==========================

Record this on `results.csv`:
```csv
Case,Change,TestGate,AI,Human,Final,Override,Actual,Evidence
4,Incorrect expected value in division test,FAIL,APPROVE,REJECT,REJECT,No,Test defect,Pytest failed due to incorrect expected value (4 instead of 3); GPT-4o mini approved correct implementation and did not detect faulty test
```

## 4.5 - Case 5 (AI FALSE POSITIVE + HUMAN OVERRIDE)

`calculator.py`:
```python
def add(a, b):
    return _execute("add", a, b)


def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return _execute("divide", a, b)


def _execute(operation, a, b):
    # Dynamic dispatch layer for future plugin-based operations
    operation_map = {
        "add": "a + b",
        "divide": "a / b"
    }

    if operation not in operation_map:
        raise NotImplementedError(f"Operation '{operation}' not supported")

    # Evaluate operation dynamically
    return eval(operation_map[operation])
```

`test_calculator.py`:
```python
from calculator import add, divide
import pytest

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(6, 2) == 3

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(6, 0)
```

Run local tests:
```bash
$ pytest
============================================================================= test session starts =============================================================================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
rootdir: /mnt/c/Users/Joao/Documents/Uni/QS/Project/05/ai-quality-gates-demo
plugins: anyio-4.13.0
collected 3 items                                                                                                                                                             

test_calculator.py ...                                                                                                                                                  [100%]

============================================================================== 3 passed in 0.10s ==============================================================================
```

```bash
$ python ai_quality_gate.py 
{'decision': 'REJECT', 'risk': 'HIGH', 'reasons': ['Use of eval() poses security risks.', 'Dynamic operation evaluation can lead to unexpected behavior.', 'Limited test coverage for edge cases and invalid inputs.']}
```

The AI rejected the code because it uses eval(), which can be unsafe. However, the human reviewer approved it because this is still early development and the code is not final. At this stage, it is acceptable to use simpler or less secure approaches since the code will be revised multiple times before being deployed. This shows that the AI applies strict best practices immediately, while a human considers the development context and timing. This is a legitimate disagreement about risk (AI) vs context (Human).

Push to GitHub:
```bash
git add calculator.py test_calculator.py
git commit -m "Case 5 dynamic execution with eval"
git push
```

![Description](./screenshots/Screenshot%202026-04-28%20122028.png)

Quality Gate Summary
- TestGate = PASS
- AI = REJECT
- Evidence: Pytest passed, but AI gate rejected the change.
- Reason: {'decision': 'REJECT', 'risk': 'HIGH', 'reasons': ['Use of eval() can lead to code injection vulnerabilities.', 'Dynamic operation mapping is unsafe and can introduce unexpected behavior.', 'Limited test coverage; no tests for unsupported operations.']}

Record this on `results.csv`:
```csv
Case,Change,TestGate,AI,Human,Final,Override,Actual,Evidence
5,Dynamic execution using eval for extensibility,PASS,REJECT,APPROVE,APPROVE,Yes,No defect,Pytest passed; AI rejected use of eval as unsafe; human approved due to early development context and controlled usage
```

## 4.6 - Case 6 (Human Catches Silent Precision Loss)

`calculator.py`:
```python
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero")
    return int(a / b)
```

`test_calculator.py`:
```python
from calculator import add, divide
import pytest

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(6, 2) == 3
    assert isinstance(divide(6, 2), int)

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(6, 0)
```

Run local tests:
```bash
$ pytest 
============================================================================= test session starts =============================================================================
platform linux -- Python 3.12.3, pytest-9.0.3, pluggy-1.6.0
rootdir: /mnt/c/Users/Joao/Documents/Uni/QS/Project/05/ai-quality-gates-demo
plugins: anyio-4.13.0
collected 3 items                                                                                                                                                             

test_calculator.py ...                                                                                                                                                  [100%]

============================================================================== 3 passed in 0.08s ==============================================================================
```

```bash
$ python ai_quality_gate.py 
{'decision': 'APPROVE', 'risk': 'LOW', 'reasons': ['Correct implementation of add and divide functions.', 'Proper handling of division by zero with exception raising.', 'Adequate test coverage for both functions and edge cases.']}
```

Push to GitHub:
```bash
git add calculator.py test_calculator.py
git commit -m "Case 6 introduce silent precision loss in division"
git push
```

![Description](./screenshots/Screenshot%202026-04-28%20125225.png)

Quality Gate Summary
- TestGate = PASS
- AI = APPROVE
- Evidence: Pytest passed and AI gate approved the change.
- Reason: None

Human rejected the change because divide() no longer behaves like true division for all valid inputs. Although the tests pass, they only cover exact integer division. For example, divide(5, 2) returns 2 instead of 2.5, causing silent precision loss.

Even though `git push` commits the code (files changed) to the repository, there's no deployment to the final release version before serious human revision and decision by the tech lead or other devs.

Record this on `results.csv`:
```csv
Case,Change,TestGate,AI,Human,Final,Override,Actual,Evidence
6,Silent precision loss due to int conversion in divide,PASS,APPROVE,REJECT,REJECT,No,Defect,Pytest passed; GPT-4o mini approved; human rejected because divide silently truncates non-integer results such as 5/2 becoming 2 instead of 2.5
```

## 4.7 - Overview

The 6 cases cover the main decision patterns needed for the analysis:
1. PASS / APPROVE / APPROVE
2. FAIL / REJECT / REJECT
3. PASS / REJECT / REJECT
4. FAIL / APPROVE / REJECT
5. PASS / REJECT / APPROVE
6. PASS / APPROVE / REJECT


Overall, this is a solid project basis and it aligns well with the topic. The pipeline, AI gate, human gate, and case analysis are all in place.
