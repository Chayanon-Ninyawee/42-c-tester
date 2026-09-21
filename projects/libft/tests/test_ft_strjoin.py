from framework import TestSuite, c_bytes

suite = TestSuite("ft_strjoin")


def compare(c, s1, s2, expected):
    s1_c = c_bytes(s1)
    s2_c = c_bytes(s2)

    test = c.include("libft.h", "stdlib.h").code(f"""
        unsigned char ft_s1[] = {{{s1_c}}};
        unsigned char ft_s2[] = {{{s2_c}}};

        char *ft = ft_strjoin(
            (char *)ft_s1,
            (char *)ft_s2
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s1",
            ft_s1,
            sizeof(ft_s1)
        );

        TEST_BUFFER(
            "ft_s2",
            ft_s2,
            sizeof(ft_s2)
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

    test.buffer("ft_s1").equals(
        s1,
        "First source buffer was modified",
    )

    test.buffer("ft_s2").equals(
        s2,
        "Second source buffer was modified",
    )

    test.buffer("ft_result").equals(
        expected,
        "Returned buffer mismatch",
    )

    test.assert_now()


def test_malloc_failures(c, s1, s2, expected):
    s1_c = c_bytes(s1)
    s2_c = c_bytes(s2)

    test = c.include("libft.h", "stdlib.h").code(f"""
        unsigned char ft_s1[] = {{{s1_c}}};
        unsigned char ft_s2[] = {{{s2_c}}};

        char *ft = ft_strjoin(
            (char *)ft_s1,
            (char *)ft_s2
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s1",
            ft_s1,
            sizeof(ft_s1)
        );

        TEST_BUFFER(
            "ft_s2",
            ft_s2,
            sizeof(ft_s2)
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

    test.buffer("ft_s1").equals(
        s1,
        "First source buffer was modified",
    )

    test.buffer("ft_s2").equals(
        s2,
        "Second source buffer was modified",
    )

    test.buffer("ft_result").equals(
        expected,
        "Returned buffer mismatch",
    )

    test.assert_now()

    test = c.include("libft.h").code(f"""
        unsigned char ft_s1[] = {{{s1_c}}};
        unsigned char ft_s2[] = {{{s2_c}}};

        char *ft = ft_strjoin(
            (char *)ft_s1,
            (char *)ft_s2
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s1",
            ft_s1,
            sizeof(ft_s1)
        );

        TEST_BUFFER(
            "ft_s2",
            ft_s2,
            sizeof(ft_s2)
        );

        return 0;
    """)

    test.malloc.fail_at(0)

    test.value("ft_is_null").equals(
        "1",
        "malloc failure at call 0",
    )

    test.buffer("ft_s1").equals(
        s1,
        "First source buffer was modified",
    )

    test.buffer("ft_s2").equals(
        s2,
        "Second source buffer was modified",
    )

    test.assert_now()


@suite.case("both empty")
def test_both_empty(c):
    compare(
        c,
        b"\0",
        b"\0",
        b"\0",
    )


@suite.case("empty prefix")
def test_empty_prefix(c):
    compare(
        c,
        b"\0",
        b"hello\0",
        b"hello\0",
    )


@suite.case("empty suffix")
def test_empty_suffix(c):
    compare(
        c,
        b"hello\0",
        b"\0",
        b"hello\0",
    )


@suite.case("simple strings")
def test_simple(c):
    compare(
        c,
        b"hello \0",
        b"world\0",
        b"hello world\0",
    )


@suite.case("multiple words")
def test_multiple_words(c):
    compare(
        c,
        b"Hello, \0",
        b"world!\0",
        b"Hello, world!\0",
    )


@suite.case("special characters")
def test_special(c):
    compare(
        c,
        b"!@#$%^&*()\0",
        b"_+-=[]{}|\0",
        b"!@#$%^&*()_+-=[]{}|\0",
    )


@suite.case("spaces")
def test_spaces(c):
    compare(
        c,
        b"hello   \0",
        b"   world\0",
        b"hello      world\0",
    )


@suite.case("large strings")
def test_large(c):
    s1 = b"0123456789" * 100 + b"\0"
    s2 = b"abcdefghijklmnopqrstuvwxyz" * 100 + b"\0"

    compare(
        c,
        s1,
        s2,
        s1[:-1] + s2,
    )


@suite.case("binary data")
def test_binary(c):
    s1 = b"\x01\x02\x03\x04\0"
    s2 = b"\x05\x06\x07\x08\0"

    compare(
        c,
        s1,
        s2,
        b"\x01\x02\x03\x04\x05\x06\x07\x08\0",
    )


@suite.case("binary data with high bytes")
def test_binary_high_bytes(c):
    s1 = b"\x01\x7f\x80\xfe\0"
    s2 = b"\x81\xff\x02\x03\0"

    compare(
        c,
        s1,
        s2,
        b"\x01\x7f\x80\xfe\x81\xff\x02\x03\0",
    )


@suite.case("binary data mixed with text")
def test_binary_mixed(c):
    s1 = b"hello\x01\x02\x03\0"
    s2 = b"\x7f\x80\xfeworld\0"

    compare(
        c,
        s1,
        s2,
        b"hello\x01\x02\x03\x7f\x80\xfeworld\0",
    )


@suite.case("all byte values")
def test_all_bytes(c):
    s1 = bytes(range(1, 128)) + b"\0"
    s2 = bytes(range(128, 256)) + b"\0"

    compare(
        c,
        s1,
        s2,
        s1[:-1] + s2,
    )


@suite.case("malloc failure 1")
def test_malloc_failure_1(c):
    test_malloc_failures(
        c,
        b"hello \0",
        b"world\0",
        b"hello world\0",
    )


@suite.case("malloc failure 2")
def test_malloc_failure_2(c):
    test_malloc_failures(
        c,
        b"0123456789" * 100 + b"\0",
        b"abcdefghijklmnopqrstuvwxyz" * 100 + b"\0",
        (b"0123456789" * 100) + (b"abcdefghijklmnopqrstuvwxyz" * 100) + b"\0",
    )


@suite.case("malloc failure binary data")
def test_malloc_failure_binary(c):
    test_malloc_failures(
        c,
        b"\x01\x02\x03\x04\0",
        b"\xfe\xff\x80\x81\0",
        b"\x01\x02\x03\x04\xfe\xff\x80\x81\0",
    )
