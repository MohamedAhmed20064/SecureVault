import unittest, crypto as c

class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.priv, cls.pub = c.rsa_generate(2048); cls.other, _ = c.rsa_generate(2048)
    def test_long_message(self):
        m = "long message " * 500
        self.assertEqual(c.hybrid_decrypt(c.hybrid_encrypt(m, self.pub), self.priv), m)
    def test_wrong_private_key(self):
        with self.assertRaises(ValueError): c.hybrid_decrypt(c.hybrid_encrypt("hi", self.pub), self.other)
    def test_garbage(self):
        with self.assertRaises(ValueError): c.hybrid_decrypt("not-a-package", self.priv)
