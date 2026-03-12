# brian2models-mcp

A Model Context Protocol (MCP) server that gives Claude Code access to a searchable library of Brian2 neural simulation models. Built for computational neuroscientists who want to use agentic AI tools for simulation workflows without starting from scratch every session.

## Prerequisites

- Python 3.11+
- [Brian2](https://brian2.readthedocs.io) (`pip install brian2`)
- An MCP-aware agent (Claude Code, or any client supporting MCP)

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

Search the library and retrieve source code:
> Search for a balanced excitatory-inhibitory network model, then get the full source for the closest match

Adapt an existing model:
> Find a Hodgkin-Huxley example in the library and modify it to use AdEx dynamics instead, keeping the same network structure

Full workflow from library to figure:
> Using the CUBA model as a starting point, scale it to 5000 neurons, run for 2 seconds, save results, and plot a raster and population rate

## Skills

The `skills/` directory contains two companion Skills for Claude Code:

- **brian2_simulation.md** — Brian2 idioms, units discipline, `start_scope()`, namespace behavior, `store()`/`restore()`, and common error fixes
- **simulation_results.md** — Reading SpikeMonitor/StateMonitor/PopulationRateMonitor, saving results, and canonical plot patterns

To use a skill, start your Claude Code session with:
> Read skills/brian2_simulation.md before we begin

Or add the skills directory to your project's `CLAUDE.md` so they load automatically.

Skills are standalone markdown files — they can be used independently of the MCP server.

## Acknowledgments

Model library seeded from the [Brian2 examples](https://brian2.readthedocs.io/en/stable/examples/) maintained by the Brian2 development team. If you use Brian2 in your research, please cite [Stimberg et al. 2019](https://elifesciences.org/articles/47314).
