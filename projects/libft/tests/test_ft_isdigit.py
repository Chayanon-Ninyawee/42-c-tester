from framework import TestSuite

suite = TestSuite("ft_isdigit")


@suite.case("'0' is a digit")
def test_zero(c):
    c.ft_isdigit("'0'").equals(1).assert_now()


@suite.case("'9' is a digit")
def test_nine(c):
    c.ft_isdigit("'9'").equals(1).assert_now()


@suite.case("'1' is a digit")
def test_one(c):
    c.ft_isdigit("'1'").equals(1).assert_now()


@suite.case("'5' is a digit")
def test_middle(c):
    c.ft_isdigit("'5'").equals(1).assert_now()


@suite.case("':' is not a digit")
def test_after_digits(c):
    c.ft_isdigit("':'").equals(0).assert_now()


@suite.case("'/' is not a digit")
def test_before_digits(c):
    c.ft_isdigit("'/'").equals(0).assert_now()


@suite.case("'A' is not a digit")
def test_uppercase(c):
    c.ft_isdigit("'A'").equals(0).assert_now()


@suite.case("'a' is not a digit")
def test_lowercase(c):
    c.ft_isdigit("'a'").equals(0).assert_now()


@suite.case("' ' is not a digit")
def test_space(c):
    c.ft_isdigit("' '").equals(0).assert_now()


@suite.case("'!' is not a digit")
def test_punctuation(c):
    c.ft_isdigit("'!'").equals(0).assert_now()


@suite.case("-1 is not a digit")
def test_negative(c):
    c.ft_isdigit("-1").equals(0).assert_now()


@suite.case("127 is not a digit")
def test_127(c):
    c.ft_isdigit("127").equals(0).assert_now()


@suite.case("128 is not a digit")
def test_128(c):
    c.ft_isdigit("128").equals(0).assert_now()
