import unittest
from host_yarn_bridge.redaction import redact

class TestRedact(unittest.TestCase):
    def test_bearer(self):
        out,n = redact("Authorization: Bearer supersecretvalue")
        self.assertIn("***", out)
        self.assertGreaterEqual(n,1)
    def test_ghp(self):
        out,n = redact("token ghp_abcdefghijklmnopqrstuvwxyz012345")
        self.assertIn("ghp_***", out)

if __name__ == '__main__':
    unittest.main()
