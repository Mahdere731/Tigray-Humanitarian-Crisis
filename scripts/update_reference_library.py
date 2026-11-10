#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import logging
import re
import tempfile
from dataclasses import dataclass
from datetime import date, datetime, timezone
from email.utils import parsedate_to_datetime
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

CUTOFF_DATE = date(2026, 9, 26)
REQUEST_TIMEOUT_SECONDS = 20
USER_AGENT = (
    "TigrayReferenceLibraryUpdater/1.0 "
    "(https://github.com/Mahdere731/Tigray-Humanitarian-Crisis)"
)
PROCESSED_ARCHIVE_LIMIT = 5000

KEYWORDS = [
    "tigray",
    "humanitarian crisis",
    "displacement",
    "food insecurity",
    "civilian casualties",
    "drone strikes",
    "aid access",
    "human rights investigations",
    "accountability efforts",
    "peace implementation",
    "eritrean troop presence",
    "recovery and reconstruction",
]

SOURCE_CONFIG: Sequence[Dict[str, object]] = [
    {
        "name": "Reuters",
        "publication": "Reuters",
        "section_heading": "## **Reuters**",
        "rss_feeds": ["https://www.reuters.com/world/africa/rss"],
    },
    {
        "name": "Associated Press",
        "publication": "Associated Press",
        "section_heading": "## **AP**",
        "rss_feeds": ["https://apnews.com/hub/africa.rss"],
        "fallback_pages": ["https://apnews.com/hub/africa"],
    },
    {
        "name": "BBC",
        "publication": "BBC",
        "section_heading": "## **BBC**",
        "rss_feeds": ["https://feeds.bbci.co.uk/news/world/africa/rss.xml"],
    },
    {
        "name": "AFP",
        "publication": "AFP",
        "section_heading": "## Recent Sources (Post September 25, 2026)",
        "fallback_pages": ["https://www.afp.com/en/search?query=tigray"],
    },
    {
        "name": "Al Jazeera",
        "publication": "Al Jazeera",
        "section_heading": "## **Al Jazeera**",
        "rss_feeds": ["https://www.aljazeera.com/xml/rss/all.xml"],
    },
    {
        "name": "UN OCHA",
        "publication": "UN OCHA",
        "section_heading": "## **United Nations Office for the Coordination of Humanitarian Affairs (OCHA)**",
        "rss_feeds": ["https://www.unocha.org/rss.xml"],
    },
    {
        "name": "OHCHR",
        "publication": "OHCHR",
        "section_heading": "## Recent Sources (Post September 25, 2026)",
        "rss_feeds": ["https://www.ohchr.org/en/press-releases/rss.xml"],
    },
    {
        "name": "Human Rights Watch",
        "publication": "Human Rights Watch",
        "section_heading": "## **Human Rights Watch**",
        "rss_feeds": ["https://www.hrw.org/rss/news"],
    },
    {
        "name": "Amnesty International",
        "publication": "Amnesty International",
        "section_heading": "## **Amnesty International**",
        "rss_feeds": ["https://www.amnesty.org/en/latest/rss/"],
    },
    {
        "name": "International Crisis Group",
        "publication": "International Crisis Group",
        "section_heading": "## Recent Sources (Post September 25, 2026)",
        "rss_feeds": ["https://www.crisisgroup.org/rss.xml"],
    },
    {
        "name": "MSF",
        "publication": "MSF",
        "section_heading": "## **Médecins Sans Frontières (Doctors Without Borders)**",
        "rss_feeds": ["https://www.doctorswithoutborders.org/latest/rss.xml"],
    },
    {
        "name": "Ethiopian Human Rights Commission",
        "publication": "Ethiopian Human Rights Commission",
        "section_heading": "## Recent Sources (Post September 25, 2026)",
        "fallback_pages": ["https://ehrc.org/category/press-release/"],
    },
    {
        "name": "African Union",
        "publication": "African Union",
        "section_heading": "## Recent Sources (Post September 25, 2026)",
        "rss_feeds": ["https://au.int/en/pressreleases/rss.xml"],
        "fallback_pages": ["https://au.int/en/pressreleases"],
    },
]


@dataclass(frozen=True)
class CandidateItem:
    source_name: str
    section_heading: str
    title: str
    url: str
    publication_date: str
    publication: str
    author: Optional[str]
    description: str


class LinkCollector(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: List[Tuple[str, str]] = []
        self._current_href: Optional[str] = None
        self._text_parts: List[str] = []

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Optional[str]]]) -> None:
        if tag.lower() != "a":
            return
        for key, value in attrs:
            if key.lower() == "href" and value:
                self._current_href = value.strip()
                self._text_parts = []
                return

    def handle_data(self, data: str) -> None:
        if self._current_href:
            self._text_parts.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() != "a" or not self._current_href:
            return
        text = " ".join(" ".join(self._text_parts).split())
        if text:
            self.links.append((self._current_href, text))
        self._current_href = None
        self._text_parts = []


def normalize_title(value: str) -> str:
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9]+", " ", value.lower())).strip()


def normalize_url(value: str) -> str:
    try:
        parsed = urlsplit(value.strip())
    except ValueError:
        return ""
    scheme = parsed.scheme.lower() or "https"
    netloc = parsed.netloc.lower()
    if not netloc:
        return ""
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = re.sub(r"/{2,}", "/", parsed.path or "/").rstrip("/") or "/"
    return urlunsplit((scheme, netloc, path, parsed.query, ""))


def safe_write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=str(path.parent)) as temp:
        temp.write(content)
        temp_path = Path(temp.name)
    temp_path.replace(path)


def fetch_text(url: str) -> str:
    request = Request(url=url, headers={"User-Agent": USER_AGENT})
    with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
        charset = response.headers.get_content_charset() or "utf-8"
        raw = response.read()
    return raw.decode(charset, errors="replace")


def parse_date(raw_date: Optional[str]) -> Optional[date]:
    if not raw_date:
        return None
    value = raw_date.strip()
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        return dt.date()
    except ValueError:
        pass
    try:
        dt = parsedate_to_datetime(value)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc).date()
    except (TypeError, ValueError):
        return None


def within_target_scope(title: str, description: str) -> bool:
    text = f"{title} {description}".lower()
    return any(term in text for term in KEYWORDS)


def summarize_description(value: str) -> str:
    cleaned = re.sub(r"<[^>]+>", " ", value or "")
    cleaned = unescape(cleaned)
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        return ""
    if len(cleaned) <= 280:
        return cleaned
    return cleaned[:277].rstrip() + "..."


def _find_text(node: ET.Element, tags: Iterable[str]) -> Optional[str]:
    for tag in tags:
        found = node.find(tag)
        if found is not None and found.text and found.text.strip():
            return found.text.strip()
    return None


def parse_rss_feed(feed_url: str, source_name: str, publication: str, section_heading: str) -> List[CandidateItem]:
    items: List[CandidateItem] = []
    try:
        payload = fetch_text(feed_url)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        logging.warning("Source '%s' RSS fetch failed for %s: %s", source_name, feed_url, exc)
        return items

    try:
        root = ET.fromstring(payload)
    except ET.ParseError as exc:
        logging.warning("Source '%s' RSS parse failed for %s: %s", source_name, feed_url, exc)
        return items

    namespaces = {"atom": "http://www.w3.org/2005/Atom", "dc": "http://purl.org/dc/elements/1.1/"}
    entries = list(root.findall(".//item")) + list(root.findall(".//atom:entry", namespaces))
    for entry in entries:
        title = _find_text(entry, ["title", "{http://www.w3.org/2005/Atom}title"])
        if not title:
            continue
        link = _find_text(entry, ["link", "{http://www.w3.org/2005/Atom}link"])
        if not link:
            atom_link = entry.find("{http://www.w3.org/2005/Atom}link")
            if atom_link is not None:
                link = atom_link.attrib.get("href")
        if not link:
            continue
        pub_date_raw = _find_text(
            entry,
            [
                "pubDate",
                "published",
                "updated",
                "{http://purl.org/dc/elements/1.1/}date",
                "{http://www.w3.org/2005/Atom}published",
                "{http://www.w3.org/2005/Atom}updated",
            ],
        )
        publication_date = parse_date(pub_date_raw)
        if not publication_date or publication_date < CUTOFF_DATE:
            continue
        description = _find_text(entry, ["description", "summary", "{http://www.w3.org/2005/Atom}summary"]) or ""
        if not within_target_scope(title, description):
            continue
        author = _find_text(
            entry,
            [
                "{http://purl.org/dc/elements/1.1/}creator",
                "author",
                "{http://www.w3.org/2005/Atom}author/{http://www.w3.org/2005/Atom}name",
            ],
        )
        items.append(
            CandidateItem(
                source_name=source_name,
                section_heading=section_heading,
                title=" ".join(title.split()),
                url=link.strip(),
                publication_date=publication_date.isoformat(),
                publication=publication,
                author=author,
                description=summarize_description(description),
            )
        )
    return items


def parse_date_from_url(url: str) -> Optional[date]:
    match = re.search(r"(20\d{2})[-/](\d{2})[-/](\d{2})", url)
    if not match:
        return None
    year, month, day = (int(group) for group in match.groups())
    try:
        return date(year, month, day)
    except ValueError:
        return None


def parse_official_page(page_url: str, source_name: str, publication: str, section_heading: str) -> List[CandidateItem]:
    items: List[CandidateItem] = []
    try:
        payload = fetch_text(page_url)
    except (HTTPError, URLError, TimeoutError, OSError) as exc:
        logging.warning("Source '%s' fallback fetch failed for %s: %s", source_name, page_url, exc)
        return items

    parser = LinkCollector()
    parser.feed(payload)

    for href, link_text in parser.links:
        absolute = urljoin(page_url, href)
        parsed = urlsplit(absolute)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            continue
        pub_date = parse_date_from_url(absolute)
        if not pub_date or pub_date < CUTOFF_DATE:
            continue
        if not within_target_scope(link_text, ""):
            continue
        items.append(
            CandidateItem(
                source_name=source_name,
                section_heading=section_heading,
                title=link_text,
                url=absolute,
                publication_date=pub_date.isoformat(),
                publication=publication,
                author=None,
                description="Collected from the source's official public page fallback.",
            )
        )
    return items


def collect_candidates() -> Tuple[List[CandidateItem], Dict[str, object]]:
    all_items: List[CandidateItem] = []
    stats = {"sources_attempted": 0, "items_collected": 0}

    for source in SOURCE_CONFIG:
        source_name = str(source["name"])
        publication = str(source["publication"])
        section_heading = str(source["section_heading"])
        stats["sources_attempted"] += 1
        source_items: List[CandidateItem] = []
        for feed in source.get("rss_feeds", []):
            source_items.extend(parse_rss_feed(str(feed), source_name, publication, section_heading))
        if not source_items:
            for page in source.get("fallback_pages", []):
                source_items.extend(parse_official_page(str(page), source_name, publication, section_heading))
        all_items.extend(source_items)

    stats["items_collected"] = len(all_items)
    return all_items, stats


def load_processed(path: Path) -> Dict[str, object]:
    if not path.exists():
        return {"updated_at_utc": None, "items": []}
    try:
        content = json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        raise RuntimeError(f"Unable to parse processed source archive: {path}") from exc
    if not isinstance(content, dict) or not isinstance(content.get("items", []), list):
        raise RuntimeError(f"Unexpected processed source schema in {path}")
    return content


def extract_existing_keys(markdown_text: str) -> Tuple[Set[str], Set[str]]:
    urls = set(normalize_url(match) for match in re.findall(r"https?://[^\s)>\"]+", markdown_text))
    titles = set(normalize_title(match) for match in re.findall(r"-\s*###\s*\[([^\]]+)\]\(", markdown_text))
    return urls, titles


def deduplicate_candidates(
    candidates: Sequence[CandidateItem],
    markdown_text: str,
    processed_items: Sequence[Dict[str, object]],
) -> List[CandidateItem]:
    markdown_urls, markdown_titles = extract_existing_keys(markdown_text)
    processed_url_keys = {
        normalize_url(str(item.get("url", "")))
        for item in processed_items
        if isinstance(item, dict) and item.get("url")
    }
    processed_title_date = {
        (normalize_title(str(item.get("title", ""))), str(item.get("publication_date", "")))
        for item in processed_items
        if isinstance(item, dict)
    }

    accepted: List[CandidateItem] = []
    seen_new: Set[Tuple[str, str]] = set()
    for item in candidates:
        normalized_url = normalize_url(item.url)
        normalized_title = normalize_title(item.title)
        title_date_key = (normalized_title, item.publication_date)
        if not normalized_url or not normalized_title:
            continue
        if (
            normalized_url in markdown_urls
            or normalized_url in processed_url_keys
            or normalized_title in markdown_titles
            or title_date_key in processed_title_date
            or title_date_key in seen_new
        ):
            continue
        seen_new.add(title_date_key)
        accepted.append(item)
    return accepted


def ensure_recent_section(lines: List[str]) -> None:
    heading = "## Recent Sources (Post September 25, 2026)"
    if any(line.strip() == heading for line in lines):
        return
    if lines and lines[-1].strip():
        lines.append("")
    lines.extend([heading, ""])


def find_section_bounds(lines: List[str], heading: str) -> Optional[Tuple[int, int]]:
    start = None
    for index, line in enumerate(lines):
        if line.strip() == heading:
            start = index
            break
    if start is None:
        return None
    end = len(lines)
    for index in range(start + 1, len(lines)):
        if lines[index].startswith("## ") or lines[index].startswith("# "):
            end = index
            break
    return start, end


def render_entry(item: CandidateItem) -> List[str]:
    return [f"- ### [{item.title}]({item.url})", "", "  ***", ""]


def insert_items(markdown_text: str, items: Sequence[CandidateItem]) -> str:
    if not items:
        return markdown_text

    lines = markdown_text.splitlines()
    grouped: Dict[str, List[CandidateItem]] = {}
    for item in items:
        grouped.setdefault(item.section_heading, []).append(item)

    if any(heading == "## Recent Sources (Post September 25, 2026)" for heading in grouped):
        ensure_recent_section(lines)

    for original_heading in sorted(grouped):
        section_heading = original_heading
        bounds = find_section_bounds(lines, section_heading)
        if not bounds:
            if section_heading != "## Recent Sources (Post September 25, 2026)":
                ensure_recent_section(lines)
                section_heading = "## Recent Sources (Post September 25, 2026)"
                bounds = find_section_bounds(lines, section_heading)
            if not bounds:
                continue
        _, end = bounds
        insert_at = end
        while insert_at > 0 and not lines[insert_at - 1].strip():
            insert_at -= 1

        section_items_source = grouped[original_heading]
        section_items = sorted(
            section_items_source,
            key=lambda item: (item.publication_date, normalize_title(item.title), normalize_url(item.url)),
            reverse=True,
        )
        block: List[str] = []
        for item in section_items:
            block.extend(render_entry(item))
        lines[insert_at:insert_at] = block

    return "\n".join(lines) + ("\n" if markdown_text.endswith("\n") else "")


def merge_processed_archive(existing_items: Sequence[Dict[str, object]], new_items: Sequence[CandidateItem]) -> List[Dict[str, object]]:
    merged = [item for item in existing_items if isinstance(item, dict)]
    for item in new_items:
        merged.append(
            {
                "source_name": item.source_name,
                "publication": item.publication,
                "title": item.title,
                "normalized_title": normalize_title(item.title),
                "url": item.url,
                "normalized_url": normalize_url(item.url),
                "publication_date": item.publication_date,
                "author": item.author,
                "description": item.description,
                "section_heading": item.section_heading,
            }
        )
    merged.sort(
        key=lambda item: (
            str(item.get("publication_date", "")),
            str(item.get("normalized_title", "")),
            str(item.get("normalized_url", "")),
        ),
        reverse=True,
    )
    seen: Set[Tuple[str, str]] = set()
    deduped: List[Dict[str, object]] = []
    for item in merged:
        key = (str(item.get("normalized_url", "")), str(item.get("publication_date", "")))
        if key in seen:
            continue
        seen.add(key)
        deduped.append(item)
        if len(deduped) >= PROCESSED_ARCHIVE_LIMIT:
            break
    return deduped


def run(reference_library: Path, processed_archive: Path, report_path: Path) -> int:
    if not reference_library.exists():
        raise RuntimeError(f"Missing reference library file: {reference_library}")

    markdown_before = reference_library.read_text(encoding="utf-8")
    processed_payload = load_processed(processed_archive)
    processed_items = processed_payload.get("items", [])
    if not isinstance(processed_items, list):
        raise RuntimeError("Processed archive must include an 'items' list")

    candidates, stats = collect_candidates()
    new_items = deduplicate_candidates(candidates, markdown_before, processed_items)
    markdown_after = insert_items(markdown_before, new_items)

    markdown_changed = markdown_after != markdown_before
    if markdown_changed:
        safe_write_text(reference_library, markdown_after)

    processed_changed = False
    if new_items:
        updated_items = merge_processed_archive(processed_items, new_items)
        new_payload = {
            "updated_at_utc": datetime.now(timezone.utc).isoformat(),
            "cutoff_date": CUTOFF_DATE.isoformat(),
            "items": updated_items,
        }
        safe_write_text(processed_archive, json.dumps(new_payload, indent=2, ensure_ascii=False) + "\n")
        processed_changed = True

    report = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "cutoff_date": CUTOFF_DATE.isoformat(),
        "sources_attempted": stats["sources_attempted"],
        "items_collected_before_deduplication": stats["items_collected"],
        "new_references_added": len(new_items),
        "reference_library_modified": markdown_changed,
        "processed_archive_modified": processed_changed,
    }
    safe_write_text(report_path, json.dumps(report, indent=2, ensure_ascii=False) + "\n")
    print(json.dumps(report, indent=2))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Collect trusted Tigray references and append new markdown entries.")
    parser.add_argument(
        "--reference-library",
        default="references/Reference-Library.md",
        help="Path to Reference-Library.md",
    )
    parser.add_argument(
        "--processed-archive",
        default="data/processed_sources.json",
        help="Path to processed source archive JSON",
    )
    parser.add_argument(
        "--report-file",
        default="data/reference_update_report.json",
        help="Path to machine-readable run report",
    )
    parser.add_argument("--log-level", default="INFO", help="Python logging level (INFO, WARNING, ...)")
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO), format="%(levelname)s: %(message)s")

    try:
        return run(
            reference_library=Path(args.reference_library).resolve(),
            processed_archive=Path(args.processed_archive).resolve(),
            report_path=Path(args.report_file).resolve(),
        )
    except Exception as exc:  # unrecoverable failures
        logging.error("Reference library update failed: %s", exc)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
