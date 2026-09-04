from framework import TestSuite

suite = TestSuite("ft_strnstr")


def compare(c, big_original, little_original, len_value, expected_offset):
    ft_buffer = c.buffer(
        big_original,
        size=len(big_original),
        type="char",
        name="ft",
    )
    ft_little = c.buffer(
        little_original,
        size=len(little_original),
        type="char",
        name="ft_little",
    )

    libc_buffer = c.buffer(
        big_original,
        size=len(big_original),
        type="char",
        name="libc",
    )
    libc_little = c.buffer(
        little_original,
        size=len(little_original),
        type="char",
        name="libc_little",
    )

    ft = c.ft_strnstr(
        ft_buffer,
        ft_little,
        len_value,
    )

    libc = c.strnstr(
        libc_buffer,
        libc_little,
        len_value,
    )

    if expected_offset is None:
        libc.is_null(
            "Test return value from strnstr() from libc",
        )

        ft.is_null(
            "Test return value",
        )
    else:
        libc.returned_pointer_is(
            libc_buffer.offset(expected_offset),
            "Test returned pointer from strnstr() from libc",
        )

        ft.returned_pointer_is(
            ft_buffer.offset(expected_offset),
            "Test returned pointer",
        )

    libc.buffer_equals(
        libc_buffer,
        big_original,
        "big buffer was modified by libc",
    )
    libc.buffer_equals(
        libc_little,
        little_original,
        "little buffer was modified by libc",
    ).assert_reference()

    ft.buffer_equals(
        ft_buffer,
        big_original,
        "big buffer was modified",
    )
    ft.buffer_equals(
        ft_little,
        little_original,
        "little buffer was modified",
    ).assert_now()


@suite.case("finds substring")
def test_normal(c):
    big_original = b"hello world\x00"
    little_original = b"world\x00"
    len_value = "11"
    expected_offset = 6

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("finds first occurrence")
def test_first_occurrence(c):
    big_original = b"hello hello\x00"
    little_original = b"hello\x00"
    len_value = "11"
    expected_offset = 0

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("finds first occurrence only")
def test_multiple_occurrences(c):
    big_original = b"abcabcabc\x00"
    little_original = b"abc\x00"
    len_value = "9"
    expected_offset = 0

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("substring not found")
def test_not_found(c):
    big_original = b"hello world\x00"
    little_original = b"xyz\x00"
    len_value = "11"
    expected_offset = None

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("empty little")
def test_empty_little(c):
    big_original = b"hello world\x00"
    little_original = b"\x00"
    len_value = "11"
    expected_offset = 0

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("empty big")
def test_empty_big(c):
    big_original = b"\x00"
    little_original = b"hello\x00"
    len_value = "1"
    expected_offset = None

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("empty big and little")
def test_both_empty(c):
    big_original = b"\x00"
    little_original = b"\x00"
    len_value = "1"
    expected_offset = 0

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("length stops before match")
def test_length_too_short(c):
    big_original = b"hello world\x00"
    little_original = b"world\x00"
    len_value = "10"
    expected_offset = None

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("length includes match")
def test_length_includes_match(c):
    big_original = b"hello world\x00"
    little_original = b"world\x00"
    len_value = "11"
    expected_offset = 6

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("match ends exactly at length")
def test_match_at_boundary(c):
    big_original = b"hello world\x00"
    little_original = b"world\x00"
    len_value = "11"
    expected_offset = 6

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("partial match at end")
def test_partial_match(c):
    big_original = b"hello wor\x00"
    little_original = b"world\x00"
    len_value = "9"
    expected_offset = None

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("zero length")
def test_zero_length(c):
    big_original = b"hello world\x00"
    little_original = b"hello\x00"
    len_value = "0"
    expected_offset = None

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("one byte length")
def test_one_byte(c):
    big_original = b"hello\x00"
    little_original = b"h\x00"
    len_value = "1"
    expected_offset = 0

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("substring starts at boundary")
def test_boundary(c):
    big_original = b"1234567890abc\x00"
    little_original = b"abc\x00"
    len_value = "13"
    expected_offset = 10

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("binary data")
def test_binary(c):
    big_original = b"\x01\x02\x80\xff\x00\x7f"
    little_original = b"\x80\xff\x00"
    len_value = "6"
    expected_offset = 2

    compare(c, big_original, little_original, len_value, expected_offset)
