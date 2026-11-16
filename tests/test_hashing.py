import unittest, crypto as c

class T(unittest.TestCase):
    def test_sha256(self):
        self.assertEqual(c.sha256("abc"), "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")
