from framework import TestSuite

suite = TestSuite("ft_memchr")


def compare(c, original, argument, n, expected_offset):
    ft_buffer = c.buffer(
        original,
        size=len(original),
        name="ft",
    )

    libc_buffer = c.buffer(
        original,
        size=len(original),
        name="libc",
    )

    ft = c.ft_memchr(
        ft_buffer,
        argument,
        n,
    )

    libc = c.memchr(
        libc_buffer,
        argument,
        n,
    )

    if expected_offset is None:
        libc.is_null(
            "Test return value from memchr() from libc",
        )
        ft.is_null(
            "Test return value",
        )
    else:
        libc.returned_pointer_is(
            libc_buffer.offset(expected_offset),
            "Test returned pointer from memchr() from libc",
        )
        ft.returned_pointer_is(
            ft_buffer.offset(expected_offset),
            "Test returned pointer",
        )

    libc.buffer_equals(
        libc_buffer,
        original,
        "Input buffer was modified by libc",
    ).assert_reference()

    ft.buffer_equals(
        ft_buffer,
        original,
        "Input buffer was modified",
    )
    ft.malloc_count_equals(
        0,
        "Test malloc count",
    ).assert_now()


@suite.case("finds first occurrence")
def test_first_occurrence(c):
    original = b"hello world"
    argument = str(ord("l"))
    n = "11"
    expected_offset = 2

    compare(c, original, argument, n, expected_offset)


@suite.case("finds later occurrence")
def test_later_occurrence(c):
    original = b"hello world"
    argument = str(ord("w"))
    n = "11"
    expected_offset = 6

    compare(c, original, argument, n, expected_offset)


@suite.case("finds last occurrence")
def test_last_occurrence(c):
    original = b"hello world"
    argument = str(ord("d"))
    n = "11"
    expected_offset = 10

    compare(c, original, argument, n, expected_offset)


@suite.case("character not found")
def test_not_found(c):
    original = b"hello world"
    argument = str(ord("z"))
    n = "11"
    expected_offset = None

    compare(c, original, argument, n, expected_offset)


@suite.case("does not search past n")
def test_stops_at_n(c):
    original = b"hello world"
    argument = str(ord("w"))
    n = "5"
    expected_offset = None

    compare(c, original, argument, n, expected_offset)


@suite.case("finds character at n - 1")
def test_at_end_of_range(c):
    original = b"hello world"
    argument = str(ord("o"))
    n = "5"
    expected_offset = 4

    compare(c, original, argument, n, expected_offset)


@suite.case("zero bytes")
def test_zero(c):
    original = b"hello world"
    argument = str(ord("h"))
    n = "0"
    expected_offset = None

    compare(c, original, argument, n, expected_offset)


@suite.case("one byte")
def test_one(c):
    original = b"hello world"
    argument = str(ord("h"))
    n = "1"
    expected_offset = 0

    compare(c, original, argument, n, expected_offset)


@suite.case("binary data")
def test_binary(c):
    original = b"\x01\x02\x80\xff\x00\x7f"
    argument = str(0x80)
    n = "6"
    expected_offset = 2

    compare(c, original, argument, n, expected_offset)


@suite.case("unsigned char comparison")
def test_unsigned_char(c):
    original = b"\xff\x80\x01\x7f"
    argument = "255"
    n = "4"
    expected_offset = 0

    compare(c, original, argument, n, expected_offset)


@suite.case("negative c matches unsigned byte")
def test_negative_c(c):
    original = b"\xff\x80\x01\x7f"
    argument = "-1"
    n = "4"
    expected_offset = 0

    compare(c, original, argument, n, expected_offset)


@suite.case("empty buffer")
def test_empty(c):
    # FIXME: doesn't support zero size buffer yet
    original = b"abcd"
    argument = str(ord("a"))
    n = "0"
    expected_offset = None

    compare(c, original, argument, n, expected_offset)
