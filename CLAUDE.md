# brian2models-mcp — Architectural Spec

## What This Is

An MCP server that gives Claude Code access to a searchable library of Brian2
neural simulation models, plus two companion Skills for writing and analyzing
Brian2 simulations.

## Repository Layout

```
brian2models-mcp/
├── skills/
│   ├── brian2_simulation.md     # Skill: idioms, gotchas, units discipline
│   └── simulation_results.md   # Skill: reading monitors, saving results, plotting
├── src/brian2models_mcp/
│   ├── server.py                # MCP boundary: @mcp.tool() decorators only
│   ├── library.py               # Model loading, search, list logic
│   ├── schemas.py               # Pydantic models for all tool inputs/outputs
│   └── cli.py                   # `brian2models seed` and `brian2models rebuild` commands
├── scripts/
│   └── seed_library.py          # Fetches Brian2 examples, writes models.json
├── models/
│   └── .gitkeep                 # Custom user models go here (gitignored content)
└── tests/
    ├── unit/
    └── integration/
```

## Three Tools (server.py)

### search_brian2_models(query: str) -> SearchResult
Returns ALL models (name + docstring). The calling model selects relevant ones.
Does NOT do vector similarity — returns full library and lets CC reason about
relevance. At 30 models this fits easily in context.

### get_model_by_id(model_id: str) -> ModelRecord
Returns complete model: name, docstring, full source code, origin URL, tags.

### list_models() -> list[ModelSummary]
Returns all models as name + one-line description. For orientation at session start.

## Model Storage (~/.brian2_models/)

```
~/.brian2_models/
├── models.json       # List of ModelRecord objects, human-readable, git-diffable
└── custom/           # User-added models (Python files with docstrings)
```

Models are plain JSON — no vector index, no binary artifacts. The calling model
reasons about relevance from docstrings. This scales to ~200 models before context
becomes a concern; at that point embeddings can be added.

## ModelRecord Schema

```python
{
    "id": str,              # slug, e.g. "HH_example"
    "name": str,            # display name
    "docstring": str,       # full docstring — this is what gets searched
    "source": str,          # full Brian2 source code
    "origin_url": str,      # Brian2 docs URL or paper reference
    "tags": list[str],      # loose tags: ["neuron", "HH", "conductance-based"]
}
```

## Seeding

`scripts/seed_library.py` fetches examples from:
  https://brian2.readthedocs.io/en/stable/examples/

Parses docstring and source from each .py file, writes to ~/.brian2_models/models.json.
Requires network access. Idempotent — reruns overwrite existing entries by id.

`brian2models rebuild` re-runs seeding and also picks up any .py files in
~/.brian2_models/custom/ using the same docstring extraction logic.

## Skills

### skills/brian2_simulation.md
Encodes Brian2 idioms CC frequently gets wrong:
- Units discipline (always use Brian2 units, never bare numbers for quantities)
- start_scope() — call at top of every simulation script
- Namespace behavior in run() — explicit namespace={} to avoid stale variable capture
- store()/restore() pattern for parameter sweeps
- Monitor patterns and common pitfalls
- "Always search the model library before writing from scratch"
- Save results to disk before analysis (simulation data is ephemeral otherwise)

### skills/simulation_results.md
Encodes patterns for reading simulation output:
- SpikeMonitor: .t, .i arrays and how to build rasters
- StateMonitor: .t, .v (or other variables) and how to plot traces
- PopulationRateMonitor: smoothing and interpretation
- Canonical save pattern: np.save or pickle to ~/brian2_results/
- Three stereotyped plots: raster, voltage trace, population rate

## Key Design Decisions

1. No embeddings — full library returned to CC, CC reasons about relevance
2. No execution wrapper — CC writes and runs Brian2 scripts in bash directly
3. Tracebacks are acceptable error output — encode common ones in the Skill
4. Skills are bundled in this repo for convenience but are independent markdown
   files — users can use them without installing the MCP
5. Results Skill includes minimal visualization patterns; complex visualization
   is left to CC reasoning
6. No relationship to connectomics-mcp — composition is CC's responsibility

## Session Discipline

Each CC build session should:
1. Read this file first
2. Read TOOL_REGISTRY.md to see current build state
3. Make changes
4. Update TOOL_REGISTRY.md before ending
5. Run pytest before ending

## Done Criteria for v0.1

- [ ] seed_library.py fetches and parses all Brian2 examples
- [ ] All three MCP tools implemented and returning correct schemas
- [ ] `brian2models seed` CLI command works
- [ ] `brian2models rebuild` picks up custom models
- [ ] skills/brian2_simulation.md covers all gotchas listed above
- [ ] skills/simulation_results.md covers monitor patterns and save/plot
- [ ] Unit tests for library.py (mocked models.json)
- [ ] Integration test: seed + search + get roundtrip
