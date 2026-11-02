import re
from model.lexeme import Lexeme
from model.token import Token

# Lexeme patterns for LOLCODE regex matching
LEXEME_PATTERNS = [
    r"HAI\b", r"KTHXBYE\b", r"WAZZUP\b", r"BUHBYE\b",
    r"BTW\b", r"OBTW\b", r"TLDR\b",
    r"I HAS A\b", r"ITZ\b", r"R\b",
    r"SUM OF\b", r"DIFF OF\b", r"PRODUKT OF\b", r"QUOSHUNT OF\b", r"MOD OF\b",
    r"BIGGR OF\b", r"SMALLR OF\b",
    r"BOTH OF\b", r"EITHER OF\b", r"WON OF\b", r"NOT\b", r"ANY OF\b", r"ALL OF\b",
    r"BOTH SAEM\b", r"DIFFRINT\b",
    r"SMOOSH\b", r"MAEK\b", r"AN\b", r"A\b", r"IS NOW A\b",
    r"VISIBLE\b", r"GIMMEH\b",
    r"O RLY\?", r"YA RLY\b", r"MEBBE\b", r"NO WAI\b", r"OIC\b",
    r"WTF\?", r"OMGWTF\b", r"OMG\b",
    r"IM IN YR\b", r"UPPIN\b", r"NERFIN\b", r"YR\b", r"TIL\b", r"WILE\b", r"IM OUTTA YR\b",
    r"HOW IZ I\b", r"IF U SAY SO\b", r"GTFO\b", r"FOUND YR\b", r"I IZ\b", r"MKAY\b",
    r"\+",
    r"[a-zA-Z][a-zA-Z0-9_]*",       # identifiers / WIN / FAIL / type names (spec: must start with a letter)
    r"-?\d+\.\d+",                  # NUMBAR
    r"-?\d+",                       # NUMBR
    r'"[^"\n]*"',                   # YARN (no newline inside)
]
# Compile the regex patterns into a single regex for matching lexemes
LEXEME_REGEX = re.compile("|".join(f"(?:{p})" for p in LEXEME_PATTERNS))

class LexicalAnalyzer:
    """
    Handles the tokenization of the raw input string into a list of tokens.
    """
    def __init__(self):
        pass

    def run(self, raw_content: str) -> list[Token]:
        """
        Run the lexical analyzer pipeline.
        Parse the raw content into lexemes, then get the lexeme types to build the list of tokens.
        """
        lexeme_list = self.lexer(raw_content)           # Tokenize the input string
        return lexeme_list, self.parser(lexeme_list)    # Parse the lexemes into tokens

    def lexer(self, raw_content: str) -> list[str]:
        """
        Parse the raw contents into lexeme list
        """
        # Ensure that newlines are \n and strip leading whitespace (except for newlines)
        raw_content = raw_content.replace("\r\n", "\n").replace("\r", "\n")
        raw_content = self.lexeme_strip(raw_content)

        lexeme_list = []            # List to hold the lexemes
        multiline_flag = False      # Flag to indicate if we are in a multiline 
        while raw_content not in ["", None]:
            if out := LEXEME_REGEX.match(raw_content):
                lexeme = out.group(0)
                lexeme_list.append(lexeme)
                # Remove the matched string from the raw_content
                raw_content = self.lexeme_strip(raw_content[out.end():])
                # Comments are swallowed as raw text, NOT tokenized as code
                if lexeme == "BTW":
                    raw_content = self.consume_line_comment(raw_content, lexeme_list)
                elif lexeme == "OBTW":
                    raw_content = self.consume_block_comment(raw_content, lexeme_list)
            elif out := re.search("^\n", raw_content):
                if not multiline_flag:
                    lexeme_list.append(out.group(0))
                raw_content = self.lexeme_strip(raw_content[out.end():])
            elif out := re.search("^,", raw_content):
                # Soft command break
                raw_content = self.lexeme_strip(raw_content[out.end():])
                lexeme_list.append('\n')    # Add a newline to split the statements
            elif out := re.search("^\\.\\.\\.", raw_content):
                # Continue the line
                raw_content = self.lexeme_strip(raw_content[out.end():])
                multiline_flag = True
                continue            # Skip the reset of multiline_flag
            else:
                out = re.search("^.", raw_content)
                lexeme_list.append(out.group(0))
                # Remove the matched string from the raw_content
                raw_content = self.lexeme_strip(raw_content[out.end():])
            # Or if it already consume, it will turn off the multiline_flag
            multiline_flag = False
        return lexeme_list

    def consume_line_comment(self, raw_content: str, lexeme_list: list[str]) -> str:
        """
        Handles the line comment starting with BTW.
        Makes the succeeding text into a single lexeme until the end of the line.
        """
        line = re.match(r"[^\n]*", raw_content) # Match everything until the end of the line
        text = line.group(0).rstrip()           # Remove trailing whitespace from the comment text
        if text:
            lexeme_list.append(text)
        return raw_content[line.end():]         # Return the remaining content after the comment line

    def consume_block_comment(self, raw_content: str, lexeme_list: list[str]) -> str:
        """
        Handles the block comment starting with OBTW and ending with TLDR.
        Makes each comment line a single lexeme until the TLDR line.
        """
        first_line_flag = True
        while True:
            line = re.match(r"[^\n]*", raw_content)         # Get the current line
            text = line.group(0)                            # Get the text of the current line

            # Check if the current line contains TLDR
            # First line doesn't allow TLDR (end of block comment)
            if not first_line_flag and (out := re.match(r"[ \t]*TLDR\b", text) or re.search(r"\bTLDR[ \t]*$", text)):
                before = text[:out.start()].strip()         # Text before TLDR, if any
                if before:
                    lexeme_list.append(before)
                lexeme_list.append("TLDR")
                return self.lexeme_strip(raw_content[line.end():])

            # Append the current line without whitespace
            if stripped := text.strip():
                lexeme_list.append(stripped)
            raw_content = raw_content[line.end():]          # Consume the WHOLE line
            if not raw_content:                             # End of file reached without TLDR
                raise SyntaxError("Block comment not closed with TLDR")
            lexeme_list.append("\n")                        # The newline that ended this line
            raw_content = raw_content[1:]                   # Consume that newline
            first_line_flag = False

    def parser(self, lexeme_list: list[str]) -> list[Token]:
        """
        Parse the lexeme list into tokens (lexeme, type) tuple
        """
        # Tokenize the input string
        comment_flag = False            # inside a BTW line comment
        block_comment_flag = False      # inside an OBTW ... TLDR block
        token_list = []
        for raw_str in lexeme_list:
            if re.search("^\n", raw_str):
                comment_flag = False
                token_list.append(Token(raw_str, Lexeme.NEWLINE))
            elif comment_flag or (block_comment_flag and raw_str != "TLDR"):
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
                elif re.search("^BTW$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.BTW))
                    comment_flag = True
                elif re.search("^OBTW$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.OBTW))
                    block_comment_flag = True
                elif re.search("^TLDR$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.TLDR))
                    block_comment_flag = False
                elif re.search("^I HAS A$", raw_str):
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
                elif re.search("^OMGWTF$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.OMGWTF))
                elif re.search("^OMG$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.OMG))
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
                elif re.search("^(NOOB|NUMBR|NUMBAR|YARN|TROOF)$", raw_str):
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
                # Variable identifiers (must start with a letter)
                elif re.search("^[a-zA-Z][a-zA-Z0-9_]*$", raw_str):
                    token_list.append(Token(raw_str, Lexeme.IDENTIFIER))
                else:
                    # A lexical error must stop the run, not be silently dropped
                    raise SyntaxError(f"Lexical error: unrecognized lexeme '{raw_str}'")
        return token_list

    def lexeme_strip(self, raw_content) -> str:
        """
        Remove whitespace in the left except for newlines
        """
        return re.sub(r'^[ \t]+', '', raw_content)
