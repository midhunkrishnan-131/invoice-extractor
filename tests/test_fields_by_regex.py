"""Regex field extraction, including totals prefixed by OCR noise."""
import unittest

from invoice_extractor import fields_by_regex


class TotalRegexTest(unittest.TestCase):
    def test_clean_total_line(self):
        text = "\n".join([
            "Bluebird Print & Design INVOICE",
            "Invoice No: INV-9797",
            "Date: Apr 28, 2025",
            "Network switch 8-port 7 185.65 1,299.55",
            "Subtotal 7,070.00",
            "Tax (5%) 353.50",
            "Total 7,423.50",
        ])
        fields = fields_by_regex(text)
        self.assertEqual(fields["invoice_no"], "INV-9797")
        self.assertEqual(fields["subtotal"], 7070.00)
        self.assertEqual(fields["tax"], 353.50)
        self.assertEqual(fields["total"], 7423.50)
        self.assertEqual(len(fields["items"]), 1)

    def test_total_with_currency_and_colon(self):
        self.assertEqual(fields_by_regex("Total: $1,234.56").get("total"), 1234.56)

    def test_subtotal_is_not_the_total(self):
        fields = fields_by_regex("Subtotal 1,692.37\nTax (10%) 169.24\n")
        self.assertEqual(fields["subtotal"], 1692.37)
        self.assertEqual(fields["tax"], 169.24)
        self.assertIsNone(fields["total"])

    def test_ocr_punctuation_before_total(self):
        # Lines from samples 04 and 05 preprocessed OCR. The amount is present,
        # but a noise glyph is prefixed to the label.
        phone = "\n".join([
            ". Subtotal 2,065.14 |",
            "Tax (8%) 165.21",
            "! Total 2,230.35",
        ])
        phone_b = "\n".join([
            "Subtotal 4,828.37 !",
            ": Tax (5%) 241.42",
            ", Total 5,069.79",
        ])
        self.assertEqual(fields_by_regex(phone)["total"], 2230.35)
        self.assertEqual(fields_by_regex(phone)["subtotal"], 2065.14)
        self.assertEqual(fields_by_regex(phone_b)["total"], 5069.79)
        self.assertEqual(fields_by_regex(phone_b)["tax"], 241.42)

    def test_total_mentioned_in_prose_does_not_win(self):
        text = "pay the Total 100.00 now\nTotal 55.00\n"
        self.assertEqual(fields_by_regex(text)["total"], 55.00)

    def test_letters_before_total_are_not_skipped(self):
        # "nay Total" is a different failure (a word fragment, not a glyph).
        self.assertIsNone(fields_by_regex("nay Total 2,230.35").get("total"))


if __name__ == "__main__":
    unittest.main()
