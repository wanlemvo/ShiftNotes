"""
embed.py
ShiftNotes RAG — Indexing Script

Run this once to embed shift reports and store them in ChromaDB.
Re-run whenever new reports are added.

Usage:
    python embed.py                          # index the mock dataset
    python embed.py --csv path/to/file.csv   # index a custom CSV
"""

import argparse
import pathlib
import pandas as pd
import chromadb
from sentence_transformers import SentenceTransformer

CHROMA_PATH = pathlib.Path(__file__).parent / "chroma_db"
DEFAULT_CSV  = pathlib.Path(__file__).parent.parent / "prototype" / "mock_shift_notes.csv"
EMBED_MODEL  = "all-MiniLM-L6-v2"
COLLECTION   = "shift_reports"


def prepare_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    text_cols = [
        "food_concerns_or_outages",
        "team_members_who_did_well",
        "guest_issues_for_the_day",
        "operational_notes",
    ]
    for col in text_cols:
        df[col] = df[col].fillna("").astype(str).str.strip()

    df["full_text"] = (
        df["food_concerns_or_outages"] + " "
        + df["team_members_who_did_well"] + " "
        + df["guest_issues_for_the_day"] + " "
        + df["operational_notes"]
    )
    return df


def build_index(csv_path: pathlib.Path = DEFAULT_CSV, chroma_path: pathlib.Path = CHROMA_PATH) -> int:
    print(f"Loading data from {csv_path} ...")
    df = prepare_dataframe(pd.read_csv(csv_path))

    print(f"Loading embedding model ({EMBED_MODEL}) ...")
    model = SentenceTransformer(EMBED_MODEL)

    print(f"Embedding {len(df)} reports ...")
    embeddings = model.encode(df["full_text"].tolist(), show_progress_bar=True)

    chroma_path.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(chroma_path))

    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass

    collection = client.create_collection(COLLECTION)

    collection.add(
        ids=[str(r) for r in df["report_id"]],
        embeddings=embeddings.tolist(),
        documents=df["full_text"].tolist(),
        metadatas=[
            {
                "report_id":           int(row["report_id"]),
                "date":                str(row["date"]),
                "week":                int(row["week"]),
                "kiosk":               str(row["kiosk"]),
                "lead_name":           str(row["lead_name"]),
                "food_quality_rating": int(row["food_quality_rating"]),
                "food_quantity_rating":int(row["food_quantity_rating"]),
                "unclaimed_lunches":   int(row["number_of_unclaimed_lunches"]),
            }
            for _, row in df.iterrows()
        ],
    )

    count = collection.count()
    print(f"Done — {count} reports indexed at {chroma_path}")
    return count


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", type=pathlib.Path, default=DEFAULT_CSV)
    args = parser.parse_args()
    build_index(csv_path=args.csv)
