from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from dsgf.hashing import ddl_hash, normalize_ddl


class HashingTests(unittest.TestCase):
    def test_normalize_ddl_ignores_comments_and_case(self):
        left = "CREATE TABLE x (id STRING); -- comment"
        right = "create   table x (id string)"
        self.assertEqual(normalize_ddl(left), normalize_ddl(right))
        self.assertEqual(ddl_hash(left), ddl_hash(right))


if __name__ == "__main__":
    unittest.main()
