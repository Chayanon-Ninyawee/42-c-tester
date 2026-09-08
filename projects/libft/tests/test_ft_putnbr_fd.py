from framework import TestSuite

suite = TestSuite("ft_putnbr_fd")


def compare(c, number, fd, expected):
    ft = c.ft_putnbr_fd(
        number,
        fd,
    )

    ft.run()

    if fd == 1:
        ft.stdout_equals(
            expected,
            "Number was not written to stdout",
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
            "Number was not written to stderr",
        )
    else:
        ft.fd_equals(
            fd,
            expected,
            "Number was not written to the specified fd",
        )

    ft.malloc_count_equals(
        0,
        "ft_putnbr_fd must not allocate memory",
    )
    ft.assert_now()


@suite.case("zero")
def test_zero(c):
    compare(
        c,
        0,
        1,
        b"0",
    )


@suite.case("positive number")
def test_positive(c):
    compare(
        c,
        42,
        1,
        b"42",
    )


@suite.case("negative number")
def test_negative(c):
    compare(
        c,
        -42,
        1,
        b"-42",
    )


@suite.case("single digit")
def test_single_digit(c):
    compare(
        c,
        7,
        1,
        b"7",
    )


@suite.case("negative single digit")
def test_negative_single_digit(c):
    compare(
        c,
        -7,
        1,
        b"-7",
    )


@suite.case("multiple digits")
def test_multiple_digits(c):
    compare(
        c,
        123456789,
        1,
        b"123456789",
    )


@suite.case("negative multiple digits")
def test_negative_multiple_digits(c):
    compare(
        c,
        -123456789,
        1,
        b"-123456789",
    )


@suite.case("INT_MAX")
def test_int_max(c):
    compare(
        c,
        2147483647,
        1,
        b"2147483647",
    )


@suite.case("INT_MIN")
def test_int_min(c):
    compare(
        c,
        -2147483648,
        1,
        b"-2147483648",
    )


@suite.case("stdout")
def test_stdout(c):
    compare(
        c,
        12345,
        1,
        b"12345",
    )


@suite.case("stderr")
def test_stderr(c):
    compare(
        c,
        12345,
        2,
        b"12345",
    )


@suite.case("custom file descriptor")
def test_custom_fd(c):
    fd = c.fd()

    compare(
        c,
        12345,
        fd,
        b"12345",
    )


@suite.case("custom fd negative")
def test_custom_fd_negative(c):
    fd = c.fd()

    compare(
        c,
        -987654,
        fd,
        b"-987654",
    )


@suite.case("custom fd zero")
def test_custom_fd_zero(c):
    fd = c.fd()

    compare(
        c,
        0,
        fd,
        b"0",
    )


@suite.case("small positive")
def test_small_positive(c):
    compare(
        c,
        10,
        1,
        b"10",
    )


@suite.case("small negative")
def test_small_negative(c):
    compare(
        c,
        -10,
        1,
        b"-10",
    )


@suite.case("powers of ten")
def test_powers_of_ten(c):
    compare(
        c,
        100000000,
        1,
        b"100000000",
    )


@suite.case("negative powers of ten")
def test_negative_powers_of_ten(c):
    compare(
        c,
        -100000000,
        1,
        b"-100000000",
    )


@suite.case("no leading zero")
def test_no_leading_zero(c):
    compare(
        c,
        123,
        1,
        b"123",
    )


@suite.case("number containing zeros")
def test_containing_zeros(c):
    compare(
        c,
        102030405,
        1,
        b"102030405",
    )


@suite.case("negative number containing zeros")
def test_negative_containing_zeros(c):
    compare(
        c,
        -102030405,
        1,
        b"-102030405",
    )
