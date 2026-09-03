from framework import TestSuite

suite = TestSuite("ft_strrchr")


def compare(c, original, argument, expected_offset):
    ft_buffer = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft",
    )

    libc_buffer = c.buffer(
        original,
        size=len(original),
        type="char",
        name="libc",
    )

    ft = c.ft_strrchr(
        ft_buffer,
        argument,
    )

    libc = c.strrchr(
        libc_buffer,
        argument,
    )

    if expected_offset is None:
        libc.is_null(
            "Test return value from strrchr() from libc",
        )

        ft.is_null(
            "Test return value",
        )
    else:
        libc.returned_pointer_is(
            libc_buffer.offset(expected_offset),
            "Test returned pointer from strrchr() from libc",
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
    ).assert_now()


@suite.case("finds last occurrence")
def test_last_occurrence(c):
    original = b"hello world\x00"
    argument = str(ord("l"))
    expected_offset = 9

    compare(c, original, argument, expected_offset)


@suite.case("finds only occurrence")
def test_only_occurrence(c):
    original = b"hello world\x00"
    argument = str(ord("w"))
    expected_offset = 6

    compare(c, original, argument, expected_offset)


@suite.case("finds first character")
def test_first_character(c):
    original = b"hello world\x00"
    argument = str(ord("h"))
    expected_offset = 0

    compare(c, original, argument, expected_offset)


@suite.case("finds null terminator")
def test_null_terminator(c):
    original = b"hello\x00"
    argument = "0"
    expected_offset = 5

    compare(c, original, argument, expected_offset)


@suite.case("character not found")
def test_not_found(c):
    original = b"hello world\x00"
    argument = str(ord("z"))
    expected_offset = None

    compare(c, original, argument, expected_offset)


@suite.case("empty string")
def test_empty_string(c):
    original = b"\x00"
    argument = str(ord("a"))
    expected_offset = None

    compare(c, original, argument, expected_offset)


@suite.case("empty string finds null")
def test_empty_string_null(c):
    original = b"\x00"
    argument = "0"
    expected_offset = 0

    compare(c, original, argument, expected_offset)


@suite.case("string finds null")
def test_string_find_null(c):
    original = b"hello world\x00"
    argument = "0"
    expected_offset = 11

    compare(c, original, argument, expected_offset)


@suite.case("case sensitive")
def test_case_sensitive(c):
    original = b"Hello World\x00"
    argument = str(ord("h"))
    expected_offset = None

    compare(c, original, argument, expected_offset)


@suite.case("binary data 1")
def test_binary_1(c):
    original = b"\x01\x80\x02\x80\xff\x00"
    argument = str(0x80)
    expected_offset = 3

    compare(c, original, argument, expected_offset)


@suite.case("binary data 2")
def test_binary_2(c):
    original = b"\xff\x80\x02\x80\xff\x00"
    argument = str(0xFF)
    expected_offset = 4

    compare(c, original, argument, expected_offset)


@suite.case("negative value")
def test_negative(c):
    original = b"hello\x00"
    argument = "-1"
    expected_offset = None

    compare(c, original, argument, expected_offset)


@suite.case("character value 127")
def test_127(c):
    original = b"hello\x7fworld\x7f\x00"
    argument = "127"
    expected_offset = 11

    compare(c, original, argument, expected_offset)
