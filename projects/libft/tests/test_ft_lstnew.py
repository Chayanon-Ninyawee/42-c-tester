from framework import TestSuite

suite = TestSuite("ft_lstnew")

T_LIST_SIZE = 16


def compare(c, value):
    test = c.include(
        "libft.h",
    ).code(
        f"""
        int content = {value};

        t_list *ft = ft_lstnew(&content);

        int ft_is_null = (ft == NULL);
        int ft_content_ok = (
            ft != NULL &&
            ft->content == &content
        );
        int ft_next_is_null = (
            ft != NULL &&
            ft->next == NULL
        );

        TEST_VALUE(
            "ft_is_null",
            "%d",
            ft_is_null
        );

        TEST_VALUE(
            "ft_content_ok",
            "%d",
            ft_content_ok
        );

        TEST_VALUE(
            "ft_next_is_null",
            "%d",
            ft_next_is_null
        );

        if (ft != NULL)
            free(ft);

        return 0;
        """
    )

    test.value("ft_is_null").equals(
        "0",
        "Test return value",
    )

    test.value("ft_content_ok").equals(
        "1",
        "Test content pointer",
    )

    test.value("ft_next_is_null").equals(
        "1",
        "Test next pointer",
    )

    test.malloc.count(
        1,
        "Test malloc count",
    )

    test.malloc.size(
        0,
        T_LIST_SIZE,
        "Test malloc size",
    )

    test.assert_now()


def test_malloc_failure(c, value):
    test = c.include(
        "libft.h",
    ).code(
        f"""
        int content = {value};

        t_list *ft = ft_lstnew(&content);

        int ft_is_null = (ft == NULL);

        TEST_VALUE(
            "ft_is_null",
            "%d",
            ft_is_null
        );

        return 0;
        """
    )

    test.malloc.fail_at(0)

    test.value("ft_is_null").equals(
        "1",
        "malloc failure at call 0",
    )

    test.assert_now()


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


@suite.case("malloc failure 1")
def test_malloc_failure_case_1(c):
    test_malloc_failure(c, 42)


@suite.case("malloc failure 2")
def test_malloc_failure_case_2(c):
    test_malloc_failure(c, 67)
