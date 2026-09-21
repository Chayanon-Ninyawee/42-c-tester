from framework import TestSuite

suite = TestSuite("ft_lstmap")


def compare(c, values):
    values_c = ", ".join(str(value) for value in values)

    test = (
        c.include(
            "libft.h",
            "stdlib.h",
        )
        .function("""
        typedef struct s_data
        {
            int id;
            int value;
        } t_data;

        static int __f_calls;

        static void *test_f(void *content)
        {
            t_data *original = content;
            t_data *new_data = malloc(sizeof(t_data));

            if (new_data == NULL)
                return NULL;

            new_data->id = original->id;
            new_data->value = original->value + 1000;

            __f_calls++;
            return new_data;
        }

        static void cleanup(void *content)
        {
            free(content);
        }
        """)
        .code(f"""
        int values[] = {{{values_c}}};

        t_list *lst = NULL;

        for (unsigned int i = 0; i < {len(values)}; i++)
        {{
            t_data *data = malloc(sizeof(t_data));

            data->id = i;
            data->value = values[i];

            t_list *node = ft_lstnew(data);

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

        t_list *original_nodes[{len(values)}];
        t_data *original_data[{len(values)}];

        t_list *current = lst;

        for (unsigned int i = 0; i < {len(values)}; i++)
        {{
            original_nodes[i] = current;
            original_data[i] = current->content;
            current = current->next;
        }}

        t_list *mapped = ft_lstmap(
            lst,
            test_f,
            cleanup
        );

        t_list *mapped_nodes[{len(values)}];
        t_data *mapped_data[{len(values)}];

        current = mapped;

        for (unsigned int i = 0; i < {len(values)}; i++)
        {{
            if (current != NULL)
            {{
                mapped_nodes[i] = current;
                mapped_data[i] = current->content;
                current = current->next;
            }}
            else
            {{
                mapped_nodes[i] = NULL;
                mapped_data[i] = NULL;
            }}
        }}

        int original_links_ok = 1;
        int original_content_ok = 1;
        int mapped_nodes_ok = 1;
        int mapped_content_ok = 1;
        int mapped_links_ok = 1;

        /*
         * Check that the original list was not changed.
         */
        current = lst;

        for (unsigned int i = 0; i < {len(values)}; i++)
        {{
            if (current != original_nodes[i])
                original_links_ok = 0;

            if (current->content != original_data[i])
                original_content_ok = 0;

            if (
                ((t_data *)current->content)->id != (int)i
                || ((t_data *)current->content)->value != values[i]
            )
                original_content_ok = 0;

            current = current->next;
        }}

        if (current != NULL)
            original_links_ok = 0;

        /*
         * Check that the mapped list contains completely new nodes
         * and completely new content.
         */
        current = mapped;

        for (unsigned int i = 0; i < {len(values)}; i++)
        {{
            if (current == NULL)
            {{
                mapped_nodes_ok = 0;
                mapped_content_ok = 0;
                mapped_links_ok = 0;
                break;
            }}

            if (current != mapped_nodes[i])
                mapped_nodes_ok = 0;

            if (current == original_nodes[i])
                mapped_nodes_ok = 0;

            if (current->content != mapped_data[i])
                mapped_content_ok = 0;

            if (current->content == original_data[i])
                mapped_content_ok = 0;

            if (
                ((t_data *)current->content)->id != (int)i
                || ((t_data *)current->content)->value
                    != values[i] + 1000
            )
                mapped_content_ok = 0;

            if (i < {len(values) - 1})
            {{
                if (current->next != mapped_nodes[i + 1])
                    mapped_links_ok = 0;
            }}
            else
            {{
                if (current->next != NULL)
                    mapped_links_ok = 0;
            }}

            current = current->next;
        }}

        TEST_VALUE(
            "f_calls",
            "%d",
            __f_calls
        );

        TEST_VALUE(
            "original_links",
            "%d",
            original_links_ok
        );

        TEST_VALUE(
            "original_content",
            "%d",
            original_content_ok
        );

        TEST_VALUE(
            "mapped_nodes",
            "%d",
            mapped_nodes_ok
        );

        TEST_VALUE(
            "mapped_content",
            "%d",
            mapped_content_ok
        );

        TEST_VALUE(
            "mapped_links",
            "%d",
            mapped_links_ok
        );

        ft_lstclear(&lst, cleanup);
        ft_lstclear(&mapped, cleanup);

        return 0;
        """)
    )

    test.value("f_calls").equals(
        str(len(values)),
        "Function was not called exactly once per node",
    )

    test.value("original_links").equals(
        "1",
        "Original list nodes or links were modified",
    )

    test.value("original_content").equals(
        "1",
        "Original list content was modified",
    )

    test.value("mapped_nodes").equals(
        "1",
        "Mapped list reused nodes from the original list",
    )

    test.value("mapped_content").equals(
        "1",
        "Mapped list contains incorrect or reused content",
    )

    test.value("mapped_links").equals(
        "1",
        "Mapped list links are incorrect",
    )

    # Each input node:
    #   1 malloc for content
    #   1 malloc for node
    #
    # Each mapped node:
    #   1 malloc in test_f
    #   1 malloc for the new node
    test.malloc.count(
        len(values) * 4,
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


@suite.case("empty")
def test_empty(c):
    test = (
        c.include(
            "libft.h",
        )
        .function("""
        static int __f_called;
        static int __del_called;

        static void *test_f(void *content)
        {
            (void)content;
            __f_called++;
            return NULL;
        }

        static void test_del(void *content)
        {
            (void)content;
            __del_called++;
        }
        """)
        .code("""
        t_list *lst = NULL;

        t_list *mapped = ft_lstmap(
            lst,
            test_f,
            test_del
        );

        TEST_VALUE(
            "result_null",
            "%d",
            mapped == NULL
        );

        TEST_VALUE(
            "f_called",
            "%d",
            __f_called
        );

        TEST_VALUE(
            "del_called",
            "%d",
            __del_called
        );

        return 0;
        """)
    )

    test.value("result_null").equals(
        "1",
        "Mapping an empty list did not return NULL",
    )

    test.value("f_called").equals(
        "0",
        "Function was called for an empty list",
    )

    test.value("del_called").equals(
        "0",
        "Delete function was called for an empty list",
    )

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("null pointer")
def test_null_pointer(c):
    test = (
        c.include(
            "libft.h",
        )
        .function("""
        static int __f_called;
        static int __del_called;

        static void *test_f(void *content)
        {
            (void)content;
            __f_called++;
            return NULL;
        }

        static void test_del(void *content)
        {
            (void)content;
            __del_called++;
        }
        """)
        .code("""
        t_list *mapped = ft_lstmap(
            NULL,
            test_f,
            test_del
        );

        TEST_VALUE(
            "result_null",
            "%d",
            mapped == NULL
        );

        TEST_VALUE(
            "f_called",
            "%d",
            __f_called
        );

        TEST_VALUE(
            "del_called",
            "%d",
            __del_called
        );

        return 0;
        """)
    )

    test.value("result_null").equals(
        "1",
        "Mapping a NULL list did not return NULL",
    )

    test.value("f_called").equals(
        "0",
        "Function was called with a NULL list",
    )

    test.value("del_called").equals(
        "0",
        "Delete function was called with a NULL list",
    )

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("malloc failure")
def test_malloc_failure(c):
    test = (
        c.include(
            "libft.h",
            "stdlib.h",
        )
        .function("""
        static int __f_calls;
        static int __del_calls;

        static void *test_f(void *content)
        {
            int *value = content;
            int *new_value = malloc(sizeof(int));

            if (new_value == NULL)
                return NULL;

            *new_value = *value + 100;
            __f_calls++;

            return new_value;
        }

        static void test_del(void *content)
        {
            if (content != NULL)
                __del_calls++;

            free(content);
        }
        """)
        .code("""
        int values[] = {1, 2, 3};

        t_list *lst = NULL;

        for (int i = 0; i < 3; i++)
        {
            int *value = malloc(sizeof(int));

            *value = values[i];

            t_list *node = ft_lstnew(value);

            if (lst == NULL)
                lst = node;
            else
            {
                t_list *current = lst;

                while (current->next)
                    current = current->next;

                current->next = node;
            }
        }

        /*
         * After resetting the malloc strike:
         *
         *   0: f() content
         *   1: new node
         *   2: f() content
         *   3: new node -> FAIL
         */
        malloc_strike_reset();
        malloc_strike_fail_at(3);

        t_list *mapped = ft_lstmap(
            lst,
            test_f,
            test_del
        );

        TEST_VALUE(
            "result_null",
            "%d",
            mapped == NULL
        );

        TEST_VALUE(
            "f_calls",
            "%d",
            __f_calls
        );

        TEST_VALUE(
            "del_calls",
            "%d",
            __del_calls
        );

        TEST_VALUE(
            "original_ok",
            "%d",
            *(int *)lst->content == 1
            && *(int *)lst->next->content == 2
            && *(int *)lst->next->next->content == 3
            && lst->next->next->next == NULL
        );

        /*
         * The original list must still exist.
         */
        ft_lstclear(&lst, test_del);

        return 0;
        """)
    )

    test.value("result_null").equals(
        "1",
        "Allocation failure did not return NULL",
    )

    test.value("f_calls").equals(
        "2",
        "Function was not called for the nodes before failure",
    )

    test.value("del_calls").equals(
        "2",
        "Previously-created and failed content were not deleted",
    )

    test.value("original_ok").equals(
        "1",
        "Original list was modified after allocation failure",
    )

    test.assert_now()
