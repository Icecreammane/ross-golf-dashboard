# Projects - Nightly Builds

Each night, Jarvis picks a project from `IDEAS.md` and builds something testable.

## Directory Structure

```
projects/
├── YYYY-MM-DD-project-name/
│   ├── README.md           # What it does, how to use it
│   ├── HANDOFF.md          # Morning handoff doc for Ross
│   ├── src/                # Source code
│   ├── tests/              # Tests (if applicable)
│   └── examples/           # Usage examples
```

## Nightly Build Process

1. **11:00pm** - Review day, check task queue
2. **11:30pm** - Start building
3. **6:00am** - Document & stage
4. **7:30am** - Send morning brief to Ross

## Rules

- ✅ All code staged (never committed)
- ✅ Test environments only
- ✅ Include clear testing instructions
- ❌ No deletions
- ❌ No live deployments
- ❌ No git pushes

## Testing Projects

Each project includes a HANDOFF.md with step-by-step testing instructions.

To test a project:
```bash
cd projects/YYYY-MM-DD-project-name
cat HANDOFF.md
# Follow the testing instructions
```

## Approving Projects

If you like a project:
1. Review the code
2. Test it
3. Commit & push when ready
4. Jarvis will note which projects got shipped

If you don't like it:
1. Leave feedback in a comment or message
2. Jarvis will iterate or move on

---

*First nightly build: Tonight (2026-02-01)*
