IGNORE_CHARS = [',']

import re
from model.lexeme import Lexeme
from model.token import Token

class LexicalAnalyzer:
    def __init__(self):
        pass

    def run(self, raw_content: str) -> list[Token]:
        lexeme_list = self.lexer(raw_content)       # Tokenize the input string
        return self.parser(lexeme_list)      # Parse the lexemes into tokens

    def lexer(self, raw_content: str) -> list[str]:
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
                or re.search("^OMG", raw_content)\
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
                raw_content = self.lexeme_strip(raw_content[out.end():])
            elif out := re.search("^\n", raw_content):
                if not multiline_flag:
                    lexeme_list.append(out.group(0))
                raw_content = self.lexeme_strip(raw_content[out.end():])
            elif out := re.search("^,", raw_content):
                # Split into newline
                raw_content = self.lexeme_strip(raw_content[out.end():])
                lexeme_list.append('\n')
            elif out := re.search("^...", raw_content):
                # Continue the line
                raw_content = self.lexeme_strip(raw_content[out.end():])
                multiline_flag = True
                continue            # Skip the reset of multiline_flag
            else:
                out = re.search("^.", raw_content)
                lexeme_list.append(out.group(0))
                # Remove the matched string from the raw_content
                raw_content = self.lexeme_strip(raw_content[out.end():])        # If the newline didn't consume after the ..., 
            # Or if it already consume, it will turn off the multiline_flag
            multiline_flag = False
        return lexeme_list

    def parser(self, lexeme_list: list[str]) -> list[Token]:
        # Tokenize the input string
        comment_flag = False
        token_list = []
        for raw_str in lexeme_list:
            if re.search("^\n", raw_str):
                comment_flag = False
                token_list.append(Token(raw_str, Lexeme.NEWLINE))
            elif comment_flag:
                token_list.append(Token(raw_str, Lexeme.COMMENT_IDENTIFIER))
            else:
                if re.search("^HAI$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.HAI))
                elif re.search("^KTHXBYE$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.KTHXBYE))
                elif re.search("^WAZZUP$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.WAZZUP))
                elif re.search("^BUHBYE$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.BUHBYE))
                elif re.search("^BTW", raw_str):
                    token_list.append(Token(raw_str, Lexeme.BTW))
                    comment_flag = True
                elif re.search("^OBTW$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.OBTW))
                elif re.search("^TLDR$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.TLDR))
                elif re.search("^I HAS A", raw_str):
                    token_list.append(Token(raw_str, Lexeme.I_HAS_A))
                elif re.search("^ITZ$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.ITZ))
                elif re.search("^R$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.R))
                elif re.search("^SUM OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.SUM_OF))
                elif re.search("^DIFF OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.DIFF_OF))
                elif re.search("^PRODUKT OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.PRODUKT_OF))
                elif re.search("^QUOSHUNT OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.QUOSHUNT_OF))
                elif re.search("^MOD OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.MOD_OF))
                elif re.search("^BIGGR OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.BIGGR_OF))
                elif re.search("^SMALLR OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.SMALLR_OF))
                elif re.search("^BOTH OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.BOTH_OF))
                elif re.search("^EITHER OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.EITHER_OF))
                elif re.search("^WON OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.WON_OF))
                elif re.search("^NOT$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.NOT))
                elif re.search("^ANY OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.ANY_OF))
                elif re.search("^ALL OF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.ALL_OF))
                elif re.search("^BOTH SAEM$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.BOTH_SAEM))
                elif re.search("^DIFFRINT$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.DIFFRINT))
                elif re.search("^SMOOSH$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.SMOOSH))
                elif re.search("^MAEK$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.MAEK))
                elif re.search("^AN$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.AN))
                elif re.search("^A$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.A))
                elif re.search("^IS NOW A$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.IS_NOW_A))
                elif re.search("^VISIBLE$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.VISIBLE))
                elif re.search("^GIMMEH$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.GIMMEH))
                elif re.search("^O RLY\\?$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.O_RLY))
                elif re.search("^YA RLY$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.YA_RLY))
                elif re.search("^MEBBE$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.MEBBE))
                elif re.search("^NO WAI$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.NO_WAI))
                elif re.search("^OIC$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.OIC))
                elif re.search("^WTF\\?$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.WTF))
                elif re.search("^OMG$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.OMG))
                elif re.search("^OMGWTF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.OMGWTF))
                elif re.search("^IM IN YR$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.IM_IN_YR))
                elif re.search("^UPPIN$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.UPPIN))
                elif re.search("^NERFIN$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.NERFIN))
                elif re.search("^YR$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.YR))
                elif re.search("^TIL$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.TIL))
                elif re.search("^WILE$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.WILE))
                elif re.search("^IM OUTTA YR$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.IM_OUTTA_YR))
                elif re.search("^HOW IZ I$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.HOW_IZ_I))
                elif re.search("^IF U SAY SO$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.IF_U_SAY_SO))
                elif re.search("^GTFO$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.GTFO))
                elif re.search("^FOUND YR$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.FOUND_YR))
                elif re.search("^I IZ$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.I_IZ))
                elif re.search("^MKAY$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.MKAY))
                elif re.search(r"^\+$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.PLUS))
                # Identifiers
                # TROOF literals
                elif re.search("^(WIN|FAIL)$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.TROOF_LITERAL))
                # TYPE literals
                elif re.search("^(NUMBR|NUMBAR|YARN|TROOF)$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.TYPE_LITERAL))
                # NUMBR literals
                elif re.search("^-?\\d+$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.NUMBR_LITERAL))
                # NUMBAR literals
                elif re.search("^-?\\d+\\.\\d+$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.NUMBAR_LITERAL))
                # YARN literals
                elif re.search("^\"[^\"]*\"$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.YARN_LITERAL))
                # Variable identifiers
                elif re.search("^[a-zA-Z_][a-zA-Z0-9_]*$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.IDENTIFIER))
                else:
                    print(f"Unrecognized lexeme >>{raw_str}")
        return token_list
            
    def lexeme_strip(self, raw_content) -> str:
        # Remove whitespace in the left except for newlines
        stripped_content = re.sub(r'^[ \t]+', '', raw_content)
        return stripped_content