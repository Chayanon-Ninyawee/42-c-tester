from framework import TestSuite

suite = TestSuite("ft_lstdelone")


def compare_buffer(c, data):
    data_c = ", ".join(f"0x{byte:02x}" for byte in data)

    test = (
        c.include(
            "libft.h",
            "stdlib.h",
            "string.h",
        )
        .function(f"""
        static int __del_called;
        static int __content_ok;

        static void test_del(void *content)
        {{
            unsigned char expected[] = {{{data_c}}};

            __del_called++;

            if (memcmp(
                content,
                expected,
                sizeof(expected)
            ) == 0)
                __content_ok = 1;

            free(content);
        }}
        """)
        .code(f"""
        unsigned char data[] = {{{data_c}}};

        unsigned char *content = malloc(sizeof(data));
        memcpy(content, data, sizeof(data));

        t_list *lst = ft_lstnew(content);

        unsigned char next_data[] = {{
            0xde, 0xad, 0xbe, 0xef,
            0x12, 0x34, 0x56, 0x78
        }};

        unsigned char *next_content = malloc(sizeof(next_data));
        memcpy(next_content, next_data, sizeof(next_data));

        t_list *next = ft_lstnew(next_content);
        lst->next = next;

        ft_lstdelone(lst, test_del);

        int next_ok = (
            next->content == next_content &&
            memcmp(
                next->content,
                next_data,
                sizeof(next_data)
            ) == 0 &&
            next->next == NULL
        );

        TEST_VALUE("del_called", "%d", __del_called);
        TEST_VALUE("content_ok", "%d", __content_ok);
        TEST_VALUE("next_ok", "%d", next_ok);

        free(next->content);
        free(next);

        return 0;
        """)
    )

    test.value("del_called").equals(
        "1",
        "Delete function was not called exactly once",
    )

    test.value("content_ok").equals(
        "1",
        "Delete function received incorrect content",
    )

    test.value("next_ok").equals(
        "1",
        "Next node was modified or freed",
    )

    test.malloc.count(
        4,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("binary buffer")
def test_binary_buffer(c):
    compare_buffer(
        c,
        [
            0x00,
            0x01,
            0x7F,
            0x80,
            0xFE,
            0xFF,
            0x42,
            0xAA,
        ],
    )


@suite.case("zero buffer")
def test_zero_buffer(c):
    compare_buffer(
        c,
        [
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
            0x00,
        ],
    )


@suite.case("string buffer")
def test_string_buffer(c):
    compare_buffer(
        c,
        [
            ord("h"),
            ord("e"),
            ord("l"),
            ord("l"),
            ord("o"),
            0x00,
            0x12,
            0xFF,
        ],
    )


@suite.case("large buffer")
def test_large_buffer(c):
    compare_buffer(
        c,
        [i & 0xFF for i in range(256)],
    )


@suite.case("null content")
def test_null_content(c):
    test = (
        c.include(
            "libft.h",
            "stdlib.h",
        )
        .function("""
        static int __del_called;
        static int __content_ok;

        static void test_del(void *content)
        {
            __del_called++;

            if (content == NULL)
                __content_ok = 1;
        }
        """)
        .code("""
        t_list *lst = ft_lstnew(NULL);

        ft_lstdelone(lst, test_del);

        TEST_VALUE(
            "del_called",
            "%d",
            __del_called
        );

        TEST_VALUE(
            "content_ok",
            "%d",
            __content_ok
        );

        return 0;
        """)
    )

    test.value("del_called").equals(
        "1",
        "Delete function was not called exactly once",
    )

    test.value("content_ok").equals(
        "1",
        "Delete function did not receive NULL content",
    )

    test.malloc.count(
        1,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("struct content")
def test_struct_content(c):
    test = (
        c.include(
            "libft.h",
            "stdlib.h",
            "string.h",
        )
        .function("""
        typedef struct s_data
        {
            int id;
            char name[16];
            double value;
        } t_data;

        static int __del_called;
        static int __content_ok;

        static void test_del(void *content)
        {
            t_data *data = content;

            __del_called++;

            if (
                data->id == 42 &&
                strcmp(data->name, "garfield") == 0 &&
                data->value == 3.14159
            )
                __content_ok = 1;

            free(content);
        }
        """)
        .code("""
        t_data *data = malloc(sizeof(t_data));

        data->id = 42;
        strcpy(data->name, "garfield");
        data->value = 3.14159;

        t_list *lst = ft_lstnew(data);

        ft_lstdelone(lst, test_del);

        TEST_VALUE(
            "del_called",
            "%d",
            __del_called
        );

        TEST_VALUE(
            "content_ok",
            "%d",
            __content_ok
        );

        return 0;
        """)
    )

    test.value("del_called").equals(
        "1",
        "Delete function was not called exactly once",
    )

    test.value("content_ok").equals(
        "1",
        "Delete function received incorrect struct",
    )

    test.malloc.count(
        2,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("next node")
def test_next_node(c):
    test = (
        c.include(
            "libft.h",
            "stdlib.h",
            "string.h",
        )
        .function("""
        static int __del_called;

        static void test_del(void *content)
        {
            __del_called++;
            free(content);
        }
        """)
        .code("""
        unsigned char first_data[] = {
            0x01, 0x02, 0x03, 0x04
        };

        unsigned char next_data[] = {
            0xaa, 0xbb, 0xcc, 0xdd
        };

        unsigned char *first = malloc(sizeof(first_data));
        unsigned char *second = malloc(sizeof(next_data));

        memcpy(first, first_data, sizeof(first_data));
        memcpy(second, next_data, sizeof(next_data));

        t_list *lst = ft_lstnew(first);
        t_list *next = ft_lstnew(second);

        lst->next = next;

        ft_lstdelone(lst, test_del);

        int next_content_ok = (
            next->content == second &&
            memcmp(
                next->content,
                next_data,
                sizeof(next_data)
            ) == 0
        );

        int next_link_ok = (
            next->next == NULL
        );

        TEST_VALUE(
            "del_called",
            "%d",
            __del_called
        );

        TEST_VALUE(
            "next_content_ok",
            "%d",
            next_content_ok
        );

        TEST_VALUE(
            "next_link_ok",
            "%d",
            next_link_ok
        );

        free(next->content);
        free(next);

        return 0;
        """)
    )

    test.value("del_called").equals(
        "1",
        "Delete function was not called exactly once",
    )

    test.value("next_content_ok").equals(
        "1",
        "Next node content was modified or freed",
    )

    test.value("next_link_ok").equals(
        "1",
        "Next node link was modified",
    )

    test.malloc.count(
        4,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("null node")
def test_null_node(c):
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
        ft_lstdelone(NULL, test_del);

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
        "Delete function was called for a NULL node",
    )

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()
