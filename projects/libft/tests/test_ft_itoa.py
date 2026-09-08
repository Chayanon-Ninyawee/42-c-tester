from framework import Assert, Capture, TestSuite

suite = TestSuite("ft_itoa")


def compare(c, n, expected):
    ft = c.ft_itoa(
        str(n),
    )

    ft.capture_return(
        Capture.buffer(len(expected)),
    )
    ft.run()

    ft.is_not_null(
        "Test return value",
    )
    ft.malloc_count_equals(
        1,
        "Test malloc count",
    )
    ft.malloc_size_equals(
        0,
        len(expected),
        "Test malloc size",
    )
    ft.assert_return(
        Assert.buffer_equals(expected),
        "Returned buffer mismatch",
    )
    ft.assert_now()


def test_malloc_failures(c, n, expected):
    c.malloc.reset()

    # Successful run to determine allocation count.
    ft = c.ft_itoa(
        str(n),
    )

    ft.capture_return(
        Capture.buffer(len(expected)),
    )
    ft.run()

    ft.is_not_null(
        "Test return value",
    )
    ft.malloc_count_equals(
        1,
        "Test malloc count",
    )
    ft.malloc_size_equals(
        0,
        len(expected),
        "Test malloc size",
    )
    ft.assert_return(
        Assert.buffer_equals(expected),
        "Returned buffer mismatch",
    )
    ft.assert_now()

    malloc_count = ft.malloc_count

    for fail_at in range(malloc_count):
        c.malloc.fail_at(fail_at)

        ft = c.ft_itoa(
            str(n),
        )

        # Expect pointer to be null so no need to free, and no need to read what inside
        ft.run()

        ft.is_null(
            f"malloc failure at call {fail_at}",
        )
        ft.assert_now()

    c.malloc.reset()


@suite.case("zero")
def test_zero(c):
    compare(
        c,
        0,
        b"0\0",
    )


@suite.case("positive single digit")
def test_positive_single_digit(c):
    compare(
        c,
        5,
        b"5\0",
    )


@suite.case("negative single digit")
def test_negative_single_digit(c):
    compare(
        c,
        -5,
        b"-5\0",
    )


@suite.case("positive number")
def test_positive(c):
    compare(
        c,
        12345,
        b"12345\0",
    )


@suite.case("negative number")
def test_negative(c):
    compare(
        c,
        -12345,
        b"-12345\0",
    )


@suite.case("positive number with zeros")
def test_positive_with_zeros(c):
    compare(
        c,
        10001,
        b"10001\0",
    )


@suite.case("negative number with zeros")
def test_negative_with_zeros(c):
    compare(
        c,
        -10001,
        b"-10001\0",
    )


@suite.case("large positive number")
def test_large_positive(c):
    compare(
        c,
        2147483647,
        b"2147483647\0",
    )


@suite.case("large negative number")
def test_large_negative(c):
    compare(
        c,
        -2147483647,
        b"-2147483647\0",
    )


@suite.case("INT_MIN")
def test_int_min(c):
    compare(
        c,
        -2147483648,
        b"-2147483648\0",
    )


@suite.case("INT_MAX")
def test_int_max(c):
    compare(
        c,
        2147483647,
        b"2147483647\0",
    )


@suite.case("power of ten")
def test_power_of_ten(c):
    compare(
        c,
        1000000,
        b"1000000\0",
    )


@suite.case("negative power of ten")
def test_negative_power_of_ten(c):
    compare(
        c,
        -1000000,
        b"-1000000\0",
    )


@suite.case("alternating digits")
def test_alternating_digits(c):
    compare(
        c,
        101010101,
        b"101010101\0",
    )


@suite.case("malloc failure zero")
def test_malloc_failure_zero(c):
    test_malloc_failures(
        c,
        0,
        b"0\0",
    )


@suite.case("malloc failure positive")
def test_malloc_failure_positive(c):
    test_malloc_failures(
        c,
        123456789,
        b"123456789\0",
    )


@suite.case("malloc failure negative")
def test_malloc_failure_negative(c):
    test_malloc_failures(
        c,
        -123456789,
        b"-123456789\0",
    )


@suite.case("malloc failure INT_MIN")
def test_malloc_failure_int_min(c):
    test_malloc_failures(
        c,
        -2147483648,
        b"-2147483648\0",
    )
