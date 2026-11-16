import unittest, ai

class T(unittest.TestCase):
    def test_detect(self):
        t = "card 4111 1111 1111 1111, id 29901011234567, mail a@b.com, password: hunter2"
        self.assertEqual({f[0] for f in ai.detect(t)}, {"Credit card number", "National ID", "Email address", "Password / secret"})
    def test_no_false_positive(self):
        self.assertEqual(ai.detect("Meet at 5pm, room 1234567, order 1234 5678 9012 3456"), [])
    def test_mask(self):
        self.assertNotIn("a@b.com", ai.mask("mail a@b.com"))
