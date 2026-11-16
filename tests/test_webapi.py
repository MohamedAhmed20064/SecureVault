import unittest, base64, os, tempfile
from webgui.api import Api

class T(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.a = Api()
    def test_scan(self):
        r = self.a.scan("card 4111 1111 1111 1111 mail a@b.com")
        self.assertEqual({f["name"] for f in r["findings"]}, {"Credit card number", "Email address"}); self.assertGreater(r["risk"], 0)
        self.assertEqual(self.a.scan("  ")["risk"], 0)
    def test_crypt_roundtrip_and_errors(self):
        e = self.a.crypt("AES-256-GCM", "encrypt", "hello", "pw"); self.assertTrue(e["ok"])
        self.assertEqual(self.a.crypt("AES-256-GCM", "decrypt", e["out"], "pw")["out"], "hello")
        self.assertFalse(self.a.crypt("AES-256-GCM", "decrypt", e["out"], "bad")["ok"])
        self.assertEqual(self.a.crypt("Caesar Cipher", "encrypt", "abc", "3")["out"], "def")
        self.assertFalse(self.a.crypt("Caesar Cipher", "encrypt", "abc", "x")["ok"])
        self.assertFalse(self.a.crypt("SHA-256 Hash", "encrypt", "abc", "")["ok"])
    def test_sign_and_tests(self):
        s = self.a.sign("Transfer 500 EGP")["out"]
        self.assertTrue(self.a.verify("Transfer 500 EGP", s)["valid"]); self.assertFalse(self.a.verify("Transfer 5000 EGP", s)["valid"])
        t = self.a.run_tests("Transfer 500 EGP to account 1234")["tests"]; self.assertEqual([x["state"] for x in t], ["ok", "bad", "warn"])
    def test_hybrid(self):
        e = self.a.hybrid("encrypt", "long " * 200); self.assertEqual(self.a.hybrid("decrypt", e["out"])["out"], "long " * 200)
    def test_file_b64(self):
        data = os.urandom(3000); e = self.a.file_op_b64("encrypt", "x.bin", base64.b64encode(data).decode(), "pw")
        d = self.a.file_op_b64("decrypt", e["name"], e["b64"], "pw"); self.assertEqual(base64.b64decode(d["b64"]), data)
        self.assertFalse(self.a.file_op_b64("decrypt", e["name"], e["b64"], "bad")["ok"])
    def test_hidden_methods(self):
        self.assertFalse(any(n.startswith("_") for n in dir(self.a) if n in ("scan", "crypt")))
