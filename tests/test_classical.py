import unittest, crypto as c

class T(unittest.TestCase):
    def test_caesar(self):
        self.assertEqual(c.caesar("Hello, World!", 3), "Khoor, Zruog!")
        self.assertEqual(c.caesar(c.caesar("Hello", 7), 7, True), "Hello")
    def test_vigenere(self):
        self.assertEqual(c.vigenere("ATTACKATDAWN", "LEMON"), "LXFOPVEFRNHR")
        self.assertEqual(c.vigenere("LXFOPVEFRNHR", "LEMON", True), "ATTACKATDAWN")
        with self.assertRaises(ValueError): c.vigenere("x", "123")
