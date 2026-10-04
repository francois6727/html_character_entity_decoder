import unittest

from html_character_entity_decoder import decode_html_entities


class TestNamedEntities(unittest.TestCase):
    def test_amp(self):
        self.assertEqual(decode_html_entities("a&amp;b"), "a&b")

    def test_lt_gt_quot(self):
        self.assertEqual(
            decode_html_entities("&lt;tag&gt;&quot;"), '<tag>"'
        )

    def test_named_without_semicolon_is_preserved(self):
        self.assertEqual(decode_html_entities("tom &amp jerry"), "tom &amp jerry")

    def test_unknown_named_entity_preserved(self):
        self.assertEqual(decode_html_entities("foo &nosuchentity; bar"), "foo &nosuchentity; bar")

    def test_multiple_named_in_one_string(self):
        self.assertEqual(
            decode_html_entities("&amp;&lt;&gt;"), "&<>"
        )


class TestNumericDecimal(unittest.TestCase):
    def test_basic_decimal(self):
        self.assertEqual(decode_html_entities("&#65;"), "A")

    def test_decimal_in_context(self):
        self.assertEqual(decode_html_entities("&#65;&#66;&#67;"), "ABC")

    def test_large_valid_codepoint(self):
        # U+1F600 GRINNING FACE
        self.assertEqual(decode_html_entities("&#128512;"), "😀")


class TestNumericHex(unittest.TestCase):
    def test_lowercase_hex(self):
        self.assertEqual(decode_html_entities("&#x41;"), "A")

    def test_uppercase_x(self):
        self.assertEqual(decode_html_entities("&#X41;"), "A")

    def test_hex_in_context(self):
        self.assertEqual(decode_html_entities("&#x41;&#x42;&#x43;"), "ABC")


class TestMalformedAndEdgeCases(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(decode_html_entities(""), "")

    def test_no_entities(self):
        self.assertEqual(decode_html_entities("just plain text"), "just plain text")

    def test_surrogate_codepoint_preserved(self):
        # U+D800 is a surrogate; we leave the reference intact.
        self.assertEqual(decode_html_entities("&#xD800;"), "&#xD800;")

    def test_codepoint_too_large_preserved(self):
        # U+110000 is one past the Unicode maximum.
        self.assertEqual(decode_html_entities("&#x110000;"), "&#x110000;")

    def test_ampersand_without_entity(self):
        self.assertEqual(decode_html_entities("Tom & Jerry"), "Tom & Jerry")

    def test_mixed_named_and_numeric(self):
        self.assertEqual(
            decode_html_entities("&amp;&#65;&#x42;&lt;"), "&AB<"
        )

    def test_type_error_on_non_string(self):
        with self.assertRaises(TypeError):
            decode_html_entities(123)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
