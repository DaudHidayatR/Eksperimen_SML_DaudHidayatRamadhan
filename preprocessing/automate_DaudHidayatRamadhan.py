"""Automate the executed notebook policy; return train-ready text and targets."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import pandas as pd
from sklearn.model_selection import train_test_split

LABELS = ["SQLInjection", "XSS", "CommandInjection", "Normal"]
RAW_SHA256 = "e221ea9e118cdac6d7dabf085a224f42b6cde800a71c446f71c2dec609a2c233"
ROOT = Path(__file__).resolve().parents[1]


def clean_frame(df):
    """Remove unusable labels/text, every contradictory group, and duplicates."""
    if list(df.columns) != ["Sentence"] + LABELS:
        raise ValueError("Raw schema must match Sentence and the four label columns")
    work = df.copy()
    valid = work.Sentence.notna() & work.Sentence.fillna("").str.strip().ne("")
    valid &= work[LABELS].isin([0, 1]).all(axis=1) & work[LABELS].sum(axis=1).eq(1)
    work = work.loc[valid].copy()
    work["target"] = work[LABELS].idxmax(axis=1)
    counts = work.groupby("Sentence").target.nunique()
    conflicts = set(counts[counts > 1].index)
    conflict_rows = int(work.Sentence.isin(conflicts).sum())
    work = work.loc[~work.Sentence.isin(conflicts)].drop_duplicates("Sentence").copy()
    work["sample_id"] = work.Sentence.map(lambda value: hashlib.sha256(value.encode("utf-8")).hexdigest())
    work = work.sort_values("sample_id").reset_index(drop=True)
    return work[["sample_id", "Sentence", "target"]], {
        "raw_rows": len(df), "invalid_or_empty_rows": int((~valid).sum()),
        "conflicting_groups": len(conflicts), "conflicting_rows": conflict_rows,
        "clean_unique_rows": len(work),
        "clean_class_counts": work.target.value_counts().sort_index().to_dict(),
    }


def preprocess(raw_path=ROOT / "sqli_xss_raw/payloads-v2.csv.gz",
               output=ROOT / "preprocessing/sqli_xss_preprocessing",
               sample_size=24000, seed=42, expected_hash=RAW_SHA256):
    raw_path, output = Path(raw_path), Path(output)
    raw_hash = hashlib.sha256(gzip.decompress(raw_path.read_bytes())).hexdigest()
    if raw_hash != expected_hash:
        raise ValueError("Raw checksum changed; review the new source and update notebook and automation together")
    clean, audit = clean_frame(pd.read_csv(raw_path))
    if not 0 < sample_size < len(clean):
        raise ValueError("Sample size must be positive and smaller than cleaned data")
    selected, excluded = train_test_split(clean, train_size=sample_size,
                                         stratify=clean.target, random_state=seed)
    train, test = train_test_split(selected, test_size=0.2, stratify=selected.target, random_state=seed)
    train, test = [frame.sort_values("sample_id").reset_index(drop=True) for frame in (train, test)]
    if not set(train.sample_id).isdisjoint(test.sample_id):
        raise ValueError("Split leakage: duplicate payload IDs")
    if set(train.target) != set(LABELS) or set(test.target) != set(LABELS):
        raise ValueError("Both splits must represent all four classes")
    output.mkdir(parents=True, exist_ok=True)
    hashes = {}
    for name, frame in [("train", train), ("test", test)]:
        content = frame.to_csv(index=False, lineterminator="\n").encode("utf-8")
        destination = output / f"{name}.csv.gz"
        with destination.open("wb") as handle:
            with gzip.GzipFile(fileobj=handle, filename="", mode="wb", mtime=0) as stream:
                stream.write(content)
        hashes[destination.name] = hashlib.sha256(destination.read_bytes()).hexdigest()
    manifest = {"policy_version": 1, "seed": seed, "sample_size": sample_size,
                "raw_sha256": raw_hash, **audit, "subset_excluded_rows": len(excluded),
                "train_rows": len(train), "test_rows": len(test),
                "train_class_counts": train.target.value_counts().sort_index().to_dict(),
                "test_class_counts": test.target.value_counts().sort_index().to_dict(),
                "files": hashes,
                "feature_boundary": "clean text+target; fit TF-IDF only on each training/CV fold"}
    (output / "manifest.json").write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n")
    return train, test, manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=ROOT / "preprocessing/sqli_xss_preprocessing")
    args = parser.parse_args()
    _, _, manifest = preprocess(output=args.output)
    print(json.dumps(manifest, indent=2, sort_keys=True))
