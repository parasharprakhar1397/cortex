<!-- managed:linked-repos -->
## Linked Repositories
- parasharprakhar1397/cortex
<!-- /managed:linked-repos -->

# Cortex — Team Code Workflow

This is the team's living reference for how code work gets done. The lead updates it
whenever the owner changes review/merge policy. All engineers read and follow it.

## Repositories
- Primary: `parasharprakhar1397/cortex` (https://github.com/parasharprakhar1397/cortex)
- Local working tree (shared, single): `/home/team/shared/cortex`
- Remote `origin` is configured and tracked on `main`.

## Golden rules
1. **One write tree, serialized writes.** All code delegations share
   `/home/team/shared/cortex`. Only one write-capable delegation runs at a time, so each
   new task starts from whatever state the previous task left. Never assume the tree is
   at some earlier point.
2. **Always start from a clean, up-to-date tree.** Before writing code: `git checkout main`,
   `git pull --ff-only origin main`, `git status` must be clean.
3. **Work on a feature branch.** Create `git checkout -b <task-id>-<short-slug>` for each
   task (e.g. `0.3-auth`, `1.1-razorpay-auth`).
4. **Open a pull request when done.** Push the branch and open a PR against `main`
   (via `gh` or `finish_task`). The lead reviews and merges; do NOT merge your own PR.
5. **Leave the tree clean and on `main` when finished.** `git checkout main`, and clean up
   any build artifacts/untracked files you created (except intended source files). A dirty
   or mid-branch tree breaks the next delegation.
6. **Read project conventions first.** Every repo may contain `CLAUDE.md` / `AGENTS.md`.
   Read and follow them before touching code.

## Repo layout
```
cortex/
├── api/            # FastAPI backend (Python)
│   ├── app/        # app code (config, db, auth, routers)
│   ├── db/         # database layer (engine, tenant schema, migrations)
│   ├── alembic/    # migrations
│   └── tests/      # pytest
├── ui/             # React + Vite + Tailwind frontend (added in Task 0.4)
├── docker-compose.yml  # api + postgres + redis
└── Dockerfile
```

## Commands & environment notes
- Docker requires `sudo` in this sandbox (e.g. `sudo docker compose up -d`).
- Backend deps: `cd api && pip install -r requirements.txt`.
- Run tests: `cd api && pytest`.
- CI runs on push via `.github/workflows/ci.yml`.

## Merge policy
- Lead merges PRs with the `merge_pr` tool (squash by default).
- A PR must not break CI. Confirm tests pass before opening.
