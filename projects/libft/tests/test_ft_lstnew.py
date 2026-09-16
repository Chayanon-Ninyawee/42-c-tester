from framework import Assert, Capture, TestSuite

suite = TestSuite("ft_lstnew")

T_LIST_SIZE = 16


def compare(c, value):
    content = c.variable(
        "int",
        value,
        name="content",
    )

    result = c.ft_lstnew(
        content.pointer(),
    )

    result.capture_return(
        Capture.struct(
            {
                "content": Capture.pointer_raw(),
                "next": Capture.pointer_raw(),
            }
        )
    )

    result.run()

    result.malloc_count_equals(
        1,
        "Test malloc count",
    )
    result.malloc_size_equals(
        0,
        T_LIST_SIZE,
        "Test malloc size",
    )

    result.assert_return(
        Assert.struct(
            {
                "content": Assert.pointer_equals(content),
                "next": Assert.is_null_pointer(),
            }
        )
    ).assert_now()


def test_malloc_failure(c, value):
    content = c.variable(
        "int",
        value,
        name="content",
    )

    # First run must succeed so we know the normal allocation count.
    result = c.ft_lstnew(
        content.pointer(),
    )

    result.capture_return(
        Capture.struct(
            {
                "content": Capture.pointer_raw(),
                "next": Capture.pointer_raw(),
            }
        )
    )

    result.run()

    result.malloc_count_equals(
        1,
        "Test malloc count",
    )
    result.malloc_size_equals(
        0,
        T_LIST_SIZE,
        "Test malloc size",
    )

    result.assert_return(
        Assert.struct(
            {
                "content": Assert.pointer_equals(content),
                "next": Assert.is_null_pointer(),
            }
        ),
        "Initial allocation test",
    )
    result.assert_now()

    malloc_count = result.malloc_count

    for fail_at in range(malloc_count):
        c.malloc.fail_at(fail_at)

        result = c.ft_lstnew(
            content.pointer(),
        )

        result.run()

        result.is_null(
            f"malloc failure at call {fail_at}",
        )

        result.assert_now()

    c.malloc.reset()


@suite.case("basic")
def test_basic(c):
    compare(c, 42)


@suite.case("zero")
def test_zero(c):
    compare(c, 0)


@suite.case("negative")
def test_negative(c):
    compare(c, -42)


@suite.case("large value")
def test_large(c):
    compare(c, 2147483647)


@suite.case("malloc failure")
def test_malloc_failure_case(c):
    test_malloc_failure(c, 42)
