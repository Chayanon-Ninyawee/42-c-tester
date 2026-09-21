from framework import TestSuite

suite = TestSuite("ft_calloc")


def compare(c, count, size, expected):
    count_i = int(count, 0)
    size_i = int(size, 0)
    total = count_i * size_i

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

    if expected is None:
        test.value("ft_is_null").equals(
            "1",
            "Test return value",
        )
    else:
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


def test_malloc_failures(c, count, size):
    count_i = int(count, 0)
    size_i = count_i * int(size, 0)

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
                {size_i}
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
        b"\0" * size_i,
        "Test calloc memory",
    )

    test.malloc.count(
        1,
        "Test malloc count",
    )

    test.malloc.size(
        0,
        size_i,
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
