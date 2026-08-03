# AGENTS.md

## Overview

This repository is a curated collection of useful skills discovered on GitHub. Each skill is packaged as a **git submodule** at the project root directory.

## Structure

```
.
├── <skill-name>/    # git submodule pointing to an external repo
├── AGENTS.md
└── README.md
```

Each subdirectory at the project root is an independent git repository tracked as a submodule. The root repo pins each submodule to a specific commit via `.gitmodules` and the git tree.

## Conventions

- **One skill per submodule.** Each submodule maps to one GitHub repo.
- **Submodule path:** `<skill-name>` at the project root (no nested directory).
- **Directory naming:** When adding a submodule, the user provides the target directory name. If not provided, ask the user for the name before proceeding.
- **Branch tracking:** Each submodule MUST track the upstream repo's default branch (typically `main`). Use `git submodule add -b main` when adding.
- **Do not fork into this repo.** Keep skills as submodules — do not copy files directly.
- **Update README.md & Check Duplicates:** Every newly added skill MUST be registered in `README.md` under the appropriate category table, and checked for any duplicate entries.

## Adding a New Skill

When the user provides a GitHub URL:
1. If a directory name is provided, use it as the submodule path.
2. If no directory name is provided, **ask the user** for the desired directory name before running the command.
3. **Update `README.md`**: Add the new skill to `README.md` under the appropriate category with its path and description, ensuring no duplicate entries exist.

```bash
git submodule add -b main <github-repo-url> <directory-name>
git commit -m "Add skill: <directory-name>"

# Update README.md and commit the README update
git commit -am "Update README.md with new skill: <directory-name>"
```

## Updating Skills

```bash
# Update a single submodule
cd <skill-name> && git pull && cd ..
git add <skill-name>
git commit -m "Update skill: <skill-name>"

# Update all submodules
git submodule update --remote --merge
git commit -am "Update all skills"
```

## Cloning

```bash
git clone --recurse-submodules <repo-url>

# Or if already cloned:
git submodule update --init --recursive
```
