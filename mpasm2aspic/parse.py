#!/usr/bin/env python3

import re
from . import mpasm_directives

EMPTY_LINE_TOKENS = {
    "field1": None,
    "field2": None,
    "field3": None,
    "comment": None,
    "indent": 0,
}


class Parser(object):
    re_line = re.compile(
        r"^\s*(?P<field1>[\w#:]+)?\s*(?P<field2>[\w\"'.]+(,\s?\w+)?)?\s*(?P<field3>[\w\"']+(,\s?\w+)?)?\s*(?P<comment>;.*)?\s*$"  # noqa: E501
    )
    re_literal = re.compile(r"^(?P<type>[\w\.])(\"|')(?P<number>[\w ]+)(\"|')")

    def __init__(self, INSTRUCTION_SET=[]):
        self.INSTRUCTION_SET = INSTRUCTION_SET

    def tokenize(self, line=""):
        """ Break the source line down into tokens.

        This makes no effort to understand the purpose of the tokens, beyond
        identifying comments.


        Parameters

        ----------
        line: str
            A line of MPASM source

        Returns
        -------
        dict
            a dictionary of tokens. The key names will always be "field1"
            through "field3" and "comments"
        """
        match = self.re_line.search(line)
        if match:
            tokens = match.groupdict()
            tokens["indent"] = 0
            return tokens
        elif line == "":
            return EMPTY_LINE_TOKENS
        else:
            tokens = self.split_match(line)
            if tokens == EMPTY_LINE_TOKENS:
                tokens["comment"] = line + "    ;#PARSE_ERROR"
            return tokens

    def split_match(self, line=""):
        tokens = EMPTY_LINE_TOKENS.copy()

        # Check for comments. set remaining to anything that's not a comment
        comment_split = line.rstrip().split(";", maxsplit=1)
        if len(comment_split) > 1:
            remaining, comment = comment_split
            tokens["comment"] = ";" + comment
        else:
            remaining = comment_split[0]

        # field_candidate is a valid field if it's an instruction or directive,
        # field_candidate could be a label if it's not.
        field_split = remaining.split(maxsplit=1)
        if len(field_split) > 1:
            field_candidate, remaining = field_split
            if self.is_directive(field_candidate) or self.is_instruction(
                field_candidate
            ):
                tokens["field1"] = field_candidate
                tokens["indent"] = 1

            field_split2 = remaining.split(maxsplit=1)
            if len(field_split2) > 1:
                field_candidate_2, remaining_2 = field_split2
                # field_candidate 1 & 2 are valid fields if field_candidate_2 is
                if self.is_instruction(field_candidate_2) or self.is_directive(
                    field_candidate_2
                ):
                    if tokens["field1"] is None:
                        # field_candidate has to be a label
                        tokens["field1"] = field_candidate
                    tokens["field2"] = field_candidate_2
                    tokens["field3"] = remaining_2

            if (tokens["field1"] is not None) and (tokens["field2"] is None):
                tokens["field2"] = remaining

            return tokens

    def fix_literals(self, field=""):
        """Reformat numeric literals.

        MPASM Literals are in the form B"10101010" where XC8 aspic literals are
        in the form 10101010B. This pattern is the same for all number
        representations. The only exception is hex, where the 0xFF
        representation is the same in both.

        It is safe to pass fields that do not contain literals through this
        function. The string will not match the regex and will be returned
        unmolested.

        Parameters
        ----------
        field: str
            Field containing literal to fix.

        Returns
        -------
        str
            fixed literal, or untouched input if no literal was found.
        """
        if field:
            match = self.re_literal.search(field)
            if match:
                # May need to add uppercase the type here?
                matches = match.groupdict()
                if match["type"] == "A":
                    xc8_literal = '"{number}"'.format(**matches)
                else:
                    xc8_literal = "{number}{type}".format(**matches)
                return xc8_literal
            else:
                return field
        else:
            return None

    def is_directive(self, token):
        if token and (token.lower() in mpasm_directives.MPASM_DIRECTIVES):
            return True
        else:
            return False

    def is_instruction(self, token):
        if token and (token.lower() in self.INSTRUCTION_SET):
            return True
        else:
            return False

    def has_label(self, tokens):
        if tokens["field1"]:
            if not (
                self.is_directive(tokens["field1"])
                or self.is_instruction(tokens["field1"])
                or (
                    self.is_directive(tokens["field2"])
                    and not (
                        tokens["field2"].lower
                        in mpasm_directives.MPASM_DIRECTIVES_WLABELS
                    )
                )
            ):
                return True
        return False

    def textify(self, tokens):
        """Convert tokens into ASPIC text"""
        for key, value in tokens.items():
            if value is None:
                tokens[key] = ""
        string = "{field1} {field2} {field3} {comment}".format(**tokens).strip()
        for i in range(tokens.get("indent", 0)):
            string = "\t" + string
        return string

    def parse(self, line):
        tokens = self.tokenize(line)

        # numeric literals can only ever be in field 2 or 3
        if tokens["field3"]:
            tokens["field3"] = self.fix_literals(tokens["field3"])
        if tokens["field2"]:
            tokens["field2"] = self.fix_literals(tokens["field2"])

        if self.has_label(tokens):
            if tokens["field1"][-1] != ":":
                tokens["field1"] += ":"
        else:
            if self.is_instruction(tokens["field1"]):
                tokens["indent"] = 1

        return tokens
