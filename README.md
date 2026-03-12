# brian2models-mcp

An MCP server that gives Claude Code access to a searchable library of Brian2 neural simulation models, plus two companion Skills for writing and analyzing simulations.

## Install

```bash
pip install -e .
brian2models seed
```

The `seed` command fetches all Brian2 examples from the official documentation and writes them to `~/.brian2_models/models.json`. Run `brian2models rebuild` at any time to refresh.

Custom models can be added as `.py` files (with docstrings) in `~/.brian2_models/custom/` — they'll be picked up on the next rebuild.

## Configure with Claude Code

Add to your Claude Code MCP config (`.claude/settings.json` or project settings):

```json
{
  "mcpServers": {
    "brian2models": {
      "command": "brian2models-mcp"
    }
  }
}
```

## Example Prompts

```
> Search the Brian2 model library for Hodgkin-Huxley examples and show me the source

> Write a simulation of 1000 LIF neurons with random connectivity, using an example from the library as a starting point

> Run my CUBA simulation, save the results, and plot a raster diagram
```

## Skills

The `skills/` directory contains two companion Skills for Claude Code:

- **brian2_simulation.md** — Brian2 idioms, units discipline, `start_scope()`, namespace behavior, `store()`/`restore()`, and common error fixes
- **simulation_results.md** — Reading SpikeMonitor/StateMonitor/PopulationRateMonitor, saving results, and canonical plot patterns

These are standalone markdown files that can be used independently of the MCP server.
