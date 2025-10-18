from unittest import TestCase

from wiktextract.extractor.el.tags import tag_map, topic_map
from wiktextract.tags import valid_tags
from wiktextract.topics import valid_topics


class TestElTags(TestCase):
    """WARNING:

    The results differ when running these tests via unittest or manually here
    as TestElTags().test_validate_tags. This is due to side effects adding more
    tags/topics when running it via unittest.

    As of the writting of this warning, there are (standalone/unittest):
    - Tags   1315 / 3365
    - Topics 227  / 854

    This explains why some topics like "computer" pass these tests, even though
    only "computing" is found in the original valid_topics.
    """

    def test_validate_tags(self) -> None:
        # Check validity of manually entered tags in tag_map.
        # valid_tags is from higher level code, originally created for the English
        # extractor but also applicable to other extractors: these are the tags
        # that should be used for tagging. Can be added to when needed, but
        # often there's already an equivalent tag with a slightly different name.
        for tags in tag_map.values():
            for tag in tags:
                for part in tag.split("-"):
                    if not part.isalpha() or (
                        part.islower() and tag not in valid_tags
                    ):
                        self.assertFalse(f"Invalid tag in tag_map: {tag=}")

    def test_validate_topics(self) -> None:
        for topics in topic_map.values():
            for topic in topics:
                for part in topic.split("-"):
                    if not part.isalpha() or (
                        part.islower() and topic not in valid_topics
                    ):
                        self.assertFalse(
                            f"Invalid topic in topic_map: {topic=}"
                        )
