from framework import TestSuite

suite = TestSuite("ft_putchar_fd")


def compare_stdout(c, character, expected):
    test = c.include(
        "libft.h",
    ).code(
        f"""
        ft_putchar_fd(
            {character},
            1
        );

        return 0;
        """
    )

    test.stdout().equals(
        expected,
        "Character was not written to stdout",
    )

    test.stderr().equals(
        b"",
        "Unexpected output on stderr",
    )

    test.assert_now()


def compare_stderr(c, character, expected):
    test = c.include(
        "libft.h",
    ).code(
        f"""
        ft_putchar_fd(
            {character},
            2
        );

        return 0;
        """
    )

    test.stdout().equals(
        b"",
        "Unexpected output on stdout",
    )

    test.stderr().equals(
        expected,
        "Character was not written to stderr",
    )

    test.assert_now()


def compare_fd(c, character, fd, expected):
    test = c.include(
        "libft.h",
    ).code(
        f"""
        ft_putchar_fd(
            {character},
            {fd}
        );

        return 0;
        """
    )

    test.stdout().equals(
        b"",
        "Unexpected output on stdout",
    )

    test.stderr().equals(
        b"",
        "Unexpected output on stderr",
    )

    test.fd(fd).equals(
        expected,
        "Character was not written to the specified fd",
    )

    test.assert_now()


@suite.case("stdout")
def test_stdout(c):
    compare_stdout(c, "'A'", b"A")


@suite.case("stderr")
def test_stderr(c):
    compare_stderr(c, "'A'", b"A")


@suite.case("custom file descriptor")
def test_custom_fd(c):
    compare_fd(c, "'A'", 3, b"A")


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
    compare_fd(c, "0x80", 3, b"\x80")


@suite.case("0xFF byte")
def test_ff(c):
    compare_fd(c, "0xff", 3, b"\xff")
