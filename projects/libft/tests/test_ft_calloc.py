from framework import Assert, Capture, TestSuite

suite = TestSuite("ft_calloc")


def compare(c, count, size, expected):
    count_i = int(count, 0)
    size_i = int(size, 0)

    ft = c.ft_calloc(
        count,
        size,
    )

    if expected is None:
        ft.capture_return(Capture.pointer_raw())
    else:
        ft.capture_return(
            Capture.buffer(count_i * size_i),
        )

    ft.run()

    if expected is None:
        ft.is_null(
            "Test return value",
        )
    else:
        ft.is_not_null(
            "Test return value",
        )

        ft.malloc_count_equals(
            1,
            "Test malloc count",
        )
        ft.malloc_size_equals(
            0,
            count_i * size_i,
            "Test malloc size",
        )

        ft.assert_return(
            Assert.buffer_equals(
                b"\0" * (count_i * size_i),
            ),
            "Test calloc memory",
        )

    ft.assert_now()


def test_malloc_failures(c, count, size):
    count_i = int(count, 0)
    size_i = int(size, 0)

    c.malloc.reset()

    ft = c.ft_calloc(
        count,
        size,
    )

    ft.capture_return(
        Capture.buffer(count_i * size_i),
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
        count_i * size_i,
        "Test malloc size",
    )
    ft.assert_return(
        Assert.buffer_equals(
            b"\0" * (count_i * size_i),
        ),
        "Test calloc memory",
    )

    ft.assert_now()

    malloc_count = ft.malloc_count

    for fail_at in range(malloc_count):
        c.malloc.fail_at(fail_at)

        ft = c.ft_calloc(
            count,
            size,
        )

        # Expect pointer to be null so no need to free, and no need to read what inside
        ft.run()

        ft.is_null(
            f"malloc failure at call {fail_at}",
        )

        ft.assert_now()

    c.malloc.reset()


@suite.case("allocates zeroed memory")
def test_basic(c):
    count = "5"
    size = "4"
    expected = 20

    compare(c, count, size, expected)


@suite.case("one element")
def test_one_element(c):
    count = "1"
    size = "1"
    expected = 1

    compare(c, count, size, expected)


@suite.case("one element with larger size")
def test_one_element_large_size(c):
    count = "1"
    size = "100"
    expected = 100

    compare(c, count, size, expected)


@suite.case("multiple elements")
def test_multiple_elements(c):
    count = "10"
    size = "8"
    expected = 80

    compare(c, count, size, expected)


@suite.case("zero count")
def test_zero_count(c):
    count = "0"
    size = "10"
    expected = 0

    compare(c, count, size, expected)


@suite.case("zero size")
def test_zero_size(c):
    count = "10"
    size = "0"
    expected = 0

    compare(c, count, size, expected)


@suite.case("both zero")
def test_both_zero(c):
    count = "0"
    size = "0"
    expected = 0

    compare(c, count, size, expected)


@suite.case("large allocation")
def test_large(c):
    count = "1000"
    size = "100"
    expected = 100000

    compare(c, count, size, expected)


# @suite.case("larger allocation")
# def test_larger(c):
#     count = "0x000000000fffffff"
#     size = "4"
#     expected = 0
#
#     compare(c, count, size, expected)


@suite.case("overflow")
def test_overflow(c):
    count = "0x8000000000000000"
    size = "2"
    expected = None

    compare(c, count, size, expected)


@suite.case("overflow with large size")
def test_overflow_large_size(c):
    count = "0xffffffffffffffff"
    size = "2"
    expected = None

    compare(c, count, size, expected)


@suite.case("malloc failure")
def test_malloc_failure(c):
    test_malloc_failures(
        c,
        "10",
        "4",
    )


@suite.case("malloc failure with one element")
def test_malloc_failure_one_element(c):
    test_malloc_failures(
        c,
        "1",
        "100",
    )


@suite.case("malloc failure with large allocation")
def test_malloc_failure_large(c):
    test_malloc_failures(
        c,
        "1000",
        "100",
    )
