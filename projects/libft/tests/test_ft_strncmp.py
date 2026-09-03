from framework import TestSuite

suite = TestSuite("ft_strncmp")


def compare(c, s1_original, s2_original, n, expected):
    ft_s1 = c.buffer(
        s1_original,
        size=len(s1_original),
        type="char",
        name="ft_s1",
    )
    ft_s2 = c.buffer(
        s2_original,
        size=len(s2_original),
        type="char",
        name="ft_s2",
    )

    libc_s1 = c.buffer(
        s1_original,
        size=len(s1_original),
        type="char",
        name="libc_s1",
    )
    libc_s2 = c.buffer(
        s2_original,
        size=len(s2_original),
        type="char",
        name="libc_s2",
    )

    ft = c.ft_strncmp(
        ft_s1,
        ft_s2,
        n,
    )

    libc = c.strncmp(
        libc_s1,
        libc_s2,
        n,
    )

    libc.equals(
        expected,
        "Test with strncmp() from libc",
    )
    libc.buffer_equals(
        libc_s1,
        s1_original,
        "s1 buffer was modified by libc",
    )
    libc.buffer_equals(
        libc_s2,
        s2_original,
        "s2 buffer was modified by libc",
    ).assert_reference()

    ft.equals(
        expected,
        "Test with value",
    )
    ft.buffer_equals(
        ft_s1,
        s1_original,
        "s1 buffer was modified",
    )
    ft.buffer_equals(
        ft_s2,
        s2_original,
        "s2 buffer was modified",
    ).assert_now()


@suite.case("identical strings")
def test_identical(c):
    s1_original = b"hello\x00"
    s2_original = b"hello\x00"
    n = "5"
    expected = 0

    compare(c, s1_original, s2_original, n, expected)


@suite.case("different strings")
def test_different(c):
    s1_original = b"hello\x00"
    s2_original = b"world\x00"
    n = "5"
    expected = ord("h") - ord("w")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("s1 is smaller")
def test_s1_smaller(c):
    s1_original = b"abc\x00"
    s2_original = b"abd\x00"
    n = "3"
    expected = ord("c") - ord("d")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("s1 is greater")
def test_s1_greater(c):
    s1_original = b"abd\x00"
    s2_original = b"abc\x00"
    n = "3"
    expected = ord("d") - ord("c")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("difference after n")
def test_difference_after_n(c):
    s1_original = b"helloX\x00"
    s2_original = b"helloY\x00"
    n = "5"
    expected = 0

    compare(c, s1_original, s2_original, n, expected)


@suite.case("difference at n")
def test_difference_at_n(c):
    s1_original = b"helloX\x00"
    s2_original = b"helloY\x00"
    n = "6"
    expected = ord("X") - ord("Y")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("n is zero")
def test_zero(c):
    s1_original = b"hello\x00"
    s2_original = b"world\x00"
    n = "0"
    expected = 0

    compare(c, s1_original, s2_original, n, expected)


@suite.case("n is one")
def test_one(c):
    s1_original = b"hello\x00"
    s2_original = b"world\x00"
    n = "1"
    expected = ord("h") - ord("w")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("empty first string")
def test_empty_first(c):
    s1_original = b"\x00"
    s2_original = b"hello\x00"
    n = "5"
    expected = -ord("h")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("empty second string")
def test_empty_second(c):
    s1_original = b"hello\x00"
    s2_original = b"\x00"
    n = "5"
    expected = ord("h")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("one string is prefix")
def test_prefix(c):
    s1_original = b"hello\x00"
    s2_original = b"hello world\x00"
    n = "10"
    expected = -ord(" ")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("binary data")
def test_binary(c):
    s1_original = b"\x01\x80\xff\x00"
    s2_original = b"\x01\x80\x7f\x00"
    n = "4"
    expected = 0xFF - 0x7F

    compare(c, s1_original, s2_original, n, expected)


@suite.case("comparison stops at null")
def test_null_terminator(c):
    s1_original = b"abc\x00xxx"
    s2_original = b"abc\x00yyy"
    n = "7"
    expected = 0

    compare(c, s1_original, s2_original, n, expected)
