from framework import TestSuite

suite = TestSuite("ft_lstiter")


def compare(c, values):
    values_c = ", ".join(str(value) for value in values)

    test = (
        c.include(
            "libft.h",
            "stdlib.h",
        )
        .function(f"""
        static int __calls;

        static void test_f(void *content)
        {{
            int *value = content;

            if (value != NULL)
            {{
                *value += 100;
                __calls++;
            }}
        }}
        """)
        .code(f"""
        int values[] = {{{values_c}}};

        t_list *lst = NULL;

        for (unsigned int i = 0; i < {len(values)}; i++)
        {{
            int *content = malloc(sizeof(int));

            *content = values[i];

            t_list *node = ft_lstnew(content);

            if (lst == NULL)
                lst = node;
            else
            {{
                t_list *current = lst;

                while (current->next)
                    current = current->next;

                current->next = node;
            }}
        }}

        t_list *nodes[{len(values)}];

        t_list *current = lst;
        unsigned int count = 0;

        while (current != NULL)
        {{
            nodes[count] = current;
            current = current->next;
            count++;
        }}

        ft_lstiter(lst, test_f);

        int calls_ok = (__calls == {len(values)});
        int values_ok = 1;
        int links_ok = 1;

        current = lst;

        for (unsigned int i = 0; i < {len(values)}; i++)
        {{
            if (current != nodes[i])
                links_ok = 0;

            if (
                *(int *)current->content
                != values[i] + 100
            )
                values_ok = 0;

            current = current->next;
        }}

        if (current != NULL)
            links_ok = 0;

        TEST_VALUE(
            "calls_ok",
            "%d",
            calls_ok
        );

        TEST_VALUE(
            "values_ok",
            "%d",
            values_ok
        );

        TEST_VALUE(
            "links_ok",
            "%d",
            links_ok
        );

        for (unsigned int i = 0; i < {len(values)}; i++)
            free(nodes[i]->content);

        for (unsigned int i = 0; i < {len(values)}; i++)
            free(nodes[i]);

        return 0;
        """)
    )

    test.value("calls_ok").equals(
        "1",
        "Function was not called exactly once per node",
    )

    test.value("values_ok").equals(
        "1",
        "Function did not receive the correct content",
    )

    test.value("links_ok").equals(
        "1",
        "List nodes or links were modified",
    )

    test.malloc.count(
        len(values) * 2,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("single")
def test_single(c):
    compare(c, [42])


@suite.case("three")
def test_three(c):
    compare(c, [42, 13, 7])


@suite.case("long list")
def test_long_list(c):
    compare(
        c,
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    )


@suite.case("negative values")
def test_negative_values(c):
    compare(
        c,
        [-1, -42, -100, -2147483648],
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


@suite.case("null content")
def test_null_content(c):
    test = (
        c.include(
            "libft.h",
            "stdlib.h",
        )
        .function("""
        static int __called;
        static int __received_null;

        static void test_f(void *content)
        {
            __called++;

            if (content == NULL)
                __received_null = 1;
        }
        """)
        .code("""
        t_list *lst = ft_lstnew(NULL);

        ft_lstiter(lst, test_f);

        TEST_VALUE(
            "called",
            "%d",
            __called
        );

        TEST_VALUE(
            "received_null",
            "%d",
            __received_null
        );

        free(lst);

        return 0;
        """)
    )

    test.value("called").equals(
        "1",
        "Function was not called for NULL content",
    )

    test.value("received_null").equals(
        "1",
        "Function did not receive NULL content",
    )

    test.malloc.count(
        1,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("empty")
def test_empty(c):
    test = (
        c.include(
            "libft.h",
        )
        .function("""
        static int __called;

        static void test_f(void *content)
        {
            (void)content;
            __called++;
        }
        """)
        .code("""
        ft_lstiter(NULL, test_f);

        TEST_VALUE(
            "called",
            "%d",
            __called
        );

        return 0;
        """)
    )

    test.value("called").equals(
        "0",
        "Function was called for an empty list",
    )

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()
