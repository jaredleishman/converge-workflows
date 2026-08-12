# Security

Converge is intentionally a skill-only plugin. It ships no MCP
servers, hooks, background services, credential handlers, or automatic network
operations.

The skills may instruct an installed coding agent to read and modify files or
run repository-native commands. Review the plugin before installing it and use
the permission controls provided by your agent harness.

Do not report ordinary workflow disagreements as security vulnerabilities.
Report vulnerabilities that could cause unauthorized command execution,
credential exposure, unsafe installation, or tampering with review evidence
through a private GitHub security advisory for this repository.
