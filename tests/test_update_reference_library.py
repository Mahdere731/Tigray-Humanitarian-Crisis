from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from update_reference_library import (  # noqa: E402
    CandidateItem,
    deduplicate_candidates,
    insert_items,
    parse_date,
)


class UpdateReferenceLibraryTests(unittest.TestCase):
    def test_parse_date_filters_invalid(self) -> None:
        self.assertEqual(str(parse_date("2026-09-26T13:00:00Z")), "2026-09-26")
        self.assertIsNone(parse_date("not-a-date"))
        self.assertIsNone(parse_date(None))

    def test_deduplicate_candidates_against_existing_markdown(self) -> None:
        markdown = (
            "## **Reuters**\n\n"
            "- ### [Sample Reuters Item](https://www.reuters.com/world/africa/example)\n\n"
            "  ***\n"
        )
        candidates = [
            CandidateItem(
                source_name="Reuters",
                section_heading="## **Reuters**",
                title="Sample Reuters Item",
                url="https://reuters.com/world/africa/example",
                publication_date="2026-09-28",
                publication="Reuters",
                author=None,
                description="desc",
            ),
            CandidateItem(
                source_name="Reuters",
                section_heading="## **Reuters**",
                title="New Reuters Item",
                url="https://reuters.com/world/africa/new-item",
                publication_date="2026-09-29",
                publication="Reuters",
                author=None,
                description="desc",
            ),
        ]
        accepted = deduplicate_candidates(candidates, markdown, [])
        self.assertEqual(len(accepted), 1)
        self.assertEqual(accepted[0].title, "New Reuters Item")

    def test_insert_items_creates_recent_section_when_missing(self) -> None:
        original = "# Reference Library of the Tigray Crisis\n\n## **BBC**\n\n---\n"
        new_item = CandidateItem(
            source_name="AFP",
            section_heading="## Recent Sources (Post September 25, 2026)",
            title="AFP item",
            url="https://www.afp.com/en/test-article/2026-09-28",
            publication_date="2026-09-28",
            publication="AFP",
            author=None,
            description="desc",
        )
        updated = insert_items(original, [new_item])
        self.assertIn("## Recent Sources (Post September 25, 2026)", updated)
        self.assertIn("- ### [AFP item](https://www.afp.com/en/test-article/2026-09-28)", updated)
        self.assertIn("## **BBC**", updated)


if __name__ == "__main__":
    unittest.main()
