IGNORE_CHARS = [',']

import re
from model.lexeme import Lexeme

def lexeme_strip(raw_content):
    # Remove whitespace in the left except for newlines
    stripped_content = re.sub(r'^[ \t]+', '', raw_content)
    return stripped_content

def run(raw_content):
    # Tokenize the input string
    lexeme_list = []
    multiline_flag = False
    while raw_content not in ["", None]:
        if out := re.search("^HAI", raw_content)\
            or re.search("^KTHXBYE", raw_content)\
            or re.search("^WAZZUP", raw_content)\
            or re.search("^BUHBYE", raw_content)\
            or re.search("^BTW", raw_content)\
            or re.search("^OBTW", raw_content)\
            or re.search("^TLDR", raw_content)\
            or re.search("^I HAS A", raw_content)\
            or re.search("^ITZ", raw_content)\
            or re.search("^R", raw_content)\
            or re.search("^SUM OF", raw_content)\
            or re.search("^DIFF OF", raw_content)\
            or re.search("^PRODUKT OF", raw_content)\
            or re.search("^QUOSHUNT OF", raw_content)\
            or re.search("^MOD OF", raw_content)\
            or re.search("^BIGGR OF", raw_content)\
            or re.search("^SMALLR OF", raw_content)\
            or re.search("^BOTH OF", raw_content)\
            or re.search("^EITHER OF", raw_content)\
            or re.search("^WON OF", raw_content)\
            or re.search("^NOT", raw_content)\
            or re.search("^ANY OF", raw_content)\
            or re.search("^ALL OF", raw_content)\
            or re.search("^BOTH SAEM", raw_content)\
            or re.search("^DIFFRINT", raw_content)\
            or re.search("^SMOOSH", raw_content)\
            or re.search("^MAEK", raw_content)\
            or re.search("^AN", raw_content)\
            or re.search("^A", raw_content)\
            or re.search("^IS NOW A", raw_content)\
            or re.search("^VISIBLE", raw_content)\
            or re.search("^GIMMEH", raw_content)\
            or re.search("^O RLY\\?", raw_content)\
            or re.search("^YA RLY", raw_content)\
            or re.search("^MEBBE", raw_content)\
            or re.search("^NO WAI", raw_content)\
            or re.search("^OIC", raw_content)\
            or re.search("^WTF\\?", raw_content)\
            or re.search("^OMGWTF", raw_content)\
            or re.search("^IM IN YR", raw_content)\
            or re.search("^UPPIN", raw_content)\
            or re.search("^NERFIN", raw_content)\
            or re.search("^YR", raw_content)\
            or re.search("^TIL", raw_content)\
            or re.search("^WILE", raw_content)\
            or re.search("^IM OUTTA YR", raw_content)\
            or re.search("^HOW IZ I", raw_content)\
            or re.search("^IF U SAY SO", raw_content)\
            or re.search("^GTFO", raw_content)\
            or re.search("^FOUND YR", raw_content)\
            or re.search("^I IZ", raw_content)\
            or re.search("^MKAY", raw_content)\
            or re.search("^ON", raw_content)\
            or re.search(r"^\+", raw_content)\
            or re.search("^[a-zA-Z_][a-zA-Z0-9_]*", raw_content)\
            or re.search("^-?\\d+\\.\\d+", raw_content)\
            or re.search("^-?\\d+", raw_content)\
            or re.search("^\"[^\"]*\"", raw_content)\
            or re.search("^(WIN|FAIL)", raw_content)\
            or re.search("^(NUMBR|NUMBAR|YARN|TROOF)", raw_content):
            lexeme_list.append(out.group(0))
            # Remove the matched string from the raw_content
            raw_content = lexeme_strip(raw_content[out.end():])
        elif out := re.search("^\n", raw_content):
            if not multiline_flag:
                lexeme_list.append(out.group(0))
            raw_content = lexeme_strip(raw_content[out.end():])
        elif out := re.search("^,", raw_content):
            # Split into newline
            raw_content = lexeme_strip(raw_content[out.end():])
            lexeme_list.append('\n')
        elif out := re.search("^...", raw_content):
            # Continue the line
            raw_content = lexeme_strip(raw_content[out.end():])
            multiline_flag = True
            continue            # Skip the reset of multiline_flag
        else:
            out = re.search("^.", raw_content)
            lexeme_list.append(out.group(0))
            # Remove the matched string from the raw_content
            raw_content = lexeme_strip(raw_content[out.end():])        # If the newline didn't consume after the ..., 
        # Or if it already consume, it will turn off the multiline_flag
        multiline_flag = False
    return lexeme_list