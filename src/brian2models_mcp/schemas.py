from pydantic import BaseModel


class ModelRecord(BaseModel):
    id: str
    name: str
    docstring: str
    source: str
    origin_url: str
    tags: list[str]


class ModelSummary(BaseModel):
    id: str
    name: str
    one_line_description: str


class SearchResult(BaseModel):
    query: str
    models: list[ModelSummary]
    total_count: int
