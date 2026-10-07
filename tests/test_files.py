"""pnkit.files: approved files are write-once."""
import os, shutil, sys, tempfile, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pnkit import files


class WriteOnce(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="pnkit-files-")
        self.p = os.path.join(self.tmp, "excerpt.wav")

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def test_writes_a_new_file_and_returns_the_path(self):
        self.assertEqual(files.write_once(self.p, b"approved"), self.p)
        self.assertEqual(open(self.p, "rb").read(), b"approved")

    def test_str_is_written_as_utf8(self):
        files.write_once(self.p, "áé")
        self.assertEqual(open(self.p, "rb").read(), "áé".encode())

    def test_existing_path_raises_and_keeps_the_bytes(self):
        files.write_once(self.p, b"approved")
        with self.assertRaises(files.WriteOnceError):
            files.write_once(self.p, b"rerun")
        self.assertEqual(open(self.p, "rb").read(), b"approved")

    def test_error_is_a_file_exists_error(self):
        files.write_once(self.p, b"x")
        with self.assertRaises(FileExistsError):
            files.write_once(self.p, b"y")

    def test_empty_existing_file_still_counts(self):
        open(self.p, "wb").close()
        with self.assertRaises(files.WriteOnceError):
            files.write_once(self.p, b"y")

    def test_dangling_symlink_counts_as_existing(self):
        os.symlink(os.path.join(self.tmp, "nowhere"), self.p)
        with self.assertRaises(files.WriteOnceError):
            files.write_once(self.p, b"y")
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "nowhere")))

    def test_next_free_returns_the_path_when_free(self):
        self.assertEqual(files.next_free(self.p), self.p)

    def test_next_free_counts_up(self):
        files.write_once(self.p, b"1")
        v2 = os.path.join(self.tmp, "excerpt-v2.wav")
        self.assertEqual(files.next_free(self.p), v2)
        files.write_once(v2, b"2")
        self.assertEqual(files.next_free(self.p), os.path.join(self.tmp, "excerpt-v3.wav"))

    def test_next_free_custom_suffix_and_no_extension(self):
        q = os.path.join(self.tmp, "NOTES")
        files.write_once(q, b"1")
        self.assertEqual(files.next_free(q, suffix="_rev"), q + "_rev2")

    def test_write_next_never_touches_the_approved_file(self):
        files.write_once(self.p, b"approved")
        w = files.write_next(self.p, b"new")
        self.assertEqual(w, os.path.join(self.tmp, "excerpt-v2.wav"))
        self.assertEqual(open(self.p, "rb").read(), b"approved")
        self.assertEqual(open(w, "rb").read(), b"new")
        self.assertEqual(files.write_next(self.p, b"newer"), os.path.join(self.tmp, "excerpt-v3.wav"))

    def test_write_next_on_a_free_path_writes_it(self):
        self.assertEqual(files.write_next(self.p, b"a"), self.p)


if __name__ == "__main__":
    unittest.main()
