import unittest, ai

class T(unittest.TestCase):
    def test_weak(self):
        for p in ("123456", "password", "qwerty123", "ahmed2005"): self.assertEqual(ai.password_strength(p)["label"], "weak", p)
    def test_strong(self):
        for p in ("k7#Qz!p9Lm2$vR8x", "correct-horse-battery-staple-91"): self.assertEqual(ai.password_strength(p)["label"], "strong", p)
    def test_tips_and_score(self):
        r = ai.password_strength("abc"); self.assertTrue(r["tips"]); self.assertLess(r["score"], 40)
        self.assertGreater(ai.password_strength("Xv9$mT2@qLp7!nWz")["score"], 80)
    def test_empty(self):
        self.assertEqual(ai.password_strength("")["score"], 0)
