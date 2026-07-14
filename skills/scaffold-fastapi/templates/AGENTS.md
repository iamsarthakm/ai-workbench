# Engineering — AI Coding Rules

## Communication
- Be direct, no fluff
- Present options with trade-offs; let the user decide
- If unsure, ask rather than assume

## Philosophy
- **No overengineering** — keep it simple, appropriate for project scale; don't add what isn't needed now
- **Practical over perfect** — trade-offs are acceptable; don't chase perfection over delivery
- **Senior mindset** — thorough code reviews; favour simplicity and balanced trade-offs
- **Prefer the proper way** — use tool-supported workflows where possible; hand-write only when tooling can't produce it

## Code
- Follow solid language and framework conventions
- No unnecessary file splits — only split when it clearly improves readability
- Remove unused code; don't comment it out

## Tooling
- Prefer mainstream, well-supported tools; add a new one only when it clearly pays off
- **FOSS first** — prefer open-source tools and licenses; note when something proprietary is required
- Prefer existing solutions over bespoke implementations
- **Docker:** start the daemon before building/pushing — `open -a Docker` on macOS, `sudo systemctl start docker` on Linux

## Documentation
- Keep docs concise and actionable
- **Single source of truth** — link to canonical docs; don't duplicate content that will drift
- Keep tests and README in sync when behaviour changes
- **Before releasing or deploying:** (1) sync tests, docs, README, trim redundancy; (2) confirm any new env vars or secrets with the user; (3) summarise and confirm before release steps

## Git
- **Protected `main`** — use a branch and open a PR; merge after review (don't push directly, including image-tag-only bumps)
- **After merge:** pull main, delete the merged local branch, `git fetch --prune`; delete the remote branch if not auto-deleted
- **Branch hygiene** — periodically prune stale remote-tracking refs (`git fetch --prune`) and merged local branches (e.g., `git branch --merged | grep -E -v '^\*|main|master|dev' | xargs git branch -d` on Linux/macOS).
- **Commits** — batch related changes into meaningful commits by context; commit when there's a coherent set or when asked
- Before committing, update docs/tests/tooling if the change affects them
- Note manual follow-ups in commit or PR text (e.g. "run migration", "update .env")
- **Deploy vs protected `main`** — ask the user to merge the PR first, then do cluster steps; only skip merge-first if they explicitly ask

## Cloud & Security
- Prefer short-lived, scoped credentials (workload identity, ADC, impersonation) over long-lived service account keys
- Org policy discourages long-lived service account tokens/keys; avoid when another auth method works
- Never hardcode secrets or credentials; always use environment variables or a secrets manager
