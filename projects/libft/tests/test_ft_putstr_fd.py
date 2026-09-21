from framework import TestSuite, c_bytes

suite = TestSuite("ft_putstr_fd")


def compare(c, original, fd, expected):
    original_c = c_bytes(original)

    test = c.include(
        "libft.h",
    ).code(
        f"""
        unsigned char ft_s[] = {{{original_c}}};

        ft_putstr_fd(
            (char *)ft_s,
            {fd}
        );

        TEST_BUFFER(
            "ft_s",
            ft_s,
            sizeof(ft_s)
        );

        return 0;
        """
    )

    if fd == 1:
        test.stdout().equals(
            expected,
            "String was not written to stdout",
        )

        test.stderr().equals(
            b"",
            "Unexpected output on stderr",
        )
    elif fd == 2:
        test.stdout().equals(
            b"",
            "Unexpected output on stdout",
        )

        test.stderr().equals(
            expected,
            "String was not written to stderr",
        )
    else:
        test.fd(fd).equals(
            expected,
            "String was not written to the specified fd",
        )

    test.buffer("ft_s").equals(
        original,
        "Input string was modified",
    )

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("stdout")
def test_stdout(c):
    compare(
        c,
        b"hello world\x00",
        1,
        b"hello world",
    )


@suite.case("stderr")
def test_stderr(c):
    compare(
        c,
        b"hello world\x00",
        2,
        b"hello world",
    )


@suite.case("custom file descriptor")
def test_custom_fd(c):
    compare(
        c,
        b"hello world\x00",
        3,
        b"hello world",
    )


@suite.case("empty string")
def test_empty(c):
    compare(
        c,
        b"\x00",
        1,
        b"",
    )


@suite.case("single character")
def test_single_character(c):
    compare(
        c,
        b"a\x00",
        1,
        b"a",
    )


@suite.case("spaces")
def test_spaces(c):
    compare(
        c,
        b"hello world\x00",
        1,
        b"hello world",
    )


@suite.case("multiple spaces")
def test_multiple_spaces(c):
    compare(
        c,
        b"hello  world   test\x00",
        1,
        b"hello  world   test",
    )


@suite.case("digits")
def test_digits(c):
    compare(
        c,
        b"1234567890\x00",
        1,
        b"1234567890",
    )


@suite.case("uppercase and lowercase")
def test_mixed_case(c):
    compare(
        c,
        b"AbCdEfGh\x00",
        1,
        b"AbCdEfGh",
    )


@suite.case("punctuation")
def test_punctuation(c):
    compare(
        c,
        b"!@#$%^&*()[]{};:'\",.<>/?\x00",
        1,
        b"!@#$%^&*()[]{};:'\",.<>/?",
    )


@suite.case("newline")
def test_newline(c):
    compare(
        c,
        b"hello\nworld\x00",
        1,
        b"hello\nworld",
    )


@suite.case("tab")
def test_tab(c):
    compare(
        c,
        b"hello\tworld\x00",
        1,
        b"hello\tworld",
    )


@suite.case("carriage return")
def test_carriage_return(c):
    compare(
        c,
        b"hello\rworld\x00",
        1,
        b"hello\rworld",
    )


@suite.case("all whitespace")
def test_whitespace(c):
    compare(
        c,
        b" \t\n\r\x00",
        1,
        b" \t\n\r",
    )


@suite.case("binary bytes")
def test_binary(c):
    compare(
        c,
        b"\x01\x02\x03\x04\x05\x00",
        1,
        b"\x01\x02\x03\x04\x05",
    )


@suite.case("high bytes")
def test_high_bytes(c):
    compare(
        c,
        b"\x80\x81\xfe\xff\x00",
        1,
        b"\x80\x81\xfe\xff",
    )


@suite.case("string with embedded null")
def test_embedded_null(c):
    compare(
        c,
        b"hello\x00world\x00",
        1,
        b"hello",
    )


@suite.case("long string")
def test_long_string(c):
    original = b"hello world " * 1000 + b"\x00"
    expected = b"hello world " * 1000

    compare(
        c,
        original,
        1,
        expected,
    )


@suite.case("custom fd with empty string")
def test_custom_fd_empty(c):
    compare(
        c,
        b"\x00",
        3,
        b"",
    )


@suite.case("custom fd with special characters")
def test_custom_fd_special(c):
    compare(
        c,
        b"!@#$%^&*()\n\t\x00",
        3,
        b"!@#$%^&*()\n\t",
    )
