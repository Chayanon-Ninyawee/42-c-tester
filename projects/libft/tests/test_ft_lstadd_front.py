from framework import TestSuite

suite = TestSuite("ft_lstadd_front")


def compare(c, old_value, new_value):
    test = c.include(
        "libft.h",
    ).code(
        f"""
        int old_content = {old_value};
        int new_content = {new_value};

        t_list *old_node = ft_lstnew(&old_content);
        t_list *new_node = ft_lstnew(&new_content);

        t_list *lst = old_node;

        ft_lstadd_front(
            &lst,
            new_node
        );

        int ft_lst_is_new = (lst == new_node);
        int ft_content_ok = (
            lst != NULL &&
            lst->content == &new_content
        );
        int ft_next_ok = (
            lst != NULL &&
            lst->next == old_node
        );
        int old_content_ok = (
            old_node != NULL &&
            old_node->content == &old_content
        );

        TEST_VALUE(
            "ft_lst_is_new",
            "%d",
            ft_lst_is_new
        );

        TEST_VALUE(
            "ft_content_ok",
            "%d",
            ft_content_ok
        );

        TEST_VALUE(
            "ft_next_ok",
            "%d",
            ft_next_ok
        );

        TEST_VALUE(
            "old_content_ok",
            "%d",
            old_content_ok
        );

        free(new_node);
        free(old_node);

        return 0;
        """
    )

    test.value("ft_lst_is_new").equals(
        "1",
        "Test list pointer",
    )

    test.value("ft_content_ok").equals(
        "1",
        "Test new node content",
    )

    test.value("ft_next_ok").equals(
        "1",
        "Test new node next pointer",
    )

    test.value("old_content_ok").equals(
        "1",
        "Test old node content",
    )

    test.malloc.count(
        2,
        "Test malloc count",
    )

    test.assert_now()


def compare_long_list(c, values):
    values_c = ", ".join(str(value) for value in values)

    test = c.include(
        "libft.h",
    ).code(
        f"""
        int values[] = {{{values_c}}};

        t_list *first = ft_lstnew(&values[0]);
        t_list *second = ft_lstnew(&values[1]);
        t_list *third = ft_lstnew(&values[2]);
        t_list *new_node = ft_lstnew(&values[3]);

        first->next = second;
        second->next = third;

        t_list *lst = first;

        ft_lstadd_front(
            &lst,
            new_node
        );

        int new_is_first = (lst == new_node);
        int new_content_ok = (
            lst != NULL &&
            lst->content == &values[3]
        );
        int first_ok = (
            lst != NULL &&
            lst->next == first &&
            first->content == &values[0]
        );
        int second_ok = (
            first->next == second &&
            second->content == &values[1]
        );
        int third_ok = (
            second->next == third &&
            third->content == &values[2]
        );
        int end_ok = (third->next == NULL);

        TEST_VALUE("new_is_first", "%d", new_is_first);
        TEST_VALUE("new_content_ok", "%d", new_content_ok);
        TEST_VALUE("first_ok", "%d", first_ok);
        TEST_VALUE("second_ok", "%d", second_ok);
        TEST_VALUE("third_ok", "%d", third_ok);
        TEST_VALUE("end_ok", "%d", end_ok);

        free(new_node);
        free(first);
        free(second);
        free(third);

        return 0;
        """
    )

    test.value("new_is_first").equals(
        "1",
        "Test new node is first",
    )

    test.value("new_content_ok").equals(
        "1",
        "Test new node content",
    )

    test.value("first_ok").equals(
        "1",
        "Test original first node",
    )

    test.value("second_ok").equals(
        "1",
        "Test original second node",
    )

    test.value("third_ok").equals(
        "1",
        "Test original third node",
    )

    test.value("end_ok").equals(
        "1",
        "Test list termination",
    )

    test.malloc.count(
        4,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("basic")
def test_basic(c):
    compare(c, 42, 13)


@suite.case("zero")
def test_zero(c):
    compare(c, 0, 13)


@suite.case("negative")
def test_negative(c):
    compare(c, -42, 13)


@suite.case("large value")
def test_large(c):
    compare(c, 2147483647, 13)


@suite.case("long list")
def test_long_list(c):
    compare_long_list(
        c,
        [42, 13, -7, 99],
    )
