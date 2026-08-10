from __future__ import annotations

from .safety import SafeContext


def _context_block(context: SafeContext) -> str:
    files = "\n".join(f"- {path}" for path in context.changed_files) or "- (status only)"
    diff = context.diff or "(git diff text is empty; rely on status and filenames)"
    return f"""Changed files:\n{files}\n\nGit status:\n{context.status}\n\nGit diff:\n{diff}"""


def build_commit_prompt(context: SafeContext) -> str:
    return f"""You write a Git commit draft from the supplied Git context.
Use only facts supported by the context. Do not invent tests or behavior.

Output contract (plain text, no Markdown fence):
TITLE: <one line, maximum 72 characters; 50 or fewer preferred>
BODY:
- <1 concise bullet describing a key change or naming a changed module/file>
- <optional second concise bullet>

Requirements:
- TITLE must be exactly one line.
- BODY must contain 1-2 bullets.
- Mention at least one changed file/module or a concrete change visible in the diff.

{_context_block(context)}
"""


def build_pr_prompt(context: SafeContext) -> str:
    return f"""You write a Pull Request draft from the supplied Git context.
Use only facts supported by the context. Do not invent tests or motivation.

Output contract (plain text, no Markdown fence):
PR_TITLE: <one line, maximum 80 characters>
PR_BODY:
## Why
- <at least one bullet; if the reason is absent from Git context, state that the author must confirm it>
## What
- <at least one bullet>
## How to Test
- <at least one bullet; if tests are unknown, state what a reviewer should verify>

Requirements:
- PR_TITLE must be exactly one line.
- Keep the three section headers exactly as shown.
- Every section must contain at least one '-' bullet.

{_context_block(context)}
"""


def build_repair_prompt(kind: str, previous: str, error: str) -> str:
    if kind == "commit":
        contract = "TITLE: one line <=72 chars; BODY: followed by 1-2 '-' bullets"
    else:
        contract = (
            "PR_TITLE: one line <=80 chars; PR_BODY: with exact ## Why, ## What, "
            "## How to Test headers and at least one '-' bullet under each"
        )
    return f"""Repair the following AI-generated {kind} draft so it strictly satisfies this contract:
{contract}
Do not add unsupported facts. Return only the repaired draft.

Validation error: {error}

Previous draft:
{previous}
"""
