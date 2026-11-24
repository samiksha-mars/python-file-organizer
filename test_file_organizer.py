import tempfile
import unittest
from pathlib import Path

from file_organizer import categorize, organize


class CategorizeTest(unittest.TestCase):

    def test_image(self):
        self.assertEqual(categorize(".png"), "images")

    def test_document(self):
        self.assertEqual(categorize(".pdf"), "documents")

    def test_code(self):
        self.assertEqual(categorize(".py"), "code")

    def test_case_insensitive(self):
        self.assertEqual(categorize(".JPG"), "images")

    def test_unknown_extension(self):
        self.assertEqual(categorize(".xyz"), "others")


class OrganizeTest(unittest.TestCase):

    def test_moves_files_into_categories(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "photo.jpg").write_text("x")
            (directory / "notes.txt").write_text("x")
            (directory / "song.mp3").write_text("x")

            moved = organize(directory)

            self.assertEqual(len(moved), 3)
            self.assertTrue((directory / "images" / "photo.jpg").exists())
            self.assertTrue((directory / "documents" / "notes.txt").exists())
            self.assertTrue((directory / "audio" / "song.mp3").exists())

    def test_dry_run_does_not_move(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "photo.jpg").write_text("x")

            moved = organize(directory, dry_run=True)

            self.assertEqual(moved, [("photo.jpg", "images")])
            self.assertTrue((directory / "photo.jpg").exists())
            self.assertFalse((directory / "images").exists())

    def test_ignores_hidden_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / ".hidden").write_text("x")
            (directory / "readme.md").write_text("x")

            moved = organize(directory)

            self.assertEqual(moved, [("readme.md", "documents")])


if __name__ == "__main__":
    unittest.main()
