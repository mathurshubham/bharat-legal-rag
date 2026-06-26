import csv
from pathlib import Path

from fastapi import APIRouter, HTTPException

router = APIRouter()

REPO_ROOT = Path(__file__).parent.parent.parent.parent


@router.get("/api/{demo}/dataset")
async def dataset_info(demo: str):
    """Return parsed golden evaluation dataset for a demo."""
    path = REPO_ROOT / "golden_sets" / f"{demo.lower()}-dataset.csv"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"No dataset for demo '{demo}'")

    rows = []
    categories: dict[str, int] = {}
    columns: list[str] = []

    with open(path, encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        raw_fields = list(reader.fieldnames or [])
        # Strip long descriptions: "eval_context (category:…)" → "eval_context"
        clean_fields = {k: k.split("(")[0].strip() for k in raw_fields}
        columns = [clean_fields[k] for k in raw_fields]
        for raw_row in reader:
            row = {clean_fields[k]: v for k, v in raw_row.items()}
            rows.append(row)
            cat = row.get("eval_context", "")
            categories[cat] = categories.get(cat, 0) + 1

    return {
        "demo_id": demo.lower(),
        "columns": columns,
        "rows": rows,
        "categories": categories,
        "total": len(rows),
    }
