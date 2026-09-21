from framework import TestSuite

suite = TestSuite("ft_lstsize")


def compare(c, values, expected):
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

        unsigned int ft = ft_lstsize(lst);

        int nodes_ok = 1;
        int values_ok = 1;

        current = lst;
        count = 0;

        while (current != NULL && count < {len(values)})
        {{
            if (current != nodes[count])
                nodes_ok = 0;

            if (*(int *)current->content != saved_values[count])
                values_ok = 0;

            current = current->next;
            count++;
        }}

        if (current != NULL || count != {len(values)})
            nodes_ok = 0;

        TEST_VALUE("ft", "%u", ft);
        TEST_VALUE("nodes_ok", "%d", nodes_ok);
        TEST_VALUE("values_ok", "%d", values_ok);

        for (unsigned int i = 0; i < {len(values)}; i++)
            free(nodes[i]);

        return 0;
        """
    )

    test.value("ft").equals(
        str(expected),
        "Test list size",
    )

    test.value("nodes_ok").equals(
        "1",
        "List nodes were modified or reordered",
    )

    test.value("values_ok").equals(
        "1",
        "List content values were modified",
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
        unsigned int ft = ft_lstsize(NULL);

        TEST_VALUE(
            "ft",
            "%u",
            ft
        );

        return 0;
        """
    )

    test.value("ft").equals(
        "0",
        "Test empty list size",
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
        1,
    )


@suite.case("three")
def test_three(c):
    compare(
        c,
        [42, 13, 7],
        3,
    )


@suite.case("long list")
def test_long_list(c):
    compare(
        c,
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
        10,
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
        5,
    )
