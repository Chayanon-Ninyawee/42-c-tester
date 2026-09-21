from framework import TestSuite, c_bytes

suite = TestSuite("ft_strlen")


def compare(c, original, expected):
    original_c = c_bytes(original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_buffer[] = {{{original_c}}};
        unsigned char libc_buffer[] = {{{original_c}}};

        size_t ft = ft_strlen((char *)ft_buffer);
        size_t libc = strlen((char *)libc_buffer);

        TEST_VALUE("ft", "%zu", ft);
        TEST_VALUE("libc", "%zu", libc);

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
        str(expected),
        "Test ft_strlen() returned value",
    )

    test.value("libc").equals(
        str(expected),
        "Reference returned value from strlen() from libc",
    ).reference()

    test.buffer("ft_buffer").equals(
        original,
        "Input buffer was modified",
    )

    test.buffer("libc_buffer").equals(
        original,
        "Input buffer was modified by libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("empty string has length 0")
def test_empty(c):
    compare(c, b"\x00", 0)


@suite.case("'a' has length 1")
def test_single_character(c):
    compare(c, b"a\x00", 1)


@suite.case("'hello' has length 5")
def test_basic(c):
    compare(c, b"hello\x00", 5)


@suite.case("'Hello World' has length 11")
def test_spaces(c):
    compare(c, b"Hello World\x00", 11)


@suite.case("string with spaces")
def test_multiple_spaces(c):
    compare(c, b"hello  world\x00", 12)


@suite.case("digits are counted")
def test_digits(c):
    compare(c, b"1234567890\x00", 10)


@suite.case("punctuation is counted")
def test_punctuation(c):
    compare(c, b"!@#$%^&*()\x00", 10)


@suite.case("uppercase and lowercase are counted")
def test_mixed_case(c):
    compare(c, b"AbCdEf\x00", 6)


@suite.case("newline is counted")
def test_newline(c):
    compare(c, b"hello\nworld\x00", 11)


@suite.case("tab is counted")
def test_tab(c):
    compare(c, b"hello\tworld\x00", 11)


@suite.case("long string")
def test_long_string(c):
    compare(
        c,
        b"This is a reasonably long string for testing\x00",
        44,
    )
