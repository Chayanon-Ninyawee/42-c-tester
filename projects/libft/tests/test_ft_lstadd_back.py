from framework import TestSuite

suite = TestSuite("ft_lstadd_back")


def compare(c, values, new_value):
    values_c = ", ".join(str(value) for value in values)

    test = c.include(
        "libft.h",
    ).code(
        f"""
        int values[] = {{{values_c}}};
        int new_value = {new_value};

        t_list *lst = NULL;

        for (unsigned int i = 0; i < {len(values)}; i++)
        {{
            t_list *node = ft_lstnew(&values[i]);
            ft_lstadd_front(&lst, node);
        }}

        t_list *new_node = ft_lstnew(&new_value);

        t_list *nodes[{len(values)}];
        int saved_values[{len(values)}];

        t_list *current = lst;
        unsigned int count = 0;

        while (current != NULL && count < {len(values)})
        {{
            nodes[count] = current;
            saved_values[count] = *(int *)current->content;

            current = current->next;
            count++;
        }}

        ft_lstadd_back(&lst, new_node);

        int head_ok = (lst == nodes[0]);
        int new_is_last = (
            new_node != NULL &&
            new_node->next == NULL
        );

        int values_ok = 1;
        int links_ok = 1;

        current = lst;
        count = 0;

        while (current != NULL && count < {len(values)})
        {{
            if (current != nodes[count])
                links_ok = 0;

            if (*(int *)current->content != saved_values[count])
                values_ok = 0;

            current = current->next;
            count++;
        }}

        if (count != {len(values)})
            links_ok = 0;

        int last_link_ok = (
            current == new_node
        );

        int new_content_ok = (
            new_node != NULL &&
            *(int *)new_node->content == new_value
        );

        TEST_VALUE("head_ok", "%d", head_ok);
        TEST_VALUE("new_is_last", "%d", new_is_last);
        TEST_VALUE("values_ok", "%d", values_ok);
        TEST_VALUE("links_ok", "%d", links_ok);
        TEST_VALUE("last_link_ok", "%d", last_link_ok);
        TEST_VALUE("new_content_ok", "%d", new_content_ok);

        for (unsigned int i = 0; i < {len(values)}; i++)
            free(nodes[i]);

        free(new_node);

        return 0;
        """
    )

    test.value("head_ok").equals(
        "1",
        "Existing list head was modified",
    )

    test.value("new_is_last").equals(
        "1",
        "New node is not the last node",
    )

    test.value("values_ok").equals(
        "1",
        "Existing list content was modified",
    )

    test.value("links_ok").equals(
        "1",
        "Existing list nodes were modified or reordered",
    )

    test.value("last_link_ok").equals(
        "1",
        "New node was not linked to the existing list",
    )

    test.value("new_content_ok").equals(
        "1",
        "New node content was modified",
    )

    test.malloc.count(
        len(values) + 1,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("empty")
def test_empty(c):
    test = c.include(
        "libft.h",
    ).code(
        """
        int value = 42;

        t_list *lst = NULL;
        t_list *new_node = ft_lstnew(&value);

        ft_lstadd_back(
            &lst,
            new_node
        );

        int head_ok = (lst == new_node);
        int next_ok = (
            lst != NULL &&
            lst->next == NULL
        );
        int content_ok = (
            lst != NULL &&
            *(int *)lst->content == value
        );

        TEST_VALUE("head_ok", "%d", head_ok);
        TEST_VALUE("next_ok", "%d", next_ok);
        TEST_VALUE("content_ok", "%d", content_ok);

        free(new_node);

        return 0;
        """
    )

    test.value("head_ok").equals(
        "1",
        "New node was not added as the head",
    )

    test.value("next_ok").equals(
        "1",
        "New node next pointer was modified",
    )

    test.value("content_ok").equals(
        "1",
        "New node content was modified",
    )

    test.malloc.count(
        1,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("single")
def test_single(c):
    compare(
        c,
        [42],
        13,
    )


@suite.case("three")
def test_three(c):
    compare(
        c,
        [42, 13, 7],
        99,
    )


@suite.case("long list")
def test_long_list(c):
    compare(
        c,
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        99,
    )


@suite.case("large values")
def test_large_values(c):
    compare(
        c,
        [
            2147483647,
            -2147483648,
            0,
            123456789,
            -123456789,
        ],
        42,
    )


@suite.case("null pointer")
def test_null_pointer(c):
    test = c.include(
        "libft.h",
    ).code(
        """
        int value = 42;

        t_list *new_node = ft_lstnew(&value);

        ft_lstadd_back(NULL, new_node);

        TEST_VALUE(
            "still_valid",
            "%d",
            *(int *)new_node->content == 42
        );

        TEST_VALUE(
            "next",
            "%d",
            new_node->next == NULL
        );

        free(new_node);

        return 0;
        """
    )

    test.value("still_valid").equals(
        "1",
        "New node was modified",
    )

    test.value("next").equals(
        "1",
        "New node next pointer was modified",
    )

    test.malloc.count(
        1,
        "Test malloc count",
    )

    test.assert_now()
