from unittest import TestCase

from wiktextract.extractor.el.tags import base_tag_map
from wiktextract.tags import valid_tags


class TestElTags(TestCase):
    def test_validate_tags(self) -> None:
        # Check validity of manually entered tags in base_tag_map.
        # valid_tags is from higher level code, originally created for the English
        # extractor but also applicable to other extractors: these are the tags
        # that should be used for tagging. Can be added to when needed, but
        # often there's already an equivalent tag with a slightly different name.
        for tags in base_tag_map.values():
            for tag in tags:
                for part in tag.split("-"):
                    if not part.isalpha() or (
                        part.islower() and tag not in valid_tags
                    ):
                        self.assertFalse(
                            f"Invalid tag in tag_map: {tag=}"
                        )
                        break
