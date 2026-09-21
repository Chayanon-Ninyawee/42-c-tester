from framework import TestSuite

suite = TestSuite("ft_lstlast")


def compare(c, values):
    values_c = ", ".join(str(value) for value in values)

    test = c.include(
        "libft.h",
    ).code(
        f"""
        int values[] = {{{values_c}}};
        t_list *lst = NULL;

        for (unsigned int i = 0; i < {len(values)}; i++)
        {{
            t_list *node = ft_lstnew(&values[i]);
            ft_lstadd_front(&lst, node);
        }}

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

        t_list *ft = ft_lstlast(lst);

        int result_ok = (ft == nodes[{len(values) - 1}]);
        int values_ok = 1;
        int links_ok = 1;

        current = lst;
        count = 0;

        while (current != NULL && count < {len(values)})
        {{
            if (*(int *)current->content != saved_values[count])
                values_ok = 0;

            if (current != nodes[count])
                links_ok = 0;

            current = current->next;
            count++;
        }}

        if (current != NULL || count != {len(values)})
            links_ok = 0;

        int last_ok = (
            ft != NULL &&
            ft->next == NULL
        );

        TEST_VALUE("result_ok", "%d", result_ok);
        TEST_VALUE("values_ok", "%d", values_ok);
        TEST_VALUE("links_ok", "%d", links_ok);
        TEST_VALUE("last_ok", "%d", last_ok);

        for (unsigned int i = 0; i < {len(values)}; i++)
            free(nodes[i]);

        return 0;
        """
    )

    test.value("result_ok").equals(
        "1",
        "Test returned last node",
    )

    test.value("values_ok").equals(
        "1",
        "List content values were modified",
    )

    test.value("links_ok").equals(
        "1",
        "List nodes were modified or reordered",
    )

    test.value("last_ok").equals(
        "1",
        "Returned node is not the last node",
    )

    test.malloc.count(
        len(values),
        "Test malloc count",
    )

    test.assert_now()


@suite.case("empty")
def test_empty(c):
    test = c.include(
        "libft.h",
    ).code(
        """
        t_list *ft = ft_lstlast(NULL);

        TEST_VALUE(
            "is_null",
            "%d",
            ft == NULL
        );

        return 0;
        """
    )

    test.value("is_null").equals(
        "1",
        "Test empty list",
    )

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("single")
def test_single(c):
    compare(
        c,
        [42],
    )


@suite.case("three")
def test_three(c):
    compare(
        c,
        [42, 13, 7],
    )


@suite.case("long list")
def test_long_list(c):
    compare(
        c,
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
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
    )
