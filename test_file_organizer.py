import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

from file_organizer import categorize, main, organize


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

    def test_reports_files_in_sorted_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for name in ("c.txt", "a.png", "b.mp3"):
                (directory / name).write_text("x")

            moved = organize(directory)

            self.assertEqual([name for name, _ in moved], ["a.png", "b.mp3", "c.txt"])

    def test_does_not_overwrite_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            (directory / "images").mkdir()
            (directory / "images" / "photo.jpg").write_text("old")
            (directory / "images" / "photo (1).jpg").write_text("older")
            (directory / "photo.jpg").write_text("new")

            organize(directory)

            self.assertEqual((directory / "images" / "photo.jpg").read_text(), "old")
            self.assertEqual((directory / "images" / "photo (1).jpg").read_text(), "older")
            self.assertEqual((directory / "images" / "photo (2).jpg").read_text(), "new")
            self.assertFalse((directory / "photo.jpg").exists())

    def test_blocked_category_skips_only_that_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            for name in ("a.txt", "others", "z.jpg"):
                (directory / name).write_text("x")
            errors = []

            moved = organize(directory, on_error=lambda path, error: errors.append(path.name))

            self.assertEqual(moved, [("a.txt", "documents"), ("z.jpg", "images")])
            self.assertEqual(errors, ["others"])
            self.assertTrue((directory / "images" / "z.jpg").exists())
            self.assertTrue((directory / "others").is_file())


class MainTest(unittest.TestCase):

    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            try:
                code = main(argv)
            except SystemExit as exc:
                code = exc.code
        return code, out.getvalue(), err.getvalue()

    def test_dry_run_reports_without_moving(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "photo.jpg").write_text("x")
            code, out, _ = self.run_main([tmp, "--dry-run"])
            self.assertTrue((Path(tmp) / "photo.jpg").exists())
        self.assertEqual(code, 0)
        self.assertIn("photo.jpg -> images/", out)
        self.assertIn("1 file(s) would be moved.", out)

    def test_unmovable_file_is_reported_and_others_still_move(self):
        with tempfile.TemporaryDirectory() as tmp:
            for name in ("a.txt", "others", "z.jpg"):
                (Path(tmp) / name).write_text("x")
            code, out, err = self.run_main([tmp])
            self.assertTrue((Path(tmp) / "images" / "z.jpg").exists())
        self.assertEqual(code, 1)
        self.assertIn("a.txt -> documents/", out)
        self.assertIn("z.jpg -> images/", out)
        self.assertIn("2 file(s) moved.", out)
        self.assertIn("could not move others: others exists and is not a folder", err)
        self.assertIn("1 file(s) could not be moved.", err)

    def test_empty_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, out, _ = self.run_main([tmp])
        self.assertEqual(code, 0)
        self.assertIn("No files to organize.", out)

    def test_missing_directory_is_an_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            code, _, err = self.run_main([str(Path(tmp) / "missing")])
        self.assertEqual(code, 2)
        self.assertIn("not a directory", err)


if __name__ == "__main__":
    unittest.main()
