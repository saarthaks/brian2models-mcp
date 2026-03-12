import json
from pathlib import Path

import pytest

from brian2models_mcp.schemas import ModelRecord

SAMPLE_MODELS = [
    {
        "id": "HH_example",
        "name": "Hodgkin-Huxley Example",
        "docstring": "Hodgkin-Huxley model of action potential generation.\n\nDemonstrates conductance-based neuron model.",
        "source": "from brian2 import *\n# HH model source",
        "origin_url": "https://brian2.readthedocs.io/en/stable/examples/HH_example.html",
        "tags": ["neuron", "HH", "conductance-based"],
    },
    {
        "id": "CUBA",
        "name": "CUBA",
        "docstring": "Current-based synapses example.\n\nA network of excitatory and inhibitory neurons.",
        "source": "from brian2 import *\n# CUBA source",
        "origin_url": "https://brian2.readthedocs.io/en/stable/examples/CUBA.html",
        "tags": ["network", "synapses", "current-based"],
    },
    {
        "id": "IF_curve",
        "name": "IF Curve",
        "docstring": "Compute the I-F curve of a LIF neuron.\n\nShows firing rate as a function of input current.",
        "source": "from brian2 import *\n# IF curve source",
        "origin_url": "https://brian2.readthedocs.io/en/stable/examples/IF_curve.html",
        "tags": ["neuron", "LIF", "f-I curve"],
    },
]


@pytest.fixture()
def models_dir(tmp_path, monkeypatch):
    """Create a temporary models.json and patch library paths."""
    import brian2models_mcp.library as lib

    models_file = tmp_path / "models.json"
    models_file.write_text(json.dumps(SAMPLE_MODELS), encoding="utf-8")

    monkeypatch.setattr(lib, "LIBRARY_DIR", tmp_path)
    monkeypatch.setattr(lib, "MODELS_FILE", models_file)
    monkeypatch.setattr(lib, "CUSTOM_DIR", tmp_path / "custom")
    return tmp_path


@pytest.fixture()
def empty_dir(tmp_path, monkeypatch):
    """Patch library paths to a directory with no models.json."""
    import brian2models_mcp.library as lib

    monkeypatch.setattr(lib, "LIBRARY_DIR", tmp_path)
    monkeypatch.setattr(lib, "MODELS_FILE", tmp_path / "models.json")
    monkeypatch.setattr(lib, "CUSTOM_DIR", tmp_path / "custom")
    return tmp_path


class TestLoadModels:
    def test_loads_all_models(self, models_dir):
        from brian2models_mcp.library import load_models

        models = load_models()
        assert len(models) == 3
        assert all(isinstance(m, ModelRecord) for m in models)

    def test_returns_empty_when_file_missing(self, empty_dir):
        from brian2models_mcp.library import load_models

        assert load_models() == []


class TestGetModelById:
    def test_found(self, models_dir):
        from brian2models_mcp.library import get_model_by_id

        model = get_model_by_id("CUBA")
        assert model is not None
        assert model.name == "CUBA"

    def test_not_found(self, models_dir):
        from brian2models_mcp.library import get_model_by_id

        assert get_model_by_id("nonexistent") is None


class TestListModels:
    def test_returns_summaries(self, models_dir):
        from brian2models_mcp.library import list_models

        summaries = list_models()
        assert len(summaries) == 3
        assert summaries[0].one_line_description == "Hodgkin-Huxley model of action potential generation."
        assert summaries[1].one_line_description == "Current-based synapses example."


class TestSearchModels:
    def test_returns_summaries_not_full_records(self, models_dir):
        from brian2models_mcp.library import search_models
        from brian2models_mcp.schemas import ModelSummary

        result = search_models("anything")
        assert result.query == "anything"
        assert result.total_count == 3
        assert len(result.models) == 3
        assert all(isinstance(m, ModelSummary) for m in result.models)
        # Summaries should NOT have source code
        assert not hasattr(result.models[0], "source")

    def test_returns_all_with_different_query(self, models_dir):
        from brian2models_mcp.library import search_models

        result = search_models("xyz_not_matching")
        assert result.total_count == 3
