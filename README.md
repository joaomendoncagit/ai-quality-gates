# AI-Enabled Quality Gates in CI/CD

This project is a controlled experiment that evaluates how Large Language Models (LLMs) can complement traditional software quality gates inside a CI/CD pipeline.

The system combines:

- GitHub Actions
- pytest
- OpenAI API (GPT-4o mini)
- Human review

to analyze software changes from three perspectives:

1. Execution-based automated testing
2. AI semantic code review
3. Human decision-making

---

# Project Objective

Traditional CI/CD pipelines mainly rely on predefined tests and static checks. However, these approaches may miss semantic issues, incomplete test coverage, or contextual risks.

This project investigates:

- whether an AI gate can detect issues missed by tests;
- whether AI decisions align with human judgment;
- how AI false positives and false negatives appear in practice;
- how automated and human review can be combined.

The project focuses on decision analysis rather than deployment automation.

---

# Repository Structure

```text
calculator.py
test_calculator.py
ai_quality_gate.py
api_check.py
requirements.txt
results.csv
.github/workflows/quality-gate.yml
README.md
```

# Main Components

### `calculator.py`

Simple calculator implementation used for controlled experiments.

Functions:
```python
add(a, b)
divide(a, b)
```

### `test_calculator.py`

pytest-based automated test suite.

Used as the traditional Test Gate.

### `ai_quality_gate.py`

AI-based quality gate using the OpenAI API and GPT-4o mini.

The AI analyzes:

- correctness
- safety
- test coverage
- code risks

and returns a structured JSON decision:
```json
{
  "decision": "APPROVE",
  "risk": "LOW",
  "reasons": ["..."]
}
```

If the AI rejects the change, the script exits with code 1.

### `quality-gate.yml`

GitHub Actions workflow that:

1. installs dependencies;
2. runs pytest;
3. runs the AI gate;
4. generates a quality summary;
5. marks the pipeline as PASS or FAIL.

Decision logic:

- If TestGate = FAIL OR AI = REJECT → pipeline FAIL
- If TestGate = PASS AND AI = APPROVE → pipeline PASS

Important: the workflow acts as a post-commit feedback mechanism. It does not block git push.

# Experimental Cases

The project contains six controlled experimental scenarios:

| Case | Description                       | Main Purpose                         |
| ---- | --------------------------------- | ------------------------------------ |
| 1    | Baseline safe implementation      | Agreement between all gates          |
| 2    | Faulty addition implementation    | True positive defect detection       |
| 3    | Missing division-by-zero handling | AI catches risk missed by tests      |
| 4    | Incorrect expected value in test  | Test defect missed by AI             |
| 5    | Dynamic execution using `eval()`  | AI false positive and human override |
| 6    | Silent precision loss             | AI false negative and defect leakage |

Results were manually recorded in `results.csv`

# Installation
Clone repository
```bash
git clone https://github.com/joaomendoncagit/ai-quality-gates.git
cd ai-quality-gates
```

Create virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

# Install dependencies
```bash
pip install -r requirements.txt
```

# Configure OpenAI API Key on Linux:
```bash
export OPENAI_API_KEY="api-key"
```

# Run Tests Locally

### Run Tests
```bash
pytest
```

### Run AI Gate
```bash
python ai_quality_gate.py
```

# GitHub Actions

The workflow automatically runs after:

- push to main
- pull request to main

Workflow file:
```bash
.github/workflows/quality-gate.yml
```

# Technologies Used
- Python 3.12
- pytest
- GitHub Actions
- OpenAI API (GPT-4o mini)

# Limitations
- Small experimental codebase
- Only six controlled cases
- Human review remains subjective
- AI decisions may vary over time
- Pipeline is post-commit, not pre-commit
- AI gate depends on external API availability

# Report
- The complete academic report is included separately as PDF.

# Authors

João Mendonça (Universidade da Beira Interior)

Tiago Valente (Universidade da Beira Interior)