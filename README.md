# ai-workbench

A personal collection of [Claude Code](https://claude.com/claude-code) skills and agents — reusable, versioned automation that Claude can run on demand, instead of re-explaining the same workflow every time.

## What's in here

```
skills/
  scaffold-fastapi/   # Scaffold a production-ready FastAPI service
```

Each skill is a self-contained folder under `skills/` with a `SKILL.md` describing what it does and how to run it, plus any supporting templates/scripts it needs.

## Using these skills with Claude Code

Claude Code loads skills from two places:

- `~/.claude/skills/` — available in every project (personal, global)
- `<project>/.claude/skills/` — available only in that project (shared with a team via git)

To use a skill from this repo, copy (or symlink) it into one of those folders.

### Copy a single skill (global, all projects)

```bash
mkdir -p ~/.claude/skills
cp -R skills/scaffold-fastapi ~/.claude/skills/
```

### Copy a single skill (project-local)

```bash
mkdir -p /path/to/your-project/.claude/skills
cp -R skills/scaffold-fastapi /path/to/your-project/.claude/skills/
```

### Copy all skills at once

```bash
mkdir -p ~/.claude/skills
cp -R skills/* ~/.claude/skills/
```

### Symlink instead of copy (keeps skills updated when this repo changes)

```bash
mkdir -p ~/.claude/skills
ln -s "$(pwd)/skills/scaffold-fastapi" ~/.claude/skills/scaffold-fastapi
```

### Invoke a skill

Once copied, restart Claude Code (or start a new session) and invoke the skill by name as a slash command:

```
/scaffold-fastapi
```

Claude will read the skill's `SKILL.md` and follow its steps, asking you for any inputs it needs along the way.

## Adding a new skill

1. Create a new folder under `skills/<skill-name>/`.
2. Add a `SKILL.md` with YAML frontmatter (`name`, `description`) followed by instructions Claude can follow step by step.
3. Put any templates, scripts, or reference files the skill needs alongside it.
4. Copy it into `~/.claude/skills/` or `<project>/.claude/skills/` to try it out.

## License

See [LICENSE](LICENSE).
