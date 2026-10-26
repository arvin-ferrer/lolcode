BTW ===================================================================
BTW  FULL SPEC TEST CASE  -  every line with "expect:" shows the output
BTW ===================================================================

BTW ---- functions may be defined BEFORE HAI ----
HOW IZ I add YR a AN YR b
  FOUND YR SUM OF a AN b
IF U SAY SO

HOW IZ I add3 YR a AN YR b AN YR c
  FOUND YR SUM OF a AN SUM OF b AN c
IF U SAY SO

HOW IZ I greet
  VISIBLE "hello from greet"
IF U SAY SO

OBTW this is a multi-line comment before HAI
VISIBLE "THIS MUST NEVER PRINT"
TLDR

HAI BTW a comment on the HAI line
WAZZUP
  I HAS A uninit
  I HAS A lit_numbr ITZ 12
  I HAS A lit_numbar ITZ 3.5
  I HAS A lit_yarn ITZ "some   spaced   yarn"
  I HAS A lit_win ITZ WIN
  I HAS A lit_fail ITZ FAIL
  I HAS A neg ITZ -7
  I HAS A copy ITZ lit_numbr
  I HAS A expr ITZ SUM OF 5 AN 4 BTW comment next to a statement
  I HAS A n ITZ 5
  I HAS A i ITZ 0
  I HAS A res ITZ 0
  I HAS A conv ITZ 17
  I HAS A dyn ITZ 1
  I HAS A input_var
BUHBYE

OBTW comment block with a statement-looking line
I HAS A bad ITZ 1
TLDR

VISIBLE "=== 1. OUTPUT (VISIBLE) ==="
VISIBLE "plain literal"                  BTW expect: plain literal
VISIBLE lit_numbr                        BTW expect: 12
VISIBLE SUM OF 1 AN 2                    BTW expect: 3
VISIBLE "a" + 1 + 2.5 + WIN + " end"     BTW expect: a12.5WIN end
VISIBLE lit_yarn                         BTW expect: some   spaced   yarn

VISIBLE "=== 2. VARIABLES ==="
VISIBLE copy                             BTW expect: 12
VISIBLE expr                             BTW expect: 9
VISIBLE neg                              BTW expect: -7
VISIBLE lit_numbar                       BTW expect: 3.5
VISIBLE lit_win + " " + lit_fail         BTW expect: WIN FAIL
VISIBLE MAEK uninit YARN                 BTW expect: (empty line, NOOB -> "")
uninit
O RLY?
YA RLY
  VISIBLE "WRONG: NOOB is WIN"
NO WAI
  VISIBLE "NOOB casts to FAIL"           BTW expect: NOOB casts to FAIL
OIC

VISIBLE "=== 3. IMPLICIT IT ==="
SUM OF 2 AN 3
VISIBLE IT                               BTW expect: 5
lit_yarn
VISIBLE IT                               BTW expect: some   spaced   yarn

VISIBLE "=== 4. ARITHMETIC ==="
VISIBLE SUM OF 2 AN 4                    BTW expect: 6
VISIBLE DIFF OF 4 AN 3.14                BTW expect: 0.86  (truncated, not rounded)
VISIBLE PRODUKT OF "2" AN "7"            BTW expect: 14
VISIBLE QUOSHUNT OF 5 AN "12"            BTW expect: 0
VISIBLE QUOSHUNT OF 7 AN 2               BTW expect: 3     (NUMBR / NUMBR)
VISIBLE QUOSHUNT OF 7.0 AN 2             BTW expect: 3.5
VISIBLE MOD OF 10 AN 3                   BTW expect: 1
VISIBLE MOD OF 3 AN "3.14"               BTW expect: 3.0
VISIBLE BIGGR OF 3 AN 9                  BTW expect: 9
VISIBLE SMALLR OF 3 AN 9                 BTW expect: 3
VISIBLE PRODUKT OF 2 AN 1.5              BTW expect: 3.0
VISIBLE SUM OF neg AN 10                 BTW expect: 3
VISIBLE SUM OF WIN AN 1                  BTW expect: 2
VISIBLE SUM OF QUOSHUNT OF PRODUKT OF 3 AN 4 AN 2 AN 1   BTW expect: 7
VISIBLE SUM OF SUM OF SUM OF 3 AN 4 AN 2 AN 1            BTW expect: 10

VISIBLE "=== 5. CONCATENATION (SMOOSH) ==="
VISIBLE SMOOSH "a" AN 124 AN 2.8 AN WIN AN "z"   BTW expect: a1242.8WINz

VISIBLE "=== 6. BOOLEAN ==="
VISIBLE BOTH OF WIN AN FAIL              BTW expect: FAIL
VISIBLE EITHER OF WIN AN FAIL            BTW expect: WIN
VISIBLE WON OF WIN AN WIN                BTW expect: FAIL
VISIBLE NOT WIN                          BTW expect: FAIL
VISIBLE NOT 0                            BTW expect: WIN
VISIBLE BOTH OF "" AN 1                  BTW expect: FAIL  (implicit casts)
VISIBLE ALL OF NOT FAIL AN BOTH OF WIN AN WIN AN EITHER OF FAIL AN WIN MKAY   BTW expect: WIN
VISIBLE ANY OF FAIL AN FAIL AN WIN MKAY  BTW expect: WIN
VISIBLE ANY OF uninit AN "x" MKAY        BTW expect: WIN
VISIBLE ALL OF WIN AN WIN AN FAIL MKAY   BTW expect: FAIL

VISIBLE "=== 7. COMPARISON ==="
VISIBLE BOTH SAEM 5 AN 5                 BTW expect: WIN
VISIBLE DIFFRINT 5 AN 6                  BTW expect: WIN
VISIBLE BOTH SAEM 5 AN "5"               BTW expect: FAIL  (no implicit casting)
VISIBLE BOTH SAEM "a" AN "a"             BTW expect: WIN
VISIBLE BOTH SAEM n AN BIGGR OF n AN lit_numbr     BTW expect: FAIL  (5 >= 12)
VISIBLE BOTH SAEM n AN SMALLR OF n AN lit_numbr    BTW expect: WIN   (5 <= 12)
VISIBLE DIFFRINT n AN SMALLR OF n AN lit_numbr     BTW expect: FAIL  (5 > 12)
VISIBLE DIFFRINT n AN BIGGR OF n AN lit_numbr      BTW expect: WIN   (5 < 12)

VISIBLE "=== 8. TYPECASTING ==="
VISIBLE MAEK lit_numbr A NUMBAR          BTW expect: 12.0
VISIBLE MAEK lit_numbr YARN              BTW expect: 12
VISIBLE lit_numbr                        BTW expect: 12   (variable unchanged)
VISIBLE MAEK 3.99 NUMBR                  BTW expect: 3
VISIBLE MAEK 3.14159 YARN                BTW expect: 3.14
VISIBLE MAEK "42" NUMBR                  BTW expect: 42
VISIBLE MAEK "3.5" NUMBAR                BTW expect: 3.5
VISIBLE MAEK "" TROOF                    BTW expect: FAIL
VISIBLE MAEK 0 TROOF                     BTW expect: FAIL
VISIBLE MAEK "abc" TROOF                 BTW expect: WIN
VISIBLE MAEK WIN NUMBR                   BTW expect: 1
VISIBLE MAEK FAIL NUMBAR                 BTW expect: 0.0
VISIBLE MAEK uninit NUMBR                BTW expect: 0
conv IS NOW A NUMBAR
VISIBLE conv                             BTW expect: 17.0
conv R MAEK conv YARN
VISIBLE conv                             BTW expect: 17.0
VISIBLE BOTH SAEM conv AN "17.0"         BTW expect: WIN  (conv is now a YARN)

VISIBLE "=== 9. ASSIGNMENT (dynamic typing) ==="
dyn R 42
VISIBLE dyn                              BTW expect: 42
dyn R "now a yarn"
VISIBLE dyn                              BTW expect: now a yarn
dyn R lit_numbr
VISIBLE dyn                              BTW expect: 12
dyn R SUM OF dyn AN 1
VISIBLE dyn                              BTW expect: 13
uninit R 7
VISIBLE uninit                           BTW expect: 7  (NOOB variable becomes NUMBR)

VISIBLE "=== 10. IF-THEN ==="
BOTH SAEM n AN 5
O RLY?
YA RLY
  VISIBLE "if branch"                    BTW expect: if branch
NO WAI
  VISIBLE "WRONG else"
OIC
BOTH SAEM n AN 6
O RLY?
YA RLY
  VISIBLE "WRONG if"
NO WAI
  VISIBLE "else branch"                  BTW expect: else branch
OIC

VISIBLE "=== 11. SWITCH-CASE ==="
SUM OF 1 AN 1
WTF?
OMG 1
  VISIBLE "one"
OMG 2
  VISIBLE "two"                          BTW expect: two
OMG 3
  VISIBLE "three (fall-through)"         BTW expect: three (fall-through)
  GTFO
OMG 4
  VISIBLE "WRONG four"
OMGWTF
  VISIBLE "WRONG default"
OIC
SUM OF 40 AN 2
WTF?
OMG 1
  VISIBLE "WRONG one"
OMGWTF
  VISIBLE "default case"                 BTW expect: default case
OIC
"b"
WTF?
OMG "a"
  VISIBLE "WRONG a"
OMG "b"
  VISIBLE "yarn case b"                  BTW expect: yarn case b
  GTFO
OMGWTF
  VISIBLE "WRONG default"
OIC
WIN
WTF?
OMG WIN
  VISIBLE "troof case WIN"               BTW expect: troof case WIN
  GTFO
OMG FAIL
  VISIBLE "WRONG fail"
OIC
1.5
WTF?
OMG 1.5
  VISIBLE "numbar case 1.5"              BTW expect: numbar case 1.5
  GTFO
OIC

VISIBLE "=== 12. LOOPS ==="
BTW UPPIN with TIL: prints 0 1 2
IM IN YR up1 UPPIN YR i TIL BOTH SAEM i AN 3
  VISIBLE i                              BTW expect: 0 1 2
IM OUTTA YR up1
VISIBLE i                                BTW expect: 3
i R 0
BTW UPPIN with WILE: prints 0 1 2
IM IN YR up2 UPPIN YR i WILE DIFFRINT i AN 3
  VISIBLE i                              BTW expect: 0 1 2
IM OUTTA YR up2
BTW NERFIN with TIL: prints 3 2 1
i R 3
IM IN YR down NERFIN YR i TIL BOTH SAEM i AN 0
  VISIBLE i                              BTW expect: 3 2 1
IM OUTTA YR down
BTW reuse of the same label, accumulate a sum 0+1+2+3+4
i R 0
res R 0
IM IN YR up1 UPPIN YR i TIL BOTH SAEM i AN 5
  res R SUM OF res AN i
IM OUTTA YR up1
VISIBLE res                              BTW expect: 10
BTW loop with no condition, ended by GTFO: prints 0 1 2
i R 0
IM IN YR forever UPPIN YR i
  VISIBLE i                              BTW expect: 0 1 2
  BOTH SAEM i AN 2
  O RLY?
  YA RLY
    GTFO
  OIC
IM OUTTA YR forever
VISIBLE "after loop"                     BTW expect: after loop

VISIBLE "=== 13. FUNCTIONS ==="
I IZ greet MKAY                          BTW expect: hello from greet
VISIBLE I IZ add YR 3 AN YR 4 MKAY       BTW expect: 7
VISIBLE I IZ add3 YR 1 AN YR 2 AN YR 3 MKAY    BTW expect: 6
VISIBLE I IZ add YR 1 AN YR I IZ add YR 2 AN YR 3 MKAY MKAY   BTW expect: 6
VISIBLE I IZ add YR SUM OF 1 AN 1 AN YR PRODUKT OF 2 AN 3 MKAY   BTW expect: 8
I IZ add YR 10 AN YR 20 MKAY
VISIBLE IT                               BTW expect: 30  (return value goes to IT)
res R I IZ add YR 100 AN YR 1 MKAY
VISIBLE res                              BTW expect: 101
VISIBLE I IZ fact YR 5 MKAY              BTW expect: 120  (recursion)
VISIBLE I IZ check YR 5 MKAY             BTW expect: nonzero
I IZ check YR 0 MKAY
O RLY?
YA RLY
  VISIBLE "WRONG: GTFO should return NOOB"
NO WAI
  VISIBLE "GTFO returned NOOB"           BTW expect: GTFO returned NOOB
OIC
I IZ greet MKAY                          BTW expect: hello from greet (again)
O RLY?
YA RLY
  VISIBLE "WRONG: no return should be NOOB"
NO WAI
  VISIBLE "no FOUND YR gives NOOB"       BTW expect: no FOUND YR gives NOOB
OIC
BTW pass-by-value: the caller's variable must not change
I IZ modify YR n MKAY
VISIBLE n                                BTW expect: 5

VISIBLE "=== 14. INPUT (GIMMEH) ==="
GIMMEH input_var
VISIBLE "you typed: " + input_var        BTW expect: you typed: <whatever you entered>

VISIBLE "=== DONE ==="
KTHXBYE

BTW ---- functions may also be defined AFTER KTHXBYE ----
HOW IZ I fact YR k
  BOTH SAEM k AN 1
  O RLY?
  YA RLY
    FOUND YR 1
  OIC
  FOUND YR PRODUKT OF k AN I IZ fact YR DIFF OF k AN 1 MKAY
IF U SAY SO

HOW IZ I check YR x
  BOTH SAEM x AN 0
  O RLY?
  YA RLY
    GTFO
  OIC
  FOUND YR "nonzero"
IF U SAY SO

HOW IZ I modify YR n
  n R SUM OF n AN 100
  FOUND YR n
IF U SAY SO

BTW this is accepted!