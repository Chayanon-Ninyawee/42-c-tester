from framework import TestSuite

# NOTE: This test can be flaky since memset by libc only require return value to be >, =, < to 0 depending on the comparasion but not promising any actual value
suite = TestSuite("ft_memcmp")


def compare(c, s1_original, s2_original, n, expected):
    ft_s1 = c.buffer(
        s1_original,
        size=len(s1_original),
        name="ft_s1",
    )
    ft_s2 = c.buffer(
        s2_original,
        size=len(s2_original),
        name="ft_s2",
    )

    libc_s1 = c.buffer(
        s1_original,
        size=len(s1_original),
        name="libc_s1",
    )
    libc_s2 = c.buffer(
        s2_original,
        size=len(s2_original),
        name="libc_s2",
    )

    ft = c.ft_memcmp(
        ft_s1,
        ft_s2,
        n,
    )

    libc = c.memcmp(
        libc_s1,
        libc_s2,
        n,
    )

    libc.equals(
        expected,
        "Test with memcmp() from libc",
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
    )
    ft.malloc_count_equals(
        0,
        "Test malloc count",
    ).assert_now()


@suite.case("identical buffers")
def test_identical(c):
    s1_original = b"hello"
    s2_original = b"hello"
    n = "5"
    expected = 0

    compare(c, s1_original, s2_original, n, expected)


@suite.case("s1 is smaller")
def test_s1_smaller(c):
    s1_original = b"hello"
    s2_original = b"jello"
    n = "5"
    expected = ord("h") - ord("j")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("s1 is greater")
def test_s1_greater(c):
    s1_original = b"jello"
    s2_original = b"hello"
    n = "5"
    expected = ord("j") - ord("h")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("difference in middle")
def test_middle_difference(c):
    s1_original = b"hello"
    s2_original = b"heLlo"
    n = "5"
    expected = ord("l") - ord("L")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("difference at last byte")
def test_last_difference(c):
    s1_original = b"hella"
    s2_original = b"hello"
    n = "5"
    expected = ord("a") - ord("o")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("difference after n")
def test_difference_after_n(c):
    s1_original = b"helloX"
    s2_original = b"helloY"
    n = "5"
    expected = 0

    compare(c, s1_original, s2_original, n, expected)


@suite.case("difference at n - 1")
def test_difference_at_n_minus_one(c):
    s1_original = b"helloX"
    s2_original = b"helloY"
    n = "6"
    expected = ord("X") - ord("Y")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("zero bytes")
def test_zero(c):
    s1_original = b"hello"
    s2_original = b"world"
    n = "0"
    expected = 0

    compare(c, s1_original, s2_original, n, expected)


@suite.case("one byte")
def test_one(c):
    s1_original = b"hello"
    s2_original = b"jello"
    n = "1"
    expected = ord("h") - ord("j")

    compare(c, s1_original, s2_original, n, expected)


@suite.case("different lengths")
def test_different_lengths(c):
    s1_original = b"hello"
    s2_original = b"hello world"
    n = "5"
    expected = 0

    compare(c, s1_original, s2_original, n, expected)


@suite.case("null byte")
def test_null_byte(c):
    s1_original = b"hello\x00wor\00ld"
    s2_original = b"hello\x00wor\00ld"
    n = "11"
    expected = 0

    compare(c, s1_original, s2_original, n, expected)


@suite.case("binary data")
def test_binary(c):
    s1_original = b"\x01\x80\xff\x7f"
    s2_original = b"\x01\x80\x7f\x7f"
    n = "4"
    expected = 0xFF - 0x7F

    compare(c, s1_original, s2_original, n, expected)


@suite.case("unsigned byte comparison")
def test_unsigned_bytes(c):
    s1_original = b"\xff"
    s2_original = b"\x01"
    n = "1"
    expected = 0xFF - 0x01

    compare(c, s1_original, s2_original, n, expected)


@suite.case("empty buffers")
def test_empty(c):
    # FIXME: doesn't support zero size buffer yet
    s1_original = b"abcd"
    s2_original = b"efgh"
    n = "0"
    expected = 0

    compare(c, s1_original, s2_original, n, expected)
