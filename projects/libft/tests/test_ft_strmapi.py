from framework import TestSuite, c_bytes

suite = TestSuite("ft_strmapi")


def compare(c, original, expected, callback_name, callback_body):
    original_c = c_bytes(original)

    test = (
        c.include(
            "libft.h",
            "stdlib.h",
        )
        .function(f"""
        static char {callback_name}(unsigned int i, char c)
        {{
            {callback_body}
        }}
        """)
        .code(f"""
        unsigned char ft_s[] = {{{original_c}}};

        char *ft = ft_strmapi(
            (char *)ft_s,
            {callback_name}
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s",
            ft_s,
            sizeof(ft_s)
        );

        if (ft != NULL) {{
            TEST_BUFFER(
                "ft_result",
                ft,
                {len(expected)}
            );

            free(ft);
        }}

        return 0;
        """)
    )

    test.value("ft_is_null").equals(
        "0",
        "Test return value",
    )

    test.malloc.count(
        1,
        "Test malloc count",
    )

    test.malloc.size(
        0,
        len(expected),
        "Test malloc size",
    )

    test.buffer("ft_s").equals(
        original,
        "Source string was modified",
    )

    test.buffer("ft_result").equals(
        expected,
        "Returned buffer mismatch",
    )

    test.assert_now()


def test_malloc_failures(
    c,
    original,
    expected,
    callback_name,
    callback_body,
):
    original_c = c_bytes(original)

    test = (
        c.include(
            "libft.h",
            "stdlib.h",
        )
        .function(f"""
        static char {callback_name}(unsigned int i, char c)
        {{
            {callback_body}
        }}
        """)
        .code(f"""
        unsigned char ft_s[] = {{{original_c}}};

        char *ft = ft_strmapi(
            (char *)ft_s,
            {callback_name}
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s",
            ft_s,
            sizeof(ft_s)
        );

        if (ft != NULL) {{
            TEST_BUFFER(
                "ft_result",
                ft,
                {len(expected)}
            );

            free(ft);
        }}

        return 0;
        """)
    )

    test.value("ft_is_null").equals(
        "0",
        "Test return value",
    )

    test.malloc.count(
        1,
        "Test malloc count",
    )

    test.malloc.size(
        0,
        len(expected),
        "Test malloc size",
    )

    test.buffer("ft_s").equals(
        original,
        "Source string was modified",
    )

    test.buffer("ft_result").equals(
        expected,
        "Returned buffer mismatch",
    )

    test.assert_now()

    test = (
        c.include(
            "libft.h",
        )
        .function(f"""
        static char {callback_name}(unsigned int i, char c)
        {{
            {callback_body}
        }}
        """)
        .code(f"""
        unsigned char ft_s[] = {{{original_c}}};

        char *ft = ft_strmapi(
            (char *)ft_s,
            {callback_name}
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s",
            ft_s,
            sizeof(ft_s)
        );

        return 0;
        """)
    )

    test.malloc.fail_at(0)

    test.value("ft_is_null").equals(
        "1",
        "malloc failure at call 0",
    )

    test.buffer("ft_s").equals(
        original,
        "Source string was modified",
    )

    test.assert_now()


@suite.case("identity")
def test_identity(c):
    compare(
        c,
        b"hello world\0",
        b"hello world\0",
        "identity",
        """
        (void)i;
        return c;
        """,
    )


@suite.case("empty string")
def test_empty(c):
    compare(
        c,
        b"\0",
        b"\0",
        "identity",
        """
        (void)i;
        return c;
        """,
    )


@suite.case("index is passed correctly")
def test_index(c):
    compare(
        c,
        b"abcdef\0",
        b"012345\0",
        "char_index",
        """
        (void)c;
        return '0' + i;
        """,
    )


@suite.case("character is passed correctly")
def test_character(c):
    compare(
        c,
        b"ABCxyz123\0",
        b"ABCxyz123\0",
        "character",
        """
        (void)i;
        return c;
        """,
    )


@suite.case("index and character")
def test_index_and_character(c):
    compare(
        c,
        b"abcde\0",
        b"acegi\0",
        "increment",
        """
        return c + i;
        """,
    )


@suite.case("decrement")
def test_decrement(c):
    compare(
        c,
        b"edcba\0",
        b"eca_]\0",
        "decrement",
        """
        return c - i;
        """,
    )


@suite.case("same callback result")
def test_same_result(c):
    compare(
        c,
        b"hello world\0",
        b"***********\0",
        "star",
        """
        (void)i;
        (void)c;
        return '*';
        """,
    )


@suite.case("index based transformation")
def test_index_transformation(c):
    compare(
        c,
        b"abcdefhh\0",
        b"badcfeig\0",
        "index_transform",
        """
        if (i % 2 == 0)
            return c + 1;

        return c - 1;
        """,
    )


@suite.case("character based transformation")
def test_character_transformation(c):
    compare(
        c,
        b"Hello WORLD 123!\0",
        b"hELLO world 123!\0",
        "character_transform",
        """
        (void)i;

        if (c >= 'a' && c <= 'z')
            return c - 'a' + 'A';

        if (c >= 'A' && c <= 'Z')
            return c - 'A' + 'a';

        return c;
        """,
    )


@suite.case("index and character dependent transformation")
def test_index_character_transformation(c):
    compare(
        c,
        b"abcdef\0",
        b"AEIMQU\0",
        "complex_transform",
        """
        if (c >= 'a' && c <= 'z')
            c -= 'a';

        return (c + i * 3) % 26 + 'A';
        """,
    )


@suite.case("conditional index transformation")
def test_conditional_index(c):
    compare(
        c,
        b"abcdef\0",
        b"klmfch\0",
        "conditional_index",
        """
        if (i < 3)
            return c + 10;

        if (i % 2 == 0)
            return c - 2;

        return c + 2;
        """,
    )


@suite.case("multiple operations")
def test_multiple_operations(c):
    compare(
        c,
        b"abcdef\0",
        b"\xbf\xc3\xc7\xcb\xcf\xd3\0",
        "multiple_operations",
        """
        int value;

        value = c;
        value += i;
        value *= 2;
        value -= 3;

        return value;
        """,
    )


@suite.case("character classification")
def test_character_classification(c):
    compare(
        c,
        b"aZ5 !b2C\0",
        b"LUDS?LDU\0",
        "classify",
        """
        (void)i;

        if (c >= '0' && c <= '9')
            return 'D';

        if (c >= 'a' && c <= 'z')
            return 'L';

        if (c >= 'A' && c <= 'Z')
            return 'U';

        if (c == ' ')
            return 'S';

        return '?';
        """,
    )


@suite.case("special characters")
def test_special(c):
    compare(
        c,
        b"!@#$%^&*()[]{};:'\",.<>/?\0",
        b"!@#$%^&*()[]{};:'\",.<>/?\0",
        "special",
        """
        (void)i;
        return c;
        """,
    )


@suite.case("spaces and whitespace")
def test_whitespace(c):
    compare(
        c,
        b" \t\n\rhello world\t\n\0",
        b" \t\n\rhello world\t\n\0",
        "whitespace",
        """
        (void)i;
        return c;
        """,
    )


@suite.case("binary data")
def test_binary(c):
    compare(
        c,
        b"\x01\x02\x03hello\x04\x05\x06\0",
        b"\x01\x02\x03hello\x04\x05\x06\0",
        "binary",
        """
        (void)i;
        return c;
        """,
    )


@suite.case("high bytes")
def test_high_bytes(c):
    compare(
        c,
        b"\x80\x81\xfe\xffhello\0",
        b"\x80\x81\xfe\xffhello\0",
        "high_bytes",
        """
        (void)i;
        return c;
        """,
    )


@suite.case("large string")
def test_large(c):
    original = b"0123456789" * 1000 + b"\0"

    compare(
        c,
        original,
        original,
        "large",
        """
        (void)i;
        return c;
        """,
    )


@suite.case("malloc failure")
def test_malloc_failure(c):
    test_malloc_failures(
        c,
        b"hello world\0",
        b"hello world\0",
        "malloc_failure",
        """
        (void)i;
        return c;
        """,
    )


@suite.case("malloc failure empty string")
def test_malloc_failure_empty(c):
    test_malloc_failures(
        c,
        b"\0",
        b"\0",
        "malloc_failure_empty",
        """
        (void)i;
        return c;
        """,
    )


@suite.case("malloc failure binary data")
def test_malloc_failure_binary(c):
    test_malloc_failures(
        c,
        b"\x01\x02hello\xfe\xff\0",
        b"\x01\x02hello\xfe\xff\0",
        "malloc_failure_binary",
        """
        (void)i;
        return c;
        """,
    )
