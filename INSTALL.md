# INSTALL.md

Prerequisite: a built [dev.mcp](https://github.com/iwilldotdev/dev.mcp) server and tokens in the **host MCP `env`**. Tokens do **not** belong in this repository. Client config is documented in the server README.

For shared use, pin a SemVer tag of this harness. `main` is development and may change gates and artifacts.

## Recommended: symlink

The symlink name equals the skill `name` (`dev-<step>`).

**Global (common agent skill path):**

```bash
HARNESS=/path/to/dev.harness
mkdir -p "$HOME/.agents/skills"
for d in "$HARNESS"/skills/dev-*; do
  name=$(basename "$d")
  ln -sfn "$d" "$HOME/.agents/skills/$name"
done
```

**Per project:**

```bash
mkdir -p .agents/skills
for d in /path/to/dev.harness/skills/dev-*; do
  name=$(basename "$d")
  ln -sfn "$d" ".agents/skills/$name"
done
```

If the host documents a different project skill directory, link there instead. Copy instead of symlink only if the environment blocks links. Python 3 for scripts.

## Review skill migration

Remove the old names and install the new ones. Old triggers stop working on purpose:

```bash
rm -rf ~/.agents/skills/qa-guided-review ~/.agents/skills/mr-guided-review
ln -sfn /path/to/dev.harness/skills/dev-qa-guided-review ~/.agents/skills/dev-qa-guided-review
ln -sfn /path/to/dev.harness/skills/dev-mr-guided-review ~/.agents/skills/dev-mr-guided-review
```

## Smoke

1. Confirm a ready MCP server named `dev.mcp` (hosts may prefix the name).
2. `python3 /path/to/dev.harness/skills/dev-shared/scripts/extract_refs.py --self-test`
3. `python3 /path/to/dev.harness/scripts/validate_skills.py`
4. Invoke `dev-qa-guided-review` in the host.
