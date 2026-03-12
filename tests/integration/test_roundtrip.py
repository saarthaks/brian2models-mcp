"""Integration test: seed the library, then search and get a model by id."""

import json

import pytest

from brian2models_mcp.library import get_model_by_id, list_models, load_models, search_models
from brian2models_mcp.seeder import extract_docstring, parse_example_links


@pytest.mark.integration
class TestSeedSearchGetRoundtrip:
    """Requires that `brian2models seed` has been run (models.json exists)."""

    def test_models_loaded(self):
        models = load_models()
        assert len(models) > 0, "No models found — run `brian2models seed` first"

    def test_list_returns_summaries(self):
        summaries = list_models()
        assert len(summaries) > 0
        for s in summaries:
            assert s.id
            assert s.name

    def test_search_returns_summaries(self):
        from brian2models_mcp.schemas import ModelSummary

        result = search_models("Hodgkin-Huxley")
        assert result.total_count == len(load_models())
        assert result.query == "Hodgkin-Huxley"
        assert all(isinstance(m, ModelSummary) for m in result.models)

    def test_get_known_model(self):
        model = get_model_by_id("CUBA")
        assert model is not None
        assert model.name == "CUBA"
        assert len(model.source) > 0
        assert "brian2" in model.source.lower() or "Brian2" in model.source

    def test_get_missing_model(self):
        assert get_model_by_id("definitely_not_a_real_model") is None


class TestDocstringExtraction:
    def test_triple_double_quotes(self):
        source = '"""This is a docstring.\n\nMore details."""\nfrom brian2 import *\n'
        assert extract_docstring(source) == "This is a docstring.\n\nMore details."

    def test_triple_single_quotes(self):
        source = "'''Single quote docstring.'''\nimport foo\n"
        assert extract_docstring(source) == "Single quote docstring."

    def test_with_leading_comments(self):
        source = '# comment\n# another\n"""Docstring after comments."""\n'
        assert extract_docstring(source) == "Docstring after comments."

    def test_no_docstring(self):
        source = "from brian2 import *\nx = 1\n"
        assert extract_docstring(source) == ""


class TestParseExampleLinks:
    def test_filters_non_python(self):
        html = '''
        <a href="CUBA.html">CUBA</a>
        <a href="frompapers.Spreizer_et_al_2019.perlin1.npy.html">npy</a>
        <a href="frompapers.Brette_2012.README.txt.html">txt</a>
        '''
        names = parse_example_links(html)
        assert "CUBA" in names
        assert not any("npy" in n for n in names)
        assert not any("txt" in n for n in names)

    def test_dot_to_slash_conversion(self):
        html = '<a href="advanced.custom_events.html">link</a>'
        names = parse_example_links(html)
        assert "advanced/custom_events" in names
