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