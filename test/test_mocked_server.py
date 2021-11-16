import unittest
from unittest.mock import MagicMock, patch

import sys
import os

# getting the name of the directory
# where the this file is present.
current = os.path.dirname(os.path.realpath(__file__))

# Getting the parent directory name
# where the current directory is present.
parent = os.path.dirname(current)

# adding the parent directory to
# the sys.path.
sys.path.append(parent)

from app import update_db_ids_for_user, Artist
from genius import get_lyrics_link

INPUT = "INPUT"
EXPECTED_OUTPUT = "EXPECTED_OUTPUT"


class UpdateDBIDsTests(unittest.TestCase):
    def setUp(self):
        self.db_mock = [Artist(artist_id="foo", username="John")]

    def mock_add_to_db(self, artist):
        self.db_mock.append(artist)

    def mock_delete_from_db(self, artist):
        self.db_mock = [
            entry for entry in self.db_mock if entry.artist_id != artist.artist_id
        ]

    def mock_db_commit(self):
        pass

    def test_update_db_ids_for_user(self):
        with patch("app.Artist.query") as mock_query:
            with patch("app.db.session.add", self.mock_add_to_db):
                with patch("app.db.session.delete", self.mock_delete_from_db):
                    with patch("app.db.session.commit", self.mock_db_commit):
                        mock_filtered = MagicMock()
                        mock_filtered.all.return_value = self.db_mock
                        # Hard-coding in some logic from test case 3.
                        # This is because SQLAlchemy is just kinda hard to mock
                        # in some instances
                        mock_filtered.filter.return_value = [
                            Artist(artist_id="bar", username="John")
                        ]
                        mock_query.filter_by.return_value = mock_filtered

                        # Now that setup is done...
                        # 1) Try to add the same ID to the DB. Should be a no-op.
                        update_db_ids_for_user("John", {"foo"})
                        self.assertEqual(len(self.db_mock), 1)
                        self.assertEqual(self.db_mock[0].artist_id, "foo")

                        # 2) Try to add a new ID to the DB. Should expand the DB
                        # collection
                        update_db_ids_for_user("John", {"foo", "bar"})
                        self.assertEqual(len(self.db_mock), 2)
                        self.assertEqual(self.db_mock[0].artist_id, "foo")
                        self.assertEqual(self.db_mock[1].artist_id, "bar")

                        # 3) Pass in a list of valid IDs that doesn't include a prior
                        # one. Should replace "bar" with "baz"
                        update_db_ids_for_user("John", {"foo", "baz"})
                        self.assertEqual(len(self.db_mock), 2)
                        self.assertEqual(self.db_mock[0].artist_id, "foo")
                        self.assertEqual(self.db_mock[1].artist_id, "baz")


class GetLyricsLinkTests(unittest.TestCase):
    def test_get_lyrics_link(self):
        with patch("genius.requests.get") as mock_requests_get:
            mock_response = MagicMock()
            # side_effect lets us set a list of return values.
            # Each successive call to mock_response.all() will generate the next
            # side effect
            mock_response.json.side_effect = [
                {},
                {
                    "response": {
                        "hits": [
                            {
                                "result": {
                                    "url": "https://www.youtube.com/watch?v=q6EoRBvdVPQ"
                                }
                            }
                        ]
                    }
                },
            ]
            mock_requests_get.return_value = mock_response

            self.assertEqual(get_lyrics_link("Song Name"), None)
            self.assertEqual(
                get_lyrics_link("Song Name 2"),
                "https://www.youtube.com/watch?v=q6EoRBvdVPQ",
            )


if __name__ == "__main__":
    unittest.main()
