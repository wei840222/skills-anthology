# Path Pattern Analysis for clawic-skills

## Overview

Analyzed 961 SKILL.md files in `clawic-skills/skills/*/SKILL.md`.
483 skills contain at least one path reference.

## Path Categories Found

### 1. Tilde Workspace Paths (`~/skillname/`) — DOMINANT (2011 matches)

The primary path pattern. Every skill uses `~/skillname/` as its data/workspace root.

**Sub-patterns:**

| Sub-pattern | Count | Example | Context |
|---|---|---|---|
| Workspace dir | 679 | `~/games/` | "Create `~/games/` as workspace" |
| Workspace file | 205 | `~/games/video/backlog.md` | "Log to `~/games/video/backlog.md`" |
| Hidden config dir | 39 | `~/.austin/`, `~/.ssh/` | "Memory lives in `~/.austin/`" |
| System path | 7 | `~/Library/LaunchAgents/` | macOS-specific paths |
| In code blocks | 423 | `~/academy/` inside ``` fences | Directory tree listings |
| In prose | 481 | `~/academy/` in text | Instructions and descriptions |
| Frontmatter configPaths | 69 | `"configPaths":["~/academy/"]` | Metadata JSON |
| Frontmatter other | 108 | `"config":["~/codex/"]` | Metadata JSON requires.config |

**Conversion target:** `~/skillname/` → `./skillname/` (relative to skill install dir)

**Special cases — workspace dir name ≠ skill name (15 skills):**
- `act-prep` → `~/act/`
- `contract` → `~/contracts/`
- `course` → `~/courses/`
- `daily-planner` → `~/planner/`
- `documents` → `~/docs/`
- `exam` → `~/exams/`
- `influencer` → `~/influencers/`
- `invoice` → `~/billing/`
- `movie` → `~/movies/<project>/`
- `people` → `~/contacts/`
- `pkm` → `~/kb/`
- `podcast` → `~/podcasts/<show>/`
- `recipe` → `~/recipes/`
- `sentiment-tracker` → `~/sentiment-analysis/`
- `song` → `~/songs/`

### 2. Relative Dot Paths (`./...`) — 35 matches

Already relative. Used for project-level config files:
- `./AGENTS.md` (referenced by auto-update, discover, jarvis, proactivity, self-criticism, self-improving)
- `./SOUL.md` (her, auto-update, discover, jarvis, proactivity, self-criticism, self-improving)
- `./TOOLS.md` (proactivity)
- `./HEARTBEAT.md` (discover, jarvis, proactivity, self-improving)
- `./src/` (storybook, tailwindcss, vite)
- `./scripts/init-workspace.sh` (write)
- `./ticketmaster.sh` (ticketmaster)

**Conversion target:** No change needed — already relative.

### 3. Absolute System Paths (`/etc/...`, `/var/...`) — 28 matches

System configuration paths, NOT user data:
- `/etc/ansible/facts.d/*.fact`
- `/etc/caddy/Caddyfile`
- `/etc/hosts`, `/etc/ssh/sshd_config`
- `/var/log/nginx/error.log`, `/var/log/auth.log`
- `/etc/letsencrypt/live/...`
- `/Users/alex/projects/webapp` (example in folders skill)

**Conversion target:** Do NOT rewrite — these are system paths, not user workspace.

### 4. Environment Variable Paths (`$VAR`) — 131 matches

API keys, tokens, and URL templates:
- `$GROQ_API_KEY`, `$STRIPE_SECRET_KEY`, `$NOTION_API_KEY`
- `$SF_INSTANCE_URL/services/data/v59.0/...`

**Conversion target:** Do NOT rewrite — these are not filesystem paths.

### 5. Windows Paths (`C:\...`) — 4 matches

- `C:\Windows` (in files and folders skills)

**Conversion target:** Do NOT rewrite — system paths.

### 6. Parent Relative Paths (`../...`) — 3 matches

- `../young-adult/` (face skill — relative to skill dir)
- `../src/` (storybook — relative to project)

**Conversion target:** Do NOT rewrite — already relative.

### 7. URL/API Paths — many matches (excluded from analysis)

Paths like `/api/v1/models`, `/rest/agile/1.0`, `/topstories.json` are URL path components, not filesystem paths.

**Conversion target:** Do NOT rewrite.

## Summary for Conversion Script

### What to rewrite:
1. `~/<dirname>/` → `./<dirname>/` (workspace directories)
2. `~/<dirname>/<file>` → `./<dirname>/<file>` (workspace files)
3. `~/.<hidden>/` → `./.<hidden>/` (hidden config dirs like `~/.austin/`)

### What NOT to rewrite:
1. Absolute system paths (`/etc/`, `/var/`, `/usr/`, etc.)
2. Environment variables (`$VAR`, `${VAR}`)
3. URL paths (`/api/...`, `/rest/...`)
4. Windows paths (`C:\...`)
5. Already-relative paths (`./...`, `../...`)

### Rewrite rules (regex):
```
~/([a-zA-Z][a-zA-Z0-9_-]*/)  →  ./$1
~/([a-zA-Z][a-zA-Z0-9_-]*/[^\s`"'`,;:)]+)  →  ./$1
~/\.[a-zA-Z][a-zA-Z0-9_.-]*/  →  ./.$1  (hidden dirs)
```

### Occurrences in frontmatter vs body:
- Frontmatter `configPaths` / `config`: ~177 matches
- Body (prose + code blocks): ~1789 matches
- Both need rewriting for full portability

### File format notes:
- Frontmatter is YAML with embedded JSON in `metadata:` field
- Paths appear in JSON strings: `"configPaths":["~/skillname/"]`
- Body paths are usually in backtick code spans: `` `~/skillname/` ``
- Some paths appear in markdown code blocks (``` fences)
- Tree diagrams use `~/skillname/` as root
