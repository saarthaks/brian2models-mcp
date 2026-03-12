# Kickstart Prompt — Session 1

Paste this into a new Claude Code session from inside the brian2models-mcp directory.

---

Read CLAUDE.md and TOOL_REGISTRY.md before doing anything else.

This session builds the complete brian2models-mcp package from scratch. Work through
the following phases in order. After each phase, run pytest and confirm tests pass
before moving to the next.

---

## Phase 1: Core infrastructure

Build these files:

**src/brian2models_mcp/schemas.py**
Pydantic models:
- `ModelRecord`: id, name, docstring, source, origin_url, tags (list[str])
- `ModelSummary`: id, name, one_line_description (first line of docstring)
- `SearchResult`: query (str), models (list[ModelRecord]), total_count (int)

**src/brian2models_mcp/library.py**
- `LIBRARY_DIR = Path.home() / ".brian2_models"`
- `MODELS_FILE = LIBRARY_DIR / "models.json"`
- `CUSTOM_DIR = LIBRARY_DIR / "custom"`
- `load_models() -> list[ModelRecord]`: reads models.json, returns [] if not found
- `get_model_by_id(model_id: str) -> ModelRecord | None`
- `list_models() -> list[ModelSummary]`
- `search_models(query: str) -> SearchResult`: returns ALL models — do not filter.
  The docstring on this function must clearly state that the caller is responsible
  for selecting relevant models from the returned list.

**tests/unit/test_library.py**
Test load_models with a fixture models.json containing 2-3 mock ModelRecords.
Test get_model_by_id found and not-found cases.
Test list_models returns correct ModelSummary fields.
Test search_models returns all models regardless of query string.

---

## Phase 2: Seeding script

**scripts/seed_library.py**

Fetches all Brian2 examples from https://brian2.readthedocs.io/en/stable/examples/

Strategy:
1. GET the examples index page, parse all example links
2. For each example, fetch the raw .py source from the Brian2 GitHub repo:
   https://raw.githubusercontent.com/brian-team/brian2/master/examples/{name}.py
3. Extract docstring (everything between the opening triple-quote and closing
   triple-quote at the top of the file)
4. Extract one_line_description as first non-empty line of docstring
5. Generate id as the filename without .py, with slashes replaced by underscores
   e.g. "CUBA" → "CUBA", "frompapers/Brunel_Hakim_1999" → "frompapers_Brunel_Hakim_1999"
6. Write all records to ~/.brian2_models/models.json

Also handle custom models:
- Scan ~/.brian2_models/custom/ for .py files
- Apply same docstring extraction
- Set origin_url to "custom"
- Merge into models.json (custom models take precedence by id)

The script should be idempotent — reruns overwrite existing entries.
Print a summary on completion: N models seeded, M custom models found.

---

## Phase 3: CLI

**src/brian2models_mcp/cli.py**

Two commands using argparse:
- `brian2models seed`: runs the seeding script logic
- `brian2models rebuild`: same as seed (alias for clarity)

Both should print progress and a completion summary.

Entry point is already defined in pyproject.toml as:
  brian2models = "brian2models_mcp.cli:main"

---

## Phase 4: MCP server

**src/brian2models_mcp/server.py**

```python
from fastmcp import FastMCP
from .library import load_models, get_model_by_id, list_models, search_models
from .schemas import ModelRecord, ModelSummary, SearchResult

mcp = FastMCP("brian2models")

@mcp.tool()
def search_brian2_models(query: str) -> SearchResult:
    """
    Search the Brian2 model library. Returns ALL models with their full docstrings.
    YOU (the calling model) are responsible for reading the docstrings and selecting
    the models most relevant to the query. Do not assume this function filters for you.
    Always call this before writing a Brian2 model from scratch.
    """
    return search_models(query)

@mcp.tool()
def get_model_by_id(model_id: str) -> ModelRecord:
    """
    Retrieve a specific model's complete source code by its id.
    Use list_models() or search_brian2_models() first to find the correct id.
    """
    model = get_model_by_id(model_id)
    if model is None:
        raise ValueError(f"Model '{model_id}' not found. Use list_models() to see available models.")
    return model

@mcp.tool()
def list_models() -> list[ModelSummary]:
    """
    List all models in the library with their one-line descriptions.
    Use this at the start of a session to orient yourself before searching.
    """
    return list_models()

def main():
    mcp.run()
```

**src/brian2models_mcp/__init__.py**
Empty or minimal version import.

---

## Phase 5: Skills

**skills/brian2_simulation.md**

Write this skill from scratch based on your knowledge of Brian2. It should cover:

1. **Always search the library first** — call list_models() to orient, then
   search_brian2_models() before writing any model from scratch
2. **start_scope()** — must be called at the top of every simulation script to
   reset Brian2's internal state. Forgetting this causes state leakage between
   simulations in the same Python session.
3. **Units discipline** — every quantity with physical units must use Brian2 units.
   `10` is wrong, `10*ms` is correct. `v = -65` is wrong, `v = -65*mV` is correct.
   Bare numbers for dimensioned quantities silently produce wrong results.
4. **Namespace behavior in run()** — Brian2 captures variable values at run() time,
   not at definition time. For parameter sweeps, always pass explicit namespace:
   `run(duration, namespace={'param': value})` to avoid stale captures.
5. **store()/restore()** — use for parameter sweeps to avoid re-running network
   construction. `net.store()` before the sweep, `net.restore()` at the top of
   each iteration.
6. **Saving results** — always save monitor data to disk before analysis.
   Simulation objects are not persistent. Use:
   ```python
   import numpy as np
   from pathlib import Path
   outdir = Path.home() / "brian2_results"
   outdir.mkdir(exist_ok=True)
   np.save(outdir / "spike_times.npy", spike_mon.t/ms)
   np.save(outdir / "spike_ids.npy", spike_mon.i)
   ```
7. **Common tracebacks** — document the 3-4 most common Brian2 errors and their fixes:
   - DimensionMismatchError: units mismatch, check every quantity
   - "Variable X not found in namespace": use explicit namespace={} in run()
   - RecursionError during code generation: usually a circular equation reference

**skills/simulation_results.md**

Write this skill covering:

1. **SpikeMonitor** — .t (spike times, has units), .i (neuron indices, no units).
   To get arrays: `spike_times = spike_mon.t/ms` (converts to float array in ms)
2. **StateMonitor** — .t (time array), .v[i] (variable for neuron i).
   Always divide by units when plotting: `plt.plot(state_mon.t/ms, state_mon.v[0]/mV)`
3. **PopulationRateMonitor** — .t, .rate. Smooth with:
   `from brian2 import *; smooth_rate(pop_mon, kernel='gaussian', width=1*ms)`
4. **Loading saved results**:
   ```python
   spike_times = np.load("~/brian2_results/spike_times.npy")
   spike_ids = np.load("~/brian2_results/spike_ids.npy")
   ```
5. **Three canonical plots** with minimal working code:
   - Raster plot: plt.plot(spike_times, spike_ids, '.k', markersize=2)
   - Voltage trace: plt.plot(t_array, v_array) for a single neuron
   - Population rate: plt.plot(t_array, rate_array)
6. **Figure saving**: always save to ~/brian2_results/ with a descriptive filename

---

## Phase 6: Wrap-up

1. Run the full test suite: `pytest tests/ -v`
2. Run integration test manually: `python scripts/seed_library.py`
   Confirm models.json is written to ~/.brian2_models/
3. Update TOOL_REGISTRY.md — mark all completed items ✅
4. Write a minimal README.md:
   - One paragraph description
   - Install: `pip install -e .` then `brian2models seed`
   - Claude Code config snippet (same pattern as connectomics-mcp)
   - Three example CC prompts showing the MCP in use
   - Note that skills/ directory contains companion Skills for CC

---

When done, report:
- How many Brian2 examples were successfully seeded
- Any examples that failed to parse and why
- pytest results
- Any architectural decisions that deviated from CLAUDE.md and why
