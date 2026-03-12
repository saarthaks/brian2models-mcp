# Tool Registry — Build State

## MCP Tools

| Tool | Status | Schema | Tests |
|------|--------|--------|-------|
| search_brian2_models | ✅ Complete | SearchResult | unit |
| get_brian2_model_by_id | ✅ Complete | ModelRecord | unit |
| list_brian2_models | ✅ Complete | list[ModelSummary] | unit |

## CLI Commands

| Command | Status |
|---------|--------|
| brian2models seed | ✅ Complete |
| brian2models rebuild | ✅ Complete |

## Skills

| File | Status | Sections |
|------|--------|----------|
| skills/brian2_simulation.md | ✅ Complete | library search, start_scope, units, namespace, store/restore, saving, tracebacks |
| skills/simulation_results.md | ✅ Complete | SpikeMonitor, StateMonitor, PopulationRateMonitor, loading, 3 plots, figure saving |

## Infrastructure

| Component | Status |
|-----------|--------|
| schemas.py | ✅ Complete |
| library.py | ✅ Complete |
| seeder.py | ✅ Complete |
| server.py | ✅ Complete |
| cli.py | ✅ Complete |
| scripts/seed_library.py | ✅ Complete |

## Status Key
- 📋 Not started
- 🔧 In progress
- ✅ Complete
- ❌ Broken — needs fix

## Decisions Log

- Seeder logic lives in `src/brian2models_mcp/seeder.py` (importable module), with `scripts/seed_library.py` as a thin standalone wrapper. This avoids fragile path manipulation in cli.py.
- Server tool functions use `_` prefixed imports to avoid name collisions with the `@mcp.tool()` decorated functions.
- Brian2 docs use dots as path separators (e.g. `frompapers.Brette_2012.Fig1.html`), GitHub uses slashes. Seeder converts dots→slashes for fetching, slashes→dots for docs URLs.
- Non-Python resources (.npy, .txt, .md, .mplstyle) filtered out during link parsing — 100 of 108 links are actual Python examples.
