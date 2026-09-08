from framework import TestSuite

suite = TestSuite("ft_putendl_fd")


def compare(c, original, fd, expected):
    ft_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s",
    )

    ft = c.ft_putendl_fd(
        ft_s,
        fd,
    )

    ft.run()

    if fd == 1:
        ft.stdout_equals(
            expected,
            "String was not written to stdout",
        )
        ft.stderr_equals(
            b"",
            "Unexpected output on stderr",
        )
    elif fd == 2:
        ft.stdout_equals(
            b"",
            "Unexpected output on stdout",
        )
        ft.stderr_equals(
            expected,
            "String was not written to stderr",
        )
    else:
        ft.fd_equals(
            fd,
            expected,
            "String was not written to the specified fd",
        )

    ft.buffer_equals(
        ft_s,
        original,
        "Input string was modified",
    )
    ft.assert_now()


@suite.case("stdout")
def test_stdout(c):
    original = b"hello world\x00"
    expected = b"hello world\n"

    compare(c, original, 1, expected)


@suite.case("stderr")
def test_stderr(c):
    original = b"hello world\x00"
    expected = b"hello world\n"

    compare(c, original, 2, expected)


@suite.case("custom file descriptor")
def test_custom_fd(c):
    fd = c.fd()
    original = b"hello world\x00"
    expected = b"hello world\n"

    compare(c, original, fd, expected)


@suite.case("empty string")
def test_empty(c):
    original = b"\x00"
    expected = b"\n"

    compare(c, original, 1, expected)


@suite.case("single character")
def test_single_character(c):
    original = b"a\x00"
    expected = b"a\n"

    compare(c, original, 1, expected)


@suite.case("spaces")
def test_spaces(c):
    original = b"hello world\x00"
    expected = b"hello world\n"

    compare(c, original, 1, expected)


@suite.case("multiple spaces")
def test_multiple_spaces(c):
    original = b"hello  world   test\x00"
    expected = b"hello  world   test\n"

    compare(c, original, 1, expected)


@suite.case("digits")
def test_digits(c):
    original = b"1234567890\x00"
    expected = b"1234567890\n"

    compare(c, original, 1, expected)


@suite.case("uppercase and lowercase")
def test_mixed_case(c):
    original = b"AbCdEfGh\x00"
    expected = b"AbCdEfGh\n"

    compare(c, original, 1, expected)


@suite.case("punctuation")
def test_punctuation(c):
    original = b"!@#$%^&*()[]{};:'\",.<>/?\x00"
    expected = b"!@#$%^&*()[]{};:'\",.<>/?\n"

    compare(c, original, 1, expected)


@suite.case("newline in string")
def test_newline(c):
    original = b"hello\nworld\x00"
    expected = b"hello\nworld\n"

    compare(c, original, 1, expected)


@suite.case("tab in string")
def test_tab(c):
    original = b"hello\tworld\x00"
    expected = b"hello\tworld\n"

    compare(c, original, 1, expected)


@suite.case("carriage return")
def test_carriage_return(c):
    original = b"hello\rworld\x00"
    expected = b"hello\rworld\n"

    compare(c, original, 1, expected)


@suite.case("all whitespace")
def test_whitespace(c):
    original = b" \t\n\r\x00"
    expected = b" \t\n\r\n"

    compare(c, original, 1, expected)


@suite.case("binary bytes")
def test_binary(c):
    original = b"\x01\x02\x03\x04\x05\x00"
    expected = b"\x01\x02\x03\x04\x05\n"

    compare(c, original, 1, expected)


@suite.case("high bytes")
def test_high_bytes(c):
    original = b"\x80\x81\xfe\xff\x00"
    expected = b"\x80\x81\xfe\xff\n"

    compare(c, original, 1, expected)


@suite.case("string with embedded null")
def test_embedded_null(c):
    original = b"hello\x00world\x00"
    expected = b"hello\n"

    compare(c, original, 1, expected)


@suite.case("long string")
def test_long_string(c):
    original = b"hello world " * 1000 + b"\x00"
    expected = b"hello world " * 1000 + b"\n"

    compare(c, original, 1, expected)


@suite.case("custom fd with empty string")
def test_custom_fd_empty(c):
    fd = c.fd()
    original = b"\x00"
    expected = b"\n"

    compare(c, original, fd, expected)


@suite.case("custom fd with special characters")
def test_custom_fd_special(c):
    fd = c.fd()
    original = b"!@#$%^&*()\n\t\x00"
    expected = b"!@#$%^&*()\n\t\n"

    compare(c, original, fd, expected)
