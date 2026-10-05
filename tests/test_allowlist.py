import unittest
from host_yarn_bridge.allowlist import validate_request

BASE = {
    "operation": "yarn-degradation-curve",
    "host": "f6a8",
    "seat": "hyperqwen",
    "artifact_root": "/home/odnt/RND/uow7-inference-recipe-rollout",
    "request_timeout_seconds": 1200,
}

class TestAllowlist(unittest.TestCase):
    def test_ok(self):
        self.assertEqual(validate_request(dict(BASE)), 1200)
    def test_reject_command(self):
        b=dict(BASE); b["command"]=["sh"]
        with self.assertRaises(ValueError):
            validate_request(b)
    def test_reject_host(self):
        b=dict(BASE); b["host"]="nazgul"
        with self.assertRaises(ValueError):
            validate_request(b)
    def test_reject_timeout(self):
        b=dict(BASE); b["request_timeout_seconds"]=1201
        with self.assertRaises(ValueError):
            validate_request(b)

if __name__ == '__main__':
    unittest.main()
