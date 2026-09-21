from framework import TestSuite

suite = TestSuite("ft_strchr")


def compare(c, original, argument, expected_offset):
    original_c = ", ".join(f"0x{byte:02x}" for byte in original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_buffer[] = {{{original_c}}};
        unsigned char libc_buffer[] = {{{original_c}}};

        char *ft = ft_strchr(
            (char *)ft_buffer,
            {argument}
        );

        char *libc = strchr(
            (char *)libc_buffer,
            {argument}
        );

        ptrdiff_t ft_offset = ft
            ? ft - (char *)ft_buffer
            : -1;

        ptrdiff_t libc_offset = libc
            ? libc - (char *)libc_buffer
            : -1;

        TEST_VALUE("ft", "%td", ft_offset);
        TEST_VALUE("libc", "%td", libc_offset);

        TEST_BUFFER(
            "ft_buffer",
            ft_buffer,
            sizeof(ft_buffer)
        );

        TEST_BUFFER(
            "libc_buffer",
            libc_buffer,
            sizeof(libc_buffer)
        );

        return 0;
    """)

    test.value("ft").equals(
        str(expected_offset if expected_offset is not None else -1),
        "Test ft_strchr() returned pointer",
    )

    test.value("libc").equals(
        str(expected_offset if expected_offset is not None else -1),
        "Reference returned pointer from strchr() from libc",
    ).reference()

    test.buffer("ft_buffer").equals(
        original,
        "Input buffer was modified",
    )

    test.buffer("libc_buffer").equals(
        original,
        "Input buffer was modified by strchr() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("finds first occurrence")
def test_first_occurrence(c):
    compare(
        c,
        b"hello world\x00",
        ord("l"),
        2,
    )


@suite.case("finds later occurrence")
def test_later_occurrence(c):
    compare(
        c,
        b"hello world\x00",
        ord("w"),
        6,
    )


@suite.case("finds last occurrence")
def test_last_occurrence(c):
    compare(
        c,
        b"hello world\x00",
        ord("d"),
        10,
    )


@suite.case("finds null terminator")
def test_null_terminator(c):
    compare(
        c,
        b"hello\x00",
        0,
        5,
    )


@suite.case("character not found")
def test_not_found(c):
    compare(
        c,
        b"hello world\x00",
        ord("z"),
        None,
    )


@suite.case("empty string")
def test_empty_string(c):
    compare(
        c,
        b"\x00",
        ord("a"),
        None,
    )


@suite.case("empty string finds null")
def test_empty_string_null(c):
    compare(
        c,
        b"\x00",
        0,
        0,
    )


@suite.case("uppercase and lowercase are different")
def test_case_sensitive(c):
    compare(
        c,
        b"Hello World\x00",
        ord("h"),
        None,
    )


@suite.case("binary data 1")
def test_binary_1(c):
    compare(
        c,
        b"\x01\x02\x03\x80\xff\x00",
        0x80,
        3,
    )


@suite.case("binary data 2")
def test_binary_2(c):
    compare(
        c,
        b"\x01\x02\x03\x80\xff\x00",
        0xFF,
        4,
    )


@suite.case("negative value")
def test_negative(c):
    compare(
        c,
        b"hello\x00",
        -1,
        None,
    )


@suite.case("character value 127")
def test_127(c):
    compare(
        c,
        b"hello\x7fworld\x00",
        127,
        5,
    )
