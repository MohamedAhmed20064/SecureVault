import unittest, base64, crypto as c

class T(unittest.TestCase):
    def test_roundtrip_and_wrong_key(self):
        t = c.aes_encrypt("secret msg", "pw123")
        self.assertEqual(c.aes_decrypt(t, "pw123"), "secret msg")
        with self.assertRaises(ValueError): c.aes_decrypt(t, "wrong")
    def test_tampered(self):
        raw = bytearray(base64.b64decode(c.aes_encrypt("secret", "pw"))); raw[-1] ^= 1
        with self.assertRaises(ValueError): c.aes_decrypt(base64.b64encode(bytes(raw)).decode(), "pw")
    def test_empty_password(self):
        with self.assertRaises(ValueError): c.aes_encrypt("x", "")
