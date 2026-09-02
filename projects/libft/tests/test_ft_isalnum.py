from framework import TestSuite

suite = TestSuite("ft_isalnum")


@suite.case("'A' is alphanumeric")
def test_uppercase_start(c):
    c.ft_isalnum("'A'").equals(1).assert_now()


@suite.case("'Z' is alphanumeric")
def test_uppercase_end(c):
    c.ft_isalnum("'Z'").equals(1).assert_now()


@suite.case("'a' is alphanumeric")
def test_lowercase_start(c):
    c.ft_isalnum("'a'").equals(1).assert_now()


@suite.case("'z' is alphanumeric")
def test_lowercase_end(c):
    c.ft_isalnum("'z'").equals(1).assert_now()


@suite.case("'0' is alphanumeric")
def test_digit_start(c):
    c.ft_isalnum("'0'").equals(1).assert_now()


@suite.case("'9' is alphanumeric")
def test_digit_end(c):
    c.ft_isalnum("'9'").equals(1).assert_now()


@suite.case("'/' is not alphanumeric")
def test_before_digits(c):
    c.ft_isalnum("'/'").equals(0).assert_now()


@suite.case("':' is not alphanumeric")
def test_after_digits(c):
    c.ft_isalnum("':'").equals(0).assert_now()


@suite.case("'[' is not alphanumeric")
def test_after_uppercase(c):
    c.ft_isalnum("'['").equals(0).assert_now()


@suite.case("'`' is not alphanumeric")
def test_before_lowercase(c):
    c.ft_isalnum("'`'").equals(0).assert_now()


@suite.case("'{' is not alphanumeric")
def test_after_lowercase(c):
    c.ft_isalnum("'{'").equals(0).assert_now()


@suite.case("' ' is not alphanumeric")
def test_space(c):
    c.ft_isalnum("' '").equals(0).assert_now()


@suite.case("'!' is not alphanumeric")
def test_punctuation(c):
    c.ft_isalnum("'!'").equals(0).assert_now()


@suite.case("-1 is not alphanumeric")
def test_negative(c):
    c.ft_isalnum("-1").equals(0).assert_now()


@suite.case("127 is not alphanumeric")
def test_127(c):
    c.ft_isalnum("127").equals(0).assert_now()
