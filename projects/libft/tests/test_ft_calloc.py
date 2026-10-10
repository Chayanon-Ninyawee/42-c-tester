from framework import TestSuite

suite = TestSuite("ft_calloc")


def compare(c, count, size, total, should_fail):
    test = c.include("libft.h").code(f"""
        void *ft = ft_calloc(
            {count},
            {size}
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        if (ft != NULL)
            TEST_BUFFER(
                "ft_buffer",
                ft,
                {total if total is not None else 0}
            );

        if (ft)
            free(ft);

        return 0;
    """)

    test.value("ft_is_null").equals(
        "1" if should_fail else "0",
        "Test return value",
    )

    if not should_fail:
        test.buffer("ft_buffer").equals(
            b"\0" * total,
            "Test calloc memory",
        )

        test.malloc.count(
            1,
            "Test malloc count",
        )

        test.malloc.size(
            0,
            total,
            "Test malloc size",
        )

    test.assert_now()


def test_malloc_failures(c, count, size, total):
    test = c.include("libft.h").code(f"""
        void *ft = ft_calloc(
            {count},
            {size}
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        if (ft != NULL)
            TEST_BUFFER(
                "ft_buffer",
                ft,
                {total}
            );

        if (ft)
            free(ft);

        return 0;
    """)

    test.value("ft_is_null").equals(
        "0",
        "Test return value",
    )

    test.buffer("ft_buffer").equals(
        b"\0" * total,
        "Test calloc memory",
    )

    test.malloc.count(
        1,
        "Test malloc count",
    )

    test.malloc.size(
        0,
        total,
        "Test malloc size",
    )

    test.assert_now()

    test = c.include("libft.h", "stdlib.h").code(f"""
        void *ft = ft_calloc(
            {count},
            {size}
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        return 0;
    """)

    test.malloc.fail_at(0)

    test.value("ft_is_null").equals(
        "1",
        "malloc failure at call 0",
    )

    test.assert_now()


@suite.case("allocates zeroed memory")
def test_basic(c):
    count = "5"
    size = "4"
    total = 5 * 4
    should_fail = False

    compare(c, count, size, total, should_fail)


@suite.case("one element")
def test_one_element(c):
    count = "1"
    size = "1"
    total = 1 * 1
    should_fail = False

    compare(c, count, size, total, should_fail)


@suite.case("one element with larger size")
def test_one_element_large_size(c):
    count = "1"
    size = "100"
    total = 1 * 100
    should_fail = False

    compare(c, count, size, total, should_fail)


@suite.case("multiple elements")
def test_multiple_elements(c):
    count = "10"
    size = "8"
    total = 10 * 8
    should_fail = False

    compare(c, count, size, total, should_fail)


@suite.case("zero count")
def test_zero_count(c):
    count = "0"
    size = "10"
    total = 0 * 10
    should_fail = False

    compare(c, count, size, total, should_fail)


@suite.case("zero size")
def test_zero_size(c):
    count = "10"
    size = "0"
    total = 10 * 0
    should_fail = False

    compare(c, count, size, total, should_fail)


@suite.case("both zero")
def test_both_zero(c):
    count = "0"
    size = "0"
    total = 0 * 0
    should_fail = False

    compare(c, count, size, total, should_fail)


@suite.case("large allocation")
def test_large(c):
    count = "1000"
    size = "100"
    total = 1000 * 100
    should_fail = False

    compare(c, count, size, total, should_fail)


@suite.case("overflow")
def test_overflow(c):
    count = "0x8000000000000000"
    size = "2"
    total = None
    should_fail = True

    compare(c, count, size, total, should_fail)


@suite.case("overflow with large size")
def test_overflow_large_size(c):
    count = "0xffffffffffffffff"
    size = "2"
    total = None
    should_fail = True

    compare(c, count, size, total, should_fail)


@suite.case("malloc failure")
def test_malloc_failure(c):
    count = "10"
    size = "4"
    total = 10 * 4

    test_malloc_failures(c, count, size, total)


@suite.case("malloc failure with one element")
def test_malloc_failure_one_element(c):
    count = "1"
    size = "100"
    total = 1 * 100

    test_malloc_failures(c, count, size, total)


@suite.case("malloc failure with large allocation")
def test_malloc_failure_large(c):
    count = "1000"
    size = "100"
    total = 1000 * 100

    test_malloc_failures(c, count, size, total)
