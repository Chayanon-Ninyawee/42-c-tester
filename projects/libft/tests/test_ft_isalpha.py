from framework import TestSuite

suite = TestSuite("ft_isalpha")


@suite.case("'A' is alphabetic")
def test_uppercase_start(c):
    c.ft_isalpha("'A'").equals(1).assert_now()


@suite.case("'Z' is alphabetic")
def test_uppercase_end(c):
    c.ft_isalpha("'Z'").equals(1).assert_now()


@suite.case("'a' is alphabetic")
def test_lowercase_start(c):
    c.ft_isalpha("'a'").equals(1).assert_now()


@suite.case("'z' is alphabetic")
def test_lowercase_end(c):
    c.ft_isalpha("'z'").equals(1).assert_now()


@suite.case("'[' is not alphabetic")
def test_after_uppercase(c):
    c.ft_isalpha("'['").equals(0).assert_now()


@suite.case("'`' is not alphabetic")
def test_before_lowercase(c):
    c.ft_isalpha("'`'").equals(0).assert_now()


@suite.case("'{' is not alphabetic")
def test_after_lowercase(c):
    c.ft_isalpha("'{'").equals(0).assert_now()


@suite.case("'0' is not alphabetic")
def test_digit(c):
    c.ft_isalpha("'0'").equals(0).assert_now()


@suite.case("'9' is not alphabetic")
def test_digit_end(c):
    c.ft_isalpha("'9'").equals(0).assert_now()


@suite.case("' ' is not alphabetic")
def test_space(c):
    c.ft_isalpha("' '").equals(0).assert_now()


@suite.case("'\\t' is not alphabetic")
def test_tab(c):
    c.ft_isalpha("'\\t'").equals(0).assert_now()


@suite.case("'\\n' is not alphabetic")
def test_newline(c):
    c.ft_isalpha("'\\n'").equals(0).assert_now()


@suite.case("'!' is not alphabetic")
def test_punctuation(c):
    c.ft_isalpha("'!'").equals(0).assert_now()


@suite.case("'@' is not alphabetic")
def test_symbol(c):
    c.ft_isalpha("'@'").equals(0).assert_now()


@suite.case("-1 is not alphabetic")
def test_negative(c):
    c.ft_isalpha("-1").equals(0).assert_now()


@suite.case("127 is not alphabetic")
def test_del(c):
    c.ft_isalpha("127").equals(0).assert_now()
