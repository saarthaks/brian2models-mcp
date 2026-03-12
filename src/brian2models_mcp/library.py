import json
from pathlib import Path

from .schemas import ModelRecord, ModelSummary, SearchResult

LIBRARY_DIR = Path.home() / ".brian2_models"
MODELS_FILE = LIBRARY_DIR / "models.json"
CUSTOM_DIR = LIBRARY_DIR / "custom"


def load_models() -> list[ModelRecord]:
    """Read models.json and return a list of ModelRecord objects.

    Returns an empty list if the file does not exist or is unreadable.
    """
    if not MODELS_FILE.exists():
        return []
    data = json.loads(MODELS_FILE.read_text(encoding="utf-8"))
    return [ModelRecord(**m) for m in data]


def get_model_by_id(model_id: str) -> ModelRecord | None:
    """Return a single ModelRecord by its id, or None if not found."""
    for model in load_models():
        if model.id == model_id:
            return model
    return None


def list_models() -> list[ModelSummary]:
    """Return all models as ModelSummary (id, name, one-line description)."""
    summaries = []
    for m in load_models():
        first_line = ""
        for line in m.docstring.splitlines():
            stripped = line.strip()
            if stripped:
                first_line = stripped
                break
        summaries.append(
            ModelSummary(id=m.id, name=m.name, one_line_description=first_line)
        )
    return summaries


def search_models(query: str) -> SearchResult:
    """Return ALL models as summaries for the given query.

    This function does NOT filter or rank models. It returns the complete
    library as ModelSummary objects (id, name, one_line_description) so that
    the caller can select relevant models and fetch full source via
    get_model_by_id().
    """
    summaries = list_models()
    return SearchResult(query=query, models=summaries, total_count=len(summaries))
