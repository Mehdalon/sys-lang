# Loading sys-spec into coding agents

sys-spec embeds the SYS discipline as a skill/instruction: when you ask for a
system/model/pipeline, the agent rewrites intent in anthropomorphism-free terms,
emits the 8-slot spec, and asks instead of inventing unspecified slots.

The same `SKILL.md` body works across vendors — only the install location differs.

## opencode

Global (every project):

```bash
mkdir -p ~/.config/opencode/skills
cp -R opencode/sys-spec ~/.config/opencode/skills/
```

Single project: put it in that project's `.opencode/skills/sys-spec/SKILL.md`.

Then **restart opencode** (skills load at startup, not hot-reloaded).

## Claude Code

Claude Code uses the same `PROGRESS.md`-style skill format (frontmatter
`name` + `description`, body rules):

```bash
mkdir -p ~/.claude/skills
cp -R opencode/sys-spec ~/.claude/skills/
```

Or per-project: `PROJECT_ROOT/.claude/skills/sys-spec/SKILL.md`.

Note: opencode also auto-discovers `~/.claude/skills/`, so this single install
serves both opencode and Claude Code.

## Cursor

Cursor has no skill loader; it uses rules files. Convert the skill body into a
rule under project rules:

```bash
mkdir -p .cursor/rules
cp opencode/sys-spec/SKILL.md .cursor/rules/sys-spec.mdc
```

The `.mdc` rule must keep frontmatter `description` (used for matching), then
the rule body carries the discipline. Rules auto-apply on matching prompts.

## Generic agents (no skill loader)

Tools that only read plain instruction files (AGENTS.md, CLAUDE.md, rules):

```bash
mkdir -p .agents/skills
cp -R opencode/sys-spec ~/.agents/skills/
```

`.agents/skills/` is auto-loaded by opencode too. For tools with no skills or
`.agents/` scan, append the contents of `SKILL.md` to your project `AGENTS.md`.

## Grok (xAI)

Grok Code reads `AGENTS.md` as its instruction file — there is no skill loader,
so the AGENTS.md route is the only one. Put the discipline in a project-level
`AGENTS.md` (or `~/.grok/AGENTS.md` for global):

```bash
cp opencode/sys-spec/SKILL.md AGENTS.md
```

If you have other global instructions, append `SKILL.md` contents instead of
overwriting.

## OpenAI (Codex)

`openai/codex` also reads `AGENTS.md` for project context. Same approach:

```bash
cp opencode/sys-spec/SKILL.md AGENTS.md         # project-wide
# or ~/.codex/AGENTS.md for every project
```

Nothing to restart — codex reads AGENTS.md per run.

## Local model servers (Ollama, LM Studio, KoboldCPP)

These aren't agents with instruction-file loaders — they serve models over an
OpenAI-compatible API, so the discipline is injected as the **system prompt**
(not a skill file). Two ways:

**1. Ollama — bake it into a model via Modelfile**

Strip the YAML frontmatter from `SKILL.md`, keep only the body, and set it as
the system prompt:

```
FROM llama3
SYSTEM """
The user wants to build a system. Follow the SYS discipline:
(contents of SKILL.md without the leading --- name/description ---)
"""
```

```bash
ollama create sys-spec -f Modelfile
ollama run sys-spec
```

**2. LM Studio / KoboldCPP — paste into the system prompt field**

- LM Studio: open a chat, set **System Prompt** to the `SKILL.md` body (frontmatter stripped). No persistent file install; re-add per-preset or save as a preset.
- KoboldCPP: set the Prompt/context template's system section to the body, or run it purely as an opencode backend (OpenAI-compatible URL) and let the agent's `AGENTS.md` carry the discipline instead.

In all three, the discipline is only as durable as your prompt preset — for
authored code, prefer hooking them as backends under opencode/Claude Code and
using the skill or AGENTS.md path above.

## Verify it loaded

Ask the agent:

> build a system that classifies tickets and drafts replies

It should reply with a `lint:` line (anthropomorphism check), the
`IN/OUT/STATE/MAP/OBJ/C/FAIL/EVAL` spec, and ask the user to fill any
unspecified slot instead of guessing.

Still no trigger? The file must be named exactly `SKILL.md` (or the vendor's
required extension) and its frontmatter `name` must match the folder (`sys-spec`).

## Closing the loop with `verify`

The skill produces the spec; `syslang verify` checks the spec's symbols against
real source, so speculative slots get flagged before coding:

```bash
python3 run.py verify <spec.md> <source|dir>
```

Exits non-zero when any symbol in the spec is missing from the code.