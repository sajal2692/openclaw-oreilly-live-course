# Tools

## Available

- **exec**: Run Python scripts, shell commands, SQL clients
- **read/write/edit**: Read data files, write analysis scripts, save outputs
- **browser**: Access documentation, download public datasets

## Conventions

- Use `exec` with `python3` for all analysis scripts.
- Save visualization outputs as PNG in the workspace.
- Use `read` to inspect data files before processing.
- When working with large files, sample first (head -n 1000) before full analysis.
- Keep analysis scripts in `scripts/` for reproducibility.
