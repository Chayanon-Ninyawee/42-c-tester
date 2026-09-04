from framework import TestSuite

suite = TestSuite("ft_calloc")


def compare(c, count, size, expected):
    ft = c.ft_calloc(
        count,
        size,
    )

    libc = c.calloc(
        count,
        size,
    )

    if expected is None:
        ft.is_null(
            "Test return value",
        )

        libc.is_null(
            "Test return value from calloc() from libc",
        ).assert_reference()
    else:
        ft.is_not_null(
            "Test return value",
        )

        libc.is_not_null(
            "Test return value from calloc() from libc",
        ).assert_reference()

    ft.assert_now()


@suite.case("allocates zeroed memory")
def test_basic(c):
    count = "5"
    size = "4"
    expected = 20

    compare(c, count, size, expected)


@suite.case("one element")
def test_one_element(c):
    count = "1"
    size = "1"
    expected = 1

    compare(c, count, size, expected)


@suite.case("one element with larger size")
def test_one_element_large_size(c):
    count = "1"
    size = "100"
    expected = 100

    compare(c, count, size, expected)


@suite.case("multiple elements")
def test_multiple_elements(c):
    count = "10"
    size = "8"
    expected = 80

    compare(c, count, size, expected)


@suite.case("zero count")
def test_zero_count(c):
    count = "0"
    size = "10"
    expected = 0

    compare(c, count, size, expected)


@suite.case("zero size")
def test_zero_size(c):
    count = "10"
    size = "0"
    expected = 0

    compare(c, count, size, expected)


@suite.case("both zero")
def test_both_zero(c):
    count = "0"
    size = "0"
    expected = 0

    compare(c, count, size, expected)


@suite.case("large allocation")
def test_large(c):
    count = "1000"
    size = "100"
    expected = 100000

    compare(c, count, size, expected)


@suite.case("overflow")
def test_overflow(c):
    count = "0x8000000000000000"
    size = "2"
    expected = None

    compare(c, count, size, expected)


@suite.case("overflow with large size")
def test_overflow_large_size(c):
    count = "0xffffffffffffffff"
    size = "2"
    expected = None

    compare(c, count, size, expected)
