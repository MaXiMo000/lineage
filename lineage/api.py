"""HTTP API. Phase 0: build a tree from variants you supply. Phase 1 adds POST /api/traces (auto-retrieval)."""
from datetime import datetime
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from .tree import Variant, build_tree

app = FastAPI(title="lineage")
WEB = Path(__file__).resolve().parent.parent / "web"


class VariantIn(BaseModel):
    text: str
    date: datetime
    url: str = ""


class TreeIn(BaseModel):
    variants: list[VariantIn]
    threshold: float = 0.25


@app.post("/api/tree")
def tree(body: TreeIn):
    vs = [Variant(id=str(i), text=v.text, date=v.date, url=v.url) for i, v in enumerate(body.variants)]
    return build_tree(vs, body.threshold)


@app.get("/")
def index():
    return FileResponse(WEB / "index.html")
