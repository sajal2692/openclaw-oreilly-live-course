# Tools

## Available

- **exec**: Run shell commands (git, npm, python, make, etc.)
- **read/write/edit**: Read, create, and modify files in the workspace
- **browser**: Open URLs for documentation reference

## Conventions

- Use `exec` for running tests, linters, and build commands.
- Prefer `edit` over `write` for modifying existing files (sends only the diff).
- Use `git` commands via `exec` for version control operations.
- When running long commands, check output for errors before proceeding.
