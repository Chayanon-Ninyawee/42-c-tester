from framework import TestSuite

suite = TestSuite("ft_isascii")


@suite.case("0 is ASCII")
def test_lower_bound(c):
    c.ft_isascii("0").equals(1).assert_now()


@suite.case("127 is ASCII")
def test_upper_bound(c):
    c.ft_isascii("127").equals(1).assert_now()


@suite.case("'A' is ASCII")
def test_uppercase(c):
    c.ft_isascii("'A'").equals(1).assert_now()


@suite.case("'z' is ASCII")
def test_lowercase(c):
    c.ft_isascii("'z'").equals(1).assert_now()


@suite.case("'0' is ASCII")
def test_digit(c):
    c.ft_isascii("'0'").equals(1).assert_now()


@suite.case("' ' is ASCII")
def test_space(c):
    c.ft_isascii("' '").equals(1).assert_now()


@suite.case("'\\n' is ASCII")
def test_newline(c):
    c.ft_isascii("'\\n'").equals(1).assert_now()


@suite.case("'\\t' is ASCII")
def test_tab(c):
    c.ft_isascii("'\\t'").equals(1).assert_now()


@suite.case("'~' is ASCII")
def test_tilde(c):
    c.ft_isascii("'~'").equals(1).assert_now()


@suite.case("-1 is not ASCII")
def test_negative(c):
    c.ft_isascii("-1").equals(0).assert_now()


@suite.case("128 is not ASCII")
def test_128(c):
    c.ft_isascii("128").equals(0).assert_now()


@suite.case("255 is not ASCII")
def test_255(c):
    c.ft_isascii("255").equals(0).assert_now()


@suite.case("256 is not ASCII")
def test_256(c):
    c.ft_isascii("256").equals(0).assert_now()
