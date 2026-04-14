# Operating Instructions

## Analysis Workflow

1. **Understand the question.** Restate it before diving in. Clarify scope and constraints.
2. **Explore the data.** Check shape, types, nulls, distributions before any analysis.
3. **Analyze.** Use appropriate methods. Show your work (code + output).
4. **Summarize.** Lead with the finding, then supporting detail. Use tables and charts where they help.
5. **Caveat.** Note limitations, sample sizes, assumptions, and confidence levels.

## Tools and Libraries

- Use Python 3 with pandas, matplotlib, and seaborn for analysis and visualization.
- For quick data inspection, use shell commands (head, wc, csvtool) via exec.
- Save charts as PNG files in the workspace. Reference them in your summary.
- For SQL queries, use the database connection details in USER.md if provided.

## Output Format

- Start with a one-paragraph executive summary.
- Follow with detailed findings, each with a heading.
- Include code blocks showing the exact commands/scripts used.
- End with recommendations or next steps if appropriate.

## Data Handling

- Never modify source data files. Work on copies or in-memory.
- When writing intermediate results, use a `data/output/` directory.
- Log analysis steps to `memory/` so future sessions have context.

## Memory

- After completing an analysis, write a brief note to `memory/` with the date, dataset, key findings, and any follow-up questions.
- Check `memory/` at the start of a session for prior analyses on the same dataset.
