from framework import TestSuite

suite = TestSuite("ft_lstclear")


def compare(c, count):
    test = (
        c.include(
            "libft.h",
            "stdlib.h",
            "string.h",
        )
        .function(f"""
        typedef struct s_data
        {{
            int id;
            unsigned char data[8];
        }} t_data;

        static int __seen[{count}];
        static int __content_ok;

        static void test_del(void *content)
        {{
            t_data *data = content;

            if (data->id >= 0 && data->id < {count})
            {{
                unsigned char expected[8];

                for (unsigned int i = 0; i < 8; i++)
                    expected[i] = (unsigned char)(
                        data->id * 17 + i
                    );

                if (
                    memcmp(
                        data->data,
                        expected,
                        sizeof(expected)
                    ) == 0
                )
                    __content_ok++;

                __seen[data->id]++;
            }}

            free(content);
        }}
        """)
        .code(f"""
        t_list *lst = NULL;

        for (int i = 0; i < {count}; i++)
        {{
            t_data *data = malloc(sizeof(t_data));

            data->id = i;

            for (unsigned int j = 0; j < 8; j++)
                data->data[j] = (unsigned char)(
                    i * 17 + j
                );

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

        ft_lstclear(&lst, test_del);

        int all_seen_once = 1;

        for (int i = 0; i < {count}; i++)
        {{
            if (__seen[i] != 1)
                all_seen_once = 0;
        }}

        TEST_VALUE(
            "content_ok",
            "%d",
            __content_ok == {count}
        );

        TEST_VALUE(
            "all_seen_once",
            "%d",
            all_seen_once
        );

        TEST_VALUE(
            "list_null",
            "%d",
            lst == NULL
        );

        return 0;
        """)
    )

    test.value("content_ok").equals(
        "1",
        "Delete function received incorrect content",
    )

    test.value("all_seen_once").equals(
        "1",
        "Delete function was not called exactly once per node",
    )

    test.value("list_null").equals(
        "1",
        "List pointer was not set to NULL",
    )

    test.malloc.count(
        count * 2,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("single")
def test_single(c):
    compare(c, 1)


@suite.case("three")
def test_three(c):
    compare(c, 3)


@suite.case("long list")
def test_long_list(c):
    compare(c, 10)


@suite.case("large list")
def test_large_list(c):
    compare(c, 100)


@suite.case("empty")
def test_empty(c):
    test = (
        c.include(
            "libft.h",
        )
        .function("""
        static int __del_called;

        static void test_del(void *content)
        {
            (void)content;
            __del_called++;
        }
        """)
        .code("""
        t_list *lst = NULL;

        ft_lstclear(&lst, test_del);

        TEST_VALUE(
            "del_called",
            "%d",
            __del_called
        );

        TEST_VALUE(
            "list_null",
            "%d",
            lst == NULL
        );

        return 0;
        """)
    )

    test.value("del_called").equals(
        "0",
        "Delete function was called for an empty list",
    )

    test.value("list_null").equals(
        "1",
        "Empty list pointer was not NULL",
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
        static int __del_called;

        static void test_del(void *content)
        {
            (void)content;
            __del_called++;
        }
        """)
        .code("""
        ft_lstclear(NULL, test_del);

        TEST_VALUE(
            "del_called",
            "%d",
            __del_called
        );

        return 0;
        """)
    )

    test.value("del_called").equals(
        "0",
        "Delete function was called with a NULL list pointer",
    )

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()
