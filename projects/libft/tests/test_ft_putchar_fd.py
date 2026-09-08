from framework import CFileDescriptor, TestSuite

suite = TestSuite("ft_putchar_fd")


def compare_stdout(c, character, expected):
    ft = c.ft_putchar_fd(
        character,
        1,
    )

    ft.run()

    ft.stdout_equals(
        expected,
        "Character was not written to stdout",
    )
    ft.stderr_equals(
        b"",
        "Unexpected output on stderr",
    )
    ft.assert_now()


def compare_stderr(c, character, expected):
    ft = c.ft_putchar_fd(
        character,
        2,
    )

    ft.run()

    ft.stdout_equals(
        b"",
        "Unexpected output on stdout",
    )
    ft.stderr_equals(
        expected,
        "Character was not written to stderr",
    )
    ft.assert_now()


def compare_fd(c, character, fd, expected):
    ft = c.ft_putchar_fd(
        character,
        fd,
    )

    ft.run()

    ft.stdout_equals(
        b"",
        "Unexpected output on stdout",
    )
    ft.stderr_equals(
        b"",
        "Unexpected output on stderr",
    )
    ft.fd_equals(
        fd,
        expected,
        "Character was not written to the specified fd",
    )
    ft.assert_now()


@suite.case("stdout")
def test_stdout(c):
    compare_stdout(c, "'A'", b"A")


@suite.case("stderr")
def test_stderr(c):
    compare_stderr(c, "'A'", b"A")


@suite.case("custom file descriptor")
def test_custom_fd(c):
    fd = c.fd()

    compare_fd(c, "'A'", fd, b"A")


@suite.case("lowercase")
def test_lowercase(c):
    compare_stdout(c, "'z'", b"z")


@suite.case("uppercase")
def test_uppercase(c):
    compare_stdout(c, "'Z'", b"Z")


@suite.case("digit")
def test_digit(c):
    compare_stdout(c, "'5'", b"5")


@suite.case("space")
def test_space(c):
    compare_stdout(c, "' '", b" ")


@suite.case("newline")
def test_newline(c):
    compare_stdout(c, "'\\n'", b"\n")


@suite.case("tab")
def test_tab(c):
    compare_stdout(c, "'\\t'", b"\t")


@suite.case("null character")
def test_null(c):
    compare_stdout(c, "'\\0'", b"\0")


@suite.case("high byte")
def test_high_byte(c):
    fd = c.fd()

    compare_fd(c, "0x80", fd, b"\x80")


@suite.case("0xFF byte")
def test_ff(c):
    fd = c.fd()

    compare_fd(c, "0xff", fd, b"\xff")
