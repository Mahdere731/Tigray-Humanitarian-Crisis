#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

URL_RE = re.compile(r"https?://[^\s<>\"'`]+", re.IGNORECASE)
TRACKING_QUERY_KEYS = {
    "utm_source",
    "utm_medium",
    "utm_campaign",
    "utm_term",
    "utm_content",
    "fbclid",
    "gclid",
    "mc_cid",
    "mc_eid",
    "igshid",
}
HEADING_RE = re.compile(r"^##\s+(.+?)\s*$")
IMAGE_PATH_SUFFIXES = {".svg", ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico"}


@dataclass
class UrlRecord:
    original: str
    normalized: str
    domain: str


def find_references_dir(repo_root: Path) -> Path:
    for name in ("references", "References"):
        candidate = repo_root / name
        if candidate.is_dir():
            return candidate
    raise FileNotFoundError("Could not find references/ or References/ directory")


def find_reference_library(references_dir: Path) -> Path:
    preferred = references_dir / "Reference-Library.md"
    if preferred.exists():
        return preferred
    markdown_files = sorted(
        p for p in references_dir.rglob("*") if p.is_file() and p.suffix.lower() in {".md", ".markdown"}
    )
    if not markdown_files:
        raise FileNotFoundError("No markdown reference files found in references directory")
    return markdown_files[0]


def iter_markdown_files(repo_root: Path) -> Iterable[Path]:
    skip_dirs = {".git", ".venv", "venv", "node_modules", "__pycache__"}
    for path in repo_root.rglob("*"):
        if not path.is_file():
            continue
        if any(part in skip_dirs for part in path.parts):
            continue
        if path.suffix.lower() in {".md", ".markdown"}:
            yield path


def extract_urls(text: str) -> List[str]:
    urls: List[str] = []
    for match in URL_RE.findall(text):
        candidate = match.strip().strip("<>\"'`")
        if ")](" in candidate:
            candidate = candidate.split(")](", 1)[0]
        if "](" in candidate:
            candidate = candidate.split("](", 1)[0]
        while candidate and candidate[-1] in ".,;:!?)]}*>_\"'`":
            candidate = candidate[:-1]
        while candidate and candidate[0] in "([{<\"'`":
            candidate = candidate[1:]
        if candidate:
            urls.append(candidate)
    return urls


def normalize_url(raw_url: str) -> Tuple[Optional[UrlRecord], Optional[str]]:
    try:
        parsed = urlsplit(raw_url)
    except Exception:
        return None, f"Malformed URL: {raw_url}"

    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"} or not parsed.netloc:
        return None, f"Unsupported or malformed URL: {raw_url}"

    domain = parsed.netloc.lower()
    if domain.startswith("www."):
        domain = domain[4:]
    if ":" in domain:
        host, _, port = domain.partition(":")
        if port in {"80", "443"}:
            domain = host
    if not re.match(r"^[a-z0-9.-]+(:[0-9]+)?$", domain):
        return None, f"Malformed domain in URL: {raw_url}"

    path = re.sub(r"/{2,}", "/", parsed.path or "/")
    path = path.rstrip("/") or "/"
    if any(path.lower().endswith(ext) for ext in IMAGE_PATH_SUFFIXES):
        return None, f"Skipped non-article asset URL: {raw_url}"

    filtered_query = [
        (k, v)
        for k, v in parse_qsl(parsed.query, keep_blank_values=True)
        if k.lower() not in TRACKING_QUERY_KEYS
    ]
    filtered_query.sort()
    query = urlencode(filtered_query, doseq=True)

    normalized = urlunsplit((scheme, domain, path, query, ""))
    return UrlRecord(original=raw_url, normalized=normalized, domain=domain), None


def parse_sections(lines: List[str]) -> List[Tuple[str, int, int]]:
    headings: List[Tuple[str, int]] = []
    for idx, line in enumerate(lines):
        match = HEADING_RE.match(line)
        if match:
            headings.append((match.group(1).strip(), idx))

    sections: List[Tuple[str, int, int]] = []
    for i, (title, start) in enumerate(headings):
        end = headings[i + 1][1] if i + 1 < len(headings) else len(lines)
        sections.append((title, start, end))
    return sections


def infer_domain_category_map(lines: List[str]) -> Tuple[Dict[str, str], List[str]]:
    sections = parse_sections(lines)
    category_by_domain_counter: Dict[str, Counter] = defaultdict(Counter)
    valid_categories: List[str] = []

    for title, start, end in sections:
        section_text = "\n".join(lines[start:end])
        section_urls = extract_urls(section_text)
        domains_in_section = []
        for url in section_urls:
            record, _ = normalize_url(url)
            if record is None:
                continue
            domains_in_section.append(record.domain)
        if domains_in_section:
            valid_categories.append(title)
            for domain in domains_in_section:
                category_by_domain_counter[domain][title] += 1

    domain_map: Dict[str, str] = {}
    for domain, counter in category_by_domain_counter.items():
        best_category = sorted(counter.items(), key=lambda item: (-item[1], item[0]))[0][0]
        domain_map[domain] = best_category

    return domain_map, valid_categories


def ensure_section(lines: List[str], section_title: str) -> None:
    for line in lines:
        m = HEADING_RE.match(line)
        if m and m.group(1).strip() == section_title:
            return

    if lines and lines[-1].strip() != "":
        lines.append("")
    lines.extend([f"## {section_title}", ""])


def insert_urls_into_section(lines: List[str], section_title: str, urls: List[str]) -> None:
    if not urls:
        return

    sections = parse_sections(lines)
    target = None
    for title, start, end in sections:
        if title == section_title:
            target = (start, end)
            break

    if target is None:
        return

    _, end = target
    insert_at = end
    while insert_at > 0 and lines[insert_at - 1].strip() == "":
        insert_at -= 1
    if insert_at > 0 and lines[insert_at - 1].strip() == "---":
        insert_at -= 1

    new_lines = [f"- [{url}]({url})" for url in urls]
    lines[insert_at:insert_at] = new_lines + [""]


def sync_references(repo_root: Path, references_file: Path, report_path: Path, dry_run: bool = False) -> Dict[str, object]:
    library_text = references_file.read_text(encoding="utf-8")
    library_lines = library_text.splitlines()

    domain_to_category, categories_with_urls = infer_domain_category_map(library_lines)
    fallback_category = "Uncategorized"

    all_urls_total = 0
    malformed_urls: List[str] = []
    duplicate_hits = 0
    seen_normalized: Set[str] = set()
    all_valid_records: Dict[str, UrlRecord] = {}

    markdown_files = list(iter_markdown_files(repo_root))

    existing_reference_urls: Set[str] = set()
    references_dir = references_file.parent.resolve()

    for md_file in markdown_files:
        text = md_file.read_text(encoding="utf-8", errors="ignore")
        urls = extract_urls(text)
        for raw_url in urls:
            all_urls_total += 1
            record, err = normalize_url(raw_url)
            if err:
                malformed_urls.append(raw_url)
                continue
            assert record is not None
            if record.normalized in seen_normalized:
                duplicate_hits += 1
            else:
                seen_normalized.add(record.normalized)
                all_valid_records[record.normalized] = record
            if references_dir in md_file.resolve().parents:
                existing_reference_urls.add(record.normalized)

    missing_keys = [key for key in all_valid_records.keys() if key not in existing_reference_urls]

    additions_by_category: Dict[str, List[str]] = defaultdict(list)
    uncategorized_urls: List[str] = []

    for key in sorted(missing_keys):
        record = all_valid_records[key]
        category = domain_to_category.get(record.domain, fallback_category)
        if category not in categories_with_urls and category != fallback_category:
            category = fallback_category
        additions_by_category[category].append(record.normalized)
        if category == fallback_category:
            uncategorized_urls.append(record.normalized)

    if additions_by_category.get(fallback_category):
        ensure_section(library_lines, fallback_category)

    for category in sorted(additions_by_category.keys()):
        insert_urls_into_section(library_lines, category, sorted(set(additions_by_category[category])))

    updated_text = "\n".join(library_lines) + "\n"
    modified = updated_text != library_text

    if modified and not dry_run:
        references_file.write_text(updated_text, encoding="utf-8")

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repository_root": str(repo_root),
        "references_file": str(references_file),
        "total_references_found": len(all_valid_records),
        "already_present": len(all_valid_records) - len(missing_keys),
        "added": sum(len(v) for v in additions_by_category.values()),
        "skipped_duplicates": duplicate_hits,
        "uncategorized_unknown": len(uncategorized_urls),
        "malformed_urls": malformed_urls,
        "scanned_markdown_files": sorted(str(p.relative_to(repo_root)) for p in markdown_files),
        "added_by_category": {k: sorted(set(v)) for k, v in sorted(additions_by_category.items())},
        "modified_references_file": modified,
    }

    if not dry_run:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    return report


def main() -> int:
    parser = argparse.ArgumentParser(description="Synchronize missing markdown references into the references library.")
    parser.add_argument("--repo-root", default=".", help="Repository root directory")
    parser.add_argument("--references-file", default=None, help="Path to the markdown reference library file")
    parser.add_argument(
        "--report-file",
        default=None,
        help="Output JSON report path (defaults to references/reference-sync-report.json)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Analyze and report without writing files")
    args = parser.parse_args()

    repo_root = Path(args.repo_root).resolve()
    references_dir = find_references_dir(repo_root)
    references_file = Path(args.references_file).resolve() if args.references_file else find_reference_library(references_dir)
    report_file = (
        Path(args.report_file).resolve()
        if args.report_file
        else (references_dir / "reference-sync-report.json").resolve()
    )

    report = sync_references(repo_root=repo_root, references_file=references_file, report_path=report_file, dry_run=args.dry_run)

    print(json.dumps({
        "total_references_found": report["total_references_found"],
        "already_present": report["already_present"],
        "added": report["added"],
        "skipped_duplicates": report["skipped_duplicates"],
        "uncategorized_unknown": report["uncategorized_unknown"],
        "modified_references_file": report["modified_references_file"],
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
