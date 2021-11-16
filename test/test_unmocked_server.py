import unittest
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

from spotify import extract_song_data, get_combined_song_artists_string

INPUT = "INPUT"
EXPECTED_OUTPUT = "EXPECTED_OUTPUT"

"""
VERSION 1: USING TEST PARAMS IN setUp()
"""


class GetSongDataTests(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                INPUT: {},
                EXPECTED_OUTPUT: (None, None, None, None),
            },
            {
                INPUT: {"name": "Song Name"},
                EXPECTED_OUTPUT: ("Song Name", None, None, None),
            },
            {
                INPUT: {
                    "name": "Song Name",
                    "artists": [{"name": "Artist"}],
                    "album": {"images": [{"url": "image_url"}]},
                    "preview_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                },
                EXPECTED_OUTPUT: (
                    "Song Name",
                    "Artist",
                    "image_url",
                    "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                ),
            },
        ]

    def test_extract_song_data(self):
        for test in self.success_test_params:
            self.assertEqual(extract_song_data(test[INPUT]), test[EXPECTED_OUTPUT])


class GetCombinedSongArtistsStringTests(unittest.TestCase):
    def setUp(self):
        self.success_test_params = [
            {
                INPUT: [],
                EXPECTED_OUTPUT: "",
            },
            {
                INPUT: [{"name": "Artist1"}],
                EXPECTED_OUTPUT: "Artist1",
            },
            {
                INPUT: [{"name": "Artist1"}, {"name": "Artist2"}],
                EXPECTED_OUTPUT: "Artist1, Artist2",
            },
        ]

    def test_get_combined_song_artists_string(self):
        for test in self.success_test_params:
            self.assertEqual(
                get_combined_song_artists_string(test[INPUT]), test[EXPECTED_OUTPUT]
            )


"""
VERSION 2: ONE TEST CASE PER FUNCTION
This is the test case organization method I prefer, but I didn't
cover it in class. Note how it frees us up to test multiple helper
functions in a single class.
"""


class SpotifyHelperTests(unittest.TestCase):
    def test_extract_song_data_1(self):
        self.assertEqual(extract_song_data({}), (None, None, None, None))

    def test_extract_song_data_2(self):
        self.assertEqual(
            extract_song_data({"name": "Song Name"}), ("Song Name", None, None, None)
        )

    def test_extract_song_data_3(self):
        # This is a big enough JSON that we should probably split it out for
        # readability
        song_json = {
            "name": "Song Name",
            "artists": [{"name": "Artist"}],
            "album": {"images": [{"url": "image_url"}]},
            "preview_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        }
        self.assertEqual(
            extract_song_data(song_json),
            (
                "Song Name",
                "Artist",
                "image_url",
                "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
            ),
        )

    def test_get_combined_song_artists_string_1(self):
        self.assertEqual(get_combined_song_artists_string([]), "")

    def test_get_combined_song_artists_string_3(self):
        self.assertEqual(
            get_combined_song_artists_string([{"name": "Artist1"}]), "Artist1"
        )

    def test_get_combined_song_artists_string_2(self):
        self.assertEqual(
            get_combined_song_artists_string(
                [{"name": "Artist1"}, {"name": "Artist2"}]
            ),
            "Artist1, Artist2",
        )


if __name__ == "__main__":
    unittest.main()