import unittest, crypto as c

class T(unittest.TestCase):
    def test_run(self):
        r = c.benchmark.run(sizes=(1024,))[1024]
        self.assertEqual(set(r), {"Caesar", "Vigenère", "AES-256-GCM", "SHA-256"}); self.assertTrue(all(v > 0 for v in r.values()))
