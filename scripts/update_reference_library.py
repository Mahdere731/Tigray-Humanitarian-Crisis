#!/usr/bin/env python3
from __future__ import annotations

import json
import logging
import re
import tempfile
from dataclasses import dataclass
from datetime import date, datetime
from email.utils import parsedate_to_datetime
from html import unescape
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set, Tuple
from urllib.parse import quote_plus, urlparse
from urllib.request import Request, urlopen

import feedparser

REPO_ROOT = Path(__file__).resolve().parents[1]
REFERENCE_LIBRARY_PATH = REPO_ROOT / "references" / "Reference-Library.md"
PROCESSED_SOURCES_PATH = REPO_ROOT / "data" / "processed_sources.json"
CUTOFF_DATE = date(2026, 9, 25)
RECENT_SECTION_TITLE = "## Recent Sources (Post September 25, 2026)"
USER_AGENT = "TigrayReferenceUpdater/1.0 (+https://github.com/Mahdere731/Tigray-Humanitarian-Crisis)"
REQUEST_TIMEOUT_SECONDS = 20
MAX_SUMMARY_LENGTH = 320

TOPIC_QUERY = (
    '(Tigray OR "humanitarian crisis" OR displacement OR "food insecurity" '
    'OR "civilian casualties" OR "drone strikes" OR "aid access" '
    'OR "human rights investigations" OR "accountability efforts" '
    'OR "peace implementation" OR "Eritrean troop presence" '
    'OR "recovery and reconstruction")'
)


@dataclass(frozen=True)
class FeedSource:
    publication: str
    url: str


@dataclass
class SourceEntry:
    title: str
    author: str
    publication: str
    publication_date: str
    url: str
    description: str

    @property
    def normalized_title(self) -> str:
        return normalize_title(self.title)


def build_google_news_rss(query: str) -> str:
    return f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"


FEEDS: List[FeedSource] = [
    FeedSource("Reuters", build_google_news_rss(f"{TOPIC_QUERY} site:reuters.com")),
    FeedSource("Associated Press", build_google_news_rss(f"{TOPIC_QUERY} site:apnews.com")),
    FeedSource("BBC", "https://feeds.bbci.co.uk/news/world/africa/rss.xml"),
    FeedSource("AFP", build_google_news_rss(f"{TOPIC_QUERY} site:afp.com")),
    FeedSource("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    FeedSource("UN OCHA", build_google_news_rss(f"{TOPIC_QUERY} site:unocha.org")),
    FeedSource("OHCHR", build_google_news_rss(f"{TOPIC_QUERY} site:ohchr.org")),
    FeedSource("Human Rights Watch", build_google_news_rss(f"{TOPIC_QUERY} site:hrw.org")),
    FeedSource("Amnesty International", build_google_news_rss(f"{TOPIC_QUERY} site:amnesty.org")),
    FeedSource("International Crisis Group", build_google_news_rss(f"{TOPIC_QUERY} site:crisisgroup.org")),
    FeedSource("MSF", build_google_news_rss(f"{TOPIC_QUERY} site:msf.org OR site:doctorswithoutborders.org")),
    FeedSource("Ethiopian Human Rights Commission", build_google_news_rss(f"{TOPIC_QUERY} site:ehrc.org")),
    FeedSource("African Union", build_google_news_rss(f"{TOPIC_QUERY} site:au.int")),
    FeedSource("Peer-Reviewed Journals", build_google_news_rss(f"{TOPIC_QUERY} site:doi.org")),
    FeedSource("Recognized Academic Institutions", build_google_news_rss(f"{TOPIC_QUERY} site:.edu")),
]

TOPIC_TERMS = {
    "tigray",
    "humanitarian",
    "displacement",
    "food insecurity",
    "civilian casualties",
    "drone",
    "aid access",
    "human rights",
    "investigation",
    "accountability",
    "peace implementation",
    "eritrean",
    "recovery",
    "reconstruction",
}

HTML_TAG_RE = re.compile(r"<[^>]+>")
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
DATE_RE = re.compile(r"_Date:_\s*(\d{4}-\d{2}-\d{2})")
META_RE = re.compile(
    r"_Publication:_\s*(?P<publication>.+?)\s*\|\s*_Date:_\s*(?P<date>\d{4}-\d{2}-\d{2})\s*\|\s*_Author:_\s*(?P<author>.+)"
)


def configure_logging() -> None:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def strip_html(text: str) -> str:
    text = unescape(text or "")
    text = HTML_TAG_RE.sub(" ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def normalize_title(title: str) -> str:
    return re.sub(r"\s+", " ", (title or "").strip().lower())


def normalize_url(raw_url: str) -> str:
    url = (raw_url or "").strip()
    if not url:
        return ""
    try:
        parsed = urlparse(url)
    except ValueError:
        return ""
    scheme = parsed.scheme.lower() if parsed.scheme else "https"
    netloc = parsed.netloc.lower()
    if netloc.startswith("www."):
        netloc = netloc[4:]
    path = parsed.path.rstrip("/") or "/"
    normalized = f"{scheme}://{netloc}{path}"
    if parsed.query:
        normalized += f"?{parsed.query}"
    return normalized


def parse_date_from_entry(entry: dict) -> Optional[date]:
    if entry.get("published_parsed"):
        tm = entry.get("published_parsed")
        return date(tm.tm_year, tm.tm_mon, tm.tm_mday)
    if entry.get("updated_parsed"):
        tm = entry.get("updated_parsed")
        return date(tm.tm_year, tm.tm_mon, tm.tm_mday)

    for key in ("published", "updated", "created"):
        raw = entry.get(key)
        if not raw:
            continue
        parsed = try_parse_date_string(str(raw))
        if parsed:
            return parsed
    return None


def try_parse_date_string(raw: str) -> Optional[date]:
    raw = raw.strip()
    if not raw:
        return None

    try:
        return parsedate_to_datetime(raw).date()
    except Exception:
        pass

    iso_candidate = raw.replace("Z", "+00:00")
    try:
        return datetime.fromisoformat(iso_candidate).date()
    except Exception:
        return None


def topic_match(text: str) -> bool:
    lowered = text.lower()
    return any(term in lowered for term in TOPIC_TERMS)


def safe_atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", delete=False, dir=path.parent) as tmp:
        tmp.write(content)
        tmp_path = Path(tmp.name)
    tmp_path.replace(path)


def load_processed_sources(path: Path) -> List[dict]:
    if not path.exists():
        return []

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logging.warning("Processed sources file was invalid JSON; starting from empty set.")
        return []

    if isinstance(payload, dict) and isinstance(payload.get("sources"), list):
        return [item for item in payload["sources"] if isinstance(item, dict)]
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    return []


def save_processed_sources(path: Path, records: List[dict]) -> None:
    records_sorted = sorted(
        records,
        key=lambda item: (
            item.get("publication_date", ""),
            normalize_title(item.get("title", "")),
            normalize_url(item.get("url", "")),
        ),
        reverse=True,
    )
    payload = {"sources": records_sorted}
    safe_atomic_write(path, json.dumps(payload, indent=2, ensure_ascii=False) + "\n")


def fetch_feed(feed: FeedSource) -> Optional[feedparser.FeedParserDict]:
    request = Request(feed.url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            feed_bytes = response.read()
    except Exception as exc:
        logging.warning("Failed to fetch feed '%s': %s", feed.publication, exc)
        return None

    parsed = feedparser.parse(feed_bytes)
    if getattr(parsed, "bozo", False):
        logging.warning("Malformed feed payload for '%s': %s", feed.publication, parsed.bozo_exception)
    return parsed


def resolve_google_news_link(url: str) -> str:
    parsed = urlparse(url)
    if "news.google.com" not in parsed.netloc:
        return url

    request = Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urlopen(request, timeout=REQUEST_TIMEOUT_SECONDS) as response:
            final_url = response.geturl()
            if final_url:
                return final_url
    except Exception:
        pass
    return url


def to_source_entry(feed: FeedSource, item: dict) -> Optional[SourceEntry]:
    raw_title = strip_html(item.get("title", ""))
    if not raw_title:
        return None

    raw_link = (item.get("link") or "").strip()
    if not raw_link:
        return None

    parsed_date = parse_date_from_entry(item)
    if not parsed_date:
        logging.info("Skipping '%s' from %s due to missing/invalid publication date.", raw_title, feed.publication)
        return None
    if parsed_date <= CUTOFF_DATE:
        return None

    summary = strip_html(item.get("summary", "") or item.get("description", ""))
    combined_text = f"{raw_title} {summary}"
    if not topic_match(combined_text):
        return None

    author = strip_html(item.get("author", "") or "Unknown")
    publication = strip_html(feed.publication)
    resolved_link = resolve_google_news_link(raw_link)
    normalized_link = normalize_url(resolved_link)
    if not normalized_link:
        return None

    if len(summary) > MAX_SUMMARY_LENGTH:
        summary = summary[: MAX_SUMMARY_LENGTH - 1].rstrip() + "…"

    if not summary:
        summary = "Summary not available from feed metadata."

    return SourceEntry(
        title=raw_title,
        author=author,
        publication=publication,
        publication_date=parsed_date.isoformat(),
        url=normalized_link,
        description=summary,
    )


def extract_existing_reference_signatures(reference_text: str) -> Tuple[Set[str], Set[str], Set[Tuple[str, str]]]:
    urls: Set[str] = set()
    titles: Set[str] = set()
    title_date_pairs: Set[Tuple[str, str]] = set()

    lines = reference_text.splitlines()
    for line in lines:
        for title, url in MARKDOWN_LINK_RE.findall(line):
            normalized_url = normalize_url(url)
            if normalized_url:
                urls.add(normalized_url)
            normalized_title = normalize_title(title)
            if normalized_title:
                titles.add(normalized_title)

    last_title: Optional[str] = None
    for line in lines:
        link_match = MARKDOWN_LINK_RE.search(line)
        if link_match:
            last_title = normalize_title(link_match.group(1))
            continue

        date_match = DATE_RE.search(line)
        if last_title and date_match:
            title_date_pairs.add((last_title, date_match.group(1)))

    return urls, titles, title_date_pairs


def parse_recent_section_entries(reference_text: str) -> List[SourceEntry]:
    lines = reference_text.splitlines()
    try:
        start = lines.index(RECENT_SECTION_TITLE)
    except ValueError:
        return []

    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## ") and lines[idx] != RECENT_SECTION_TITLE:
            end = idx
            break
        if lines[idx].startswith("# "):
            end = idx
            break

    section_lines = lines[start + 1 : end]
    entries: List[SourceEntry] = []
    i = 0
    while i < len(section_lines):
        line = section_lines[i]
        if not line.startswith("- ### "):
            i += 1
            continue

        link_match = MARKDOWN_LINK_RE.search(line)
        if not link_match:
            i += 1
            continue

        title = strip_html(link_match.group(1))
        url = normalize_url(link_match.group(2))

        author = "Unknown"
        publication = "Unknown"
        publication_date = ""
        description = "Summary not available from feed metadata."

        j = i + 1
        while j < len(section_lines) and not section_lines[j].startswith("- ### "):
            meta_match = META_RE.search(section_lines[j].strip())
            if meta_match:
                publication = strip_html(meta_match.group("publication"))
                publication_date = meta_match.group("date")
                author = strip_html(meta_match.group("author"))
            elif section_lines[j].strip() and section_lines[j].strip() not in {"***", "---"}:
                description = strip_html(section_lines[j].strip())
            j += 1

        if title and url and publication_date:
            entries.append(
                SourceEntry(
                    title=title,
                    author=author,
                    publication=publication,
                    publication_date=publication_date,
                    url=url,
                    description=description,
                )
            )
        i = j

    return entries


def deduplicate_entries(entries: Iterable[SourceEntry]) -> List[SourceEntry]:
    by_url: Set[str] = set()
    by_title: Set[str] = set()
    by_title_date: Set[Tuple[str, str]] = set()
    unique: List[SourceEntry] = []

    for entry in entries:
        normalized_url = normalize_url(entry.url)
        normalized_title = entry.normalized_title
        title_date = (normalized_title, entry.publication_date)

        if normalized_url in by_url:
            continue
        if normalized_title in by_title:
            continue
        if title_date in by_title_date:
            continue

        by_url.add(normalized_url)
        by_title.add(normalized_title)
        by_title_date.add(title_date)
        unique.append(entry)

    unique.sort(
        key=lambda item: (
            item.publication_date,
            item.publication.lower(),
            item.normalized_title,
        ),
        reverse=True,
    )
    return unique


def render_recent_section(entries: List[SourceEntry]) -> str:
    lines: List[str] = [RECENT_SECTION_TITLE, ""]
    for entry in entries:
        lines.append(f"- ### [{entry.title}]({entry.url})")
        lines.append("")
        lines.append(
            f"  _Publication:_ {entry.publication} | _Date:_ {entry.publication_date} | _Author:_ {entry.author or 'Unknown'}"
        )
        lines.append("")
        lines.append(f"  {entry.description}")
        lines.append("")
        lines.append("  ***")
        lines.append("")
    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def upsert_recent_section(reference_text: str, rendered_section: str) -> str:
    lines = reference_text.splitlines()
    try:
        start = lines.index(RECENT_SECTION_TITLE)
    except ValueError:
        insertion_marker = "# Podcasts & Multimedia"
        if insertion_marker in lines:
            insert_at = lines.index(insertion_marker)
            prefix = "\n".join(lines[:insert_at]).rstrip("\n")
            suffix = "\n".join(lines[insert_at:]).lstrip("\n")
            pieces = [prefix, rendered_section, suffix]
            return "\n\n".join(piece for piece in pieces if piece) + "\n"

        fallback = reference_text.rstrip("\n")
        return f"{fallback}\n\n{rendered_section}\n"

    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if lines[idx].startswith("## ") and lines[idx] != RECENT_SECTION_TITLE:
            end = idx
            break
        if lines[idx].startswith("# "):
            end = idx
            break

    updated_lines = lines[:start] + rendered_section.splitlines() + lines[end:]
    return "\n".join(updated_lines).rstrip("\n") + "\n"


def collect_entries(existing_reference_text: str, processed_records: List[dict]) -> List[SourceEntry]:
    existing_urls, existing_titles, existing_title_date = extract_existing_reference_signatures(existing_reference_text)

    processed_urls = {normalize_url(item.get("url", "")) for item in processed_records if item.get("url")}
    processed_titles = {normalize_title(item.get("title", "")) for item in processed_records if item.get("title")}
    processed_title_date = {
        (normalize_title(item.get("title", "")), item.get("publication_date", ""))
        for item in processed_records
        if item.get("title") and item.get("publication_date")
    }

    new_entries: List[SourceEntry] = []

    for feed in FEEDS:
        parsed_feed = fetch_feed(feed)
        if parsed_feed is None:
            continue

        for raw_item in parsed_feed.entries:
            entry = to_source_entry(feed, raw_item)
            if entry is None:
                continue

            normalized_url = normalize_url(entry.url)
            normalized_title = entry.normalized_title
            title_date = (normalized_title, entry.publication_date)

            if normalized_url in existing_urls or normalized_url in processed_urls:
                continue
            if normalized_title in existing_titles or normalized_title in processed_titles:
                continue
            if title_date in existing_title_date or title_date in processed_title_date:
                continue

            new_entries.append(entry)

            existing_urls.add(normalized_url)
            existing_titles.add(normalized_title)
            existing_title_date.add(title_date)
            processed_urls.add(normalized_url)
            processed_titles.add(normalized_title)
            processed_title_date.add(title_date)

    return deduplicate_entries(new_entries)


def update_reference_library() -> int:
    if not REFERENCE_LIBRARY_PATH.exists():
        raise FileNotFoundError(f"Reference library not found: {REFERENCE_LIBRARY_PATH}")

    existing_reference_text = REFERENCE_LIBRARY_PATH.read_text(encoding="utf-8")
    processed_records = load_processed_sources(PROCESSED_SOURCES_PATH)

    existing_recent_entries = parse_recent_section_entries(existing_reference_text)
    new_entries = collect_entries(existing_reference_text, processed_records)

    if not new_entries:
        logging.info("No new qualifying references found after %s.", CUTOFF_DATE.isoformat())
        print("NEW_REFERENCES_COUNT=0")
        return 0

    combined_entries = deduplicate_entries([*existing_recent_entries, *new_entries])
    rendered_section = render_recent_section(combined_entries)
    updated_reference_text = upsert_recent_section(existing_reference_text, rendered_section)

    if updated_reference_text != existing_reference_text:
        safe_atomic_write(REFERENCE_LIBRARY_PATH, updated_reference_text)

    combined_processed = processed_records + [
        {
            "title": entry.title,
            "author": entry.author,
            "publication": entry.publication,
            "publication_date": entry.publication_date,
            "url": entry.url,
            "description": entry.description,
        }
        for entry in new_entries
    ]
    save_processed_sources(PROCESSED_SOURCES_PATH, combined_processed)

    logging.info("Added %s new references.", len(new_entries))
    print(f"NEW_REFERENCES_COUNT={len(new_entries)}")
    return 0


def main() -> int:
    configure_logging()
    try:
        return update_reference_library()
    except Exception as exc:
        logging.error("Reference update failed: %s", exc)
        print("NEW_REFERENCES_COUNT=0")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
