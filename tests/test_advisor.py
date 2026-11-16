import unittest, ai

class T(unittest.TestCase):
    def test_advisor(self):
        self.assertEqual(ai.recommend("my card is 4111 1111 1111 1111")["data_type"], "financial")
        self.assertIn("AES", ai.recommend("password: abc12345")["algorithm"])
        self.assertEqual(ai.recommend("hi how are you")["data_type"], "short_secret")

    def test_new_sentences_not_in_training(self):
        cases = [("خلّي الباسورد بتاع الواي فاي 12345", "credentials"), ("ابعتلي المبلغ على الحساب البنكي", "financial"),
                 ("بيانات المريض والتشخيص", "personal"), ("تمام شكرا", "short_secret"),
                 ("ملخص المحاضرة عن قواعد البيانات وأنواعها", "public")]
        for text, label in cases:
            self.assertEqual(ai.recommend(text)["data_type"], label, text)
