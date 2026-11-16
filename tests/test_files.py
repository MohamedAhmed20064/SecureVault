import unittest, os, tempfile, crypto as c

class T(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp(); self.src = os.path.join(self.d, "a.bin"); self.enc = self.src + ".svlt"; self.out = os.path.join(self.d, "o.bin")
        self.data = os.urandom(5000); open(self.src, "wb").write(self.data)
    def test_roundtrip(self):
        c.encrypt_file(self.src, self.enc, "pw"); c.decrypt_file(self.enc, self.out, "pw")
        self.assertEqual(open(self.out, "rb").read(), self.data)
        self.assertNotIn(self.data[:50], open(self.enc, "rb").read())
    def test_wrong_password(self):
        c.encrypt_file(self.src, self.enc, "pw")
        with self.assertRaises(ValueError): c.decrypt_file(self.enc, self.out, "bad")
    def test_modified_file(self):
        c.encrypt_file(self.src, self.enc, "pw"); b = bytearray(open(self.enc, "rb").read()); b[-5] ^= 1; open(self.enc, "wb").write(bytes(b))
        with self.assertRaises(ValueError): c.decrypt_file(self.enc, self.out, "pw")
    def test_not_svlt(self):
        with self.assertRaises(ValueError): c.decrypt_file(self.src, self.out, "pw")
