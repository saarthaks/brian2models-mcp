"""MCP server exposing Brian2 model library tools."""

from mcp.server.fastmcp import FastMCP

from .library import get_model_by_id as _get_model_by_id
from .library import list_models as _list_models
from .library import search_models as _search_models
from .schemas import ModelRecord, ModelSummary

mcp = FastMCP("brian2models")


@mcp.tool()
def search_brian2_models(query: str) -> list[ModelSummary]:
    """Search the Brian2 model library. Returns model summaries only (id, name, one-line description).

    Call get_brian2_model_by_id() to retrieve full source code for a specific model.
    Always call this before writing a Brian2 model from scratch.
    """
    result = _search_models(query)
    return result.models


@mcp.tool()
def get_brian2_model_by_id(model_id: str) -> ModelRecord:
    """Retrieve a specific model's complete source code by its id.

    Use list_brian2_models() or search_brian2_models() first to find the correct id.
    """
    model = _get_model_by_id(model_id)
    if model is None:
        raise ValueError(
            f"Model '{model_id}' not found. Use list_brian2_models() to see available models."
        )
    return model


@mcp.tool()
def list_brian2_models() -> list[ModelSummary]:
    """List all models in the library with their one-line descriptions.

    Use this at the start of a session to orient yourself before searching.
    """
    return _list_models()


def main():
    mcp.run()
