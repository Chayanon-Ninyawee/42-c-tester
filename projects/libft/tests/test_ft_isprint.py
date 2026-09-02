from framework import TestSuite

suite = TestSuite("ft_isprint")


@suite.case("32 is printable")
def test_lower_bound(c):
    c.ft_isprint("32").equals(1).assert_now()


@suite.case("126 is printable")
def test_upper_bound(c):
    c.ft_isprint("126").equals(1).assert_now()


@suite.case("' ' is printable")
def test_space(c):
    c.ft_isprint("' '").equals(1).assert_now()


@suite.case("'!' is printable")
def test_exclamation(c):
    c.ft_isprint("'!'").equals(1).assert_now()


@suite.case("'A' is printable")
def test_uppercase(c):
    c.ft_isprint("'A'").equals(1).assert_now()


@suite.case("'z' is printable")
def test_lowercase(c):
    c.ft_isprint("'z'").equals(1).assert_now()


@suite.case("'0' is printable")
def test_digit(c):
    c.ft_isprint("'0'").equals(1).assert_now()


@suite.case("'~' is printable")
def test_tilde(c):
    c.ft_isprint("'~'").equals(1).assert_now()


@suite.case("31 is not printable")
def test_before_lower_bound(c):
    c.ft_isprint("31").equals(0).assert_now()


@suite.case("127 is not printable")
def test_after_upper_bound(c):
    c.ft_isprint("127").equals(0).assert_now()


@suite.case("0 is not printable")
def test_null(c):
    c.ft_isprint("0").equals(0).assert_now()


@suite.case("'\\n' is not printable")
def test_newline(c):
    c.ft_isprint("'\\n'").equals(0).assert_now()


@suite.case("'\\t' is not printable")
def test_tab(c):
    c.ft_isprint("'\\t'").equals(0).assert_now()


@suite.case("-1 is not printable")
def test_negative(c):
    c.ft_isprint("-1").equals(0).assert_now()


@suite.case("128 is not printable")
def test_128(c):
    c.ft_isprint("128").equals(0).assert_now()


@suite.case("255 is not printable")
def test_255(c):
    c.ft_isprint("255").equals(0).assert_now()
