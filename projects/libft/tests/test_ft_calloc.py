from framework import TestSuite

suite = TestSuite("ft_calloc")


def compare(c, count, size, expected):
    ft = c.ft_calloc(
        count,
        size,
    )

    libc = c.calloc(
        count,
        size,
    )

    if expected is None:
        libc.is_null(
            "Test return value from calloc() from libc",
        )
        ft.is_null(
            "Test return value",
        )
    else:
        libc.is_not_null(
            "Test return value from calloc() from libc",
        )
        ft.is_not_null(
            "Test return value",
        )
        ft.malloc_count_equals(
            1,
            "Test malloc count",
        )
        ft.malloc_size_equals(
            0,
            int(count, 0) * int(size, 0),
            "Test malloc size",
        )

    # NOTE: libc calloc doesn't really use malloc so no need to do this
    # libc.malloc_count_equals(
    #     1,
    #     "Test malloc count from calloc() from libc",
    # )

    libc.assert_reference()
    ft.assert_now()


def test_malloc_failures(c, count, size):
    c.malloc.reset()

    result = c.ft_calloc(
        count,
        size,
    )
    result.assert_now()

    malloc_count = result.malloc_count

    for fail_at in range(malloc_count):
        c.malloc.fail_at(fail_at)

        result = c.ft_calloc(
            count,
            size,
        )

        # If the return pointer from the function is not null then smt is wrong
        result.is_null(
            f"malloc failure at call {fail_at}",
        ).assert_now()

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


@suite.case("larger allocation")
def test_larger(c):
    count = "0x000000000fffffff"
    size = "4"
    expected = 0

    compare(c, count, size, expected)


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
