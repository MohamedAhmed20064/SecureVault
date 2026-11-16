import unittest, crypto as c

class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.priv, cls.pub = c.rsa_generate(2048)
    def test_encrypt(self):
        self.assertEqual(c.rsa_decrypt(c.rsa_encrypt("hi", self.pub), self.priv), "hi")
        with self.assertRaises(ValueError): c.rsa_encrypt("a" * 300, self.pub)
    def test_signature(self):
        s = c.sign("Transfer 500 EGP", self.priv)
        self.assertTrue(c.verify("Transfer 500 EGP", s, self.pub))
        self.assertFalse(c.verify("Transfer 5000 EGP", s, self.pub))
        self.assertFalse(c.verify("Transfer 500 EGP", "garbage", self.pub))
