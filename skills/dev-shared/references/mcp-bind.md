# MCP bind — `dev.mcp` only

1. Discover a ready MCP server named `dev.mcp`. Hosts may prefix the name (for example `user-dev.mcp`). Do not use another server just because the name contains `mcp`.
2. Require a ready/connected status. If the host reports auth-needed, error, or loading, do not treat it as usable.
3. Invoke tools by their **short names** (`figma_*`, `jira_*`, `gitlab_*`, `confluence_*`) on that server.
4. Complete a host auth handshake only when the server requires it; then re-check ready.
5. Bind failed → **stop**. Do not fall back to the official Figma, Atlassian/Rovo, or GitLab MCP servers, or any other wrapper.

Smoke: `gitlab_whoami`. `figma_whoami` if the phase will try Figma.

Do not hardcode a GitLab host, `projectId`, Figma file key, or Jira key in this file.
