from mpasm2aspic import __version__
import mpasm2aspic
import mpasm2aspic.pic16f877
import unittest


class TestInstruction(unittest.TestCase):
    def setUp(self):
        self.parser = mpasm2aspic.Parser(mpasm2aspic.pic16f877.INSTRUCTION_SET)

    def test_movwf(self):
        self.assertTrue(self.parser.is_instruction("movwf"))

    def test_directive(self):
        self.assertFalse(self.parser.is_instruction("#define"))


class TestParse(unittest.TestCase):
    def setUp(self):
        self.parser = mpasm2aspic.Parser(mpasm2aspic.pic16f877.INSTRUCTION_SET)

    def test_simpleLabel(self):
        self.assertEqual(
            self.parser.parse("LABEL"),
            {
                "field1": "LABEL:",
                "field2": None,
                "field3": None,
                "comment": None,
                "indent": 0,
            },
        )

    def test_commentedLabel(self):
        self.assertEqual(
            self.parser.parse("LABEL\t\t    ; a comment"),
            {
                "field1": "LABEL:",
                "field2": None,
                "field3": None,
                "comment": "; a comment",
                "indent": 0,
            },
        )

    def test_fourfieldLabel(self):
        self.assertEqual(
            self.parser.parse(
                'LABEL MOVLW B"10101010"\t;comment don\'t\t; #v4.1.1 style'
            ),
            {
                "field1": "LABEL:",
                "field2": "MOVLW",
                "field3": "10101010B",
                "comment": ";comment don't\t; #v4.1.1 style",
                "indent": 0,
            },
        )

    def test_colonLabel(self):
        self.assertEqual(
            self.parser.parse("BEGIN:"),
            {
                "field1": "BEGIN:",
                "field2": None,
                "field3": None,
                "comment": None,
                "indent": 0,
            },
        )

    def test_twofieldInstruction(self):
        self.assertEqual(
            self.parser.parse("\tmovwf TRISB"),
            {
                "field1": "movwf",
                "field2": "TRISB",
                "field3": None,
                "comment": None,
                "indent": 1,
            },
        )

    def test_define(self):
        self.assertEqual(
            self.parser.parse("#include pic16f877a.inc"),
            {
                "field1": "#include",
                "field2": "pic16f877a.inc",
                "field3": None,
                "comment": None,
                "indent": 0,
            },
        )


def test_version():
    assert __version__ == "0.1.0"


if __name__ == "__main__":
    unittest.main()
