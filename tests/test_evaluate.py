import json, unittest
from ai import evaluate

class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.r = evaluate.report()
    def test_advisor_accuracy_on_unseen_sentences(self):
        a = self.r["advisor"]; self.assertGreaterEqual(a["accuracy"], 0.85); self.assertEqual(a["test"], 40)
    def test_password_accuracy(self):
        self.assertGreaterEqual(self.r["password"]["hand_accuracy"], 0.9)
    def test_report_is_json_ready(self):
        json.dumps(self.r)
