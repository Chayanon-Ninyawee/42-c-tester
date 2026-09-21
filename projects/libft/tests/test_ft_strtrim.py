from framework import TestSuite, c_bytes

suite = TestSuite("ft_strtrim")


def compare(c, original, trim_set, expected):
    original_c = c_bytes(original)
    trim_set_c = c_bytes(trim_set)

    test = c.include("libft.h", "stdlib.h").code(f"""
        unsigned char ft_s1[] = {{{original_c}}};
        unsigned char ft_set[] = {{{trim_set_c}}};

        char *ft = ft_strtrim(
            (char *)ft_s1,
            (char *)ft_set
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s1",
            ft_s1,
            sizeof(ft_s1)
        );

        TEST_BUFFER(
            "ft_set",
            ft_set,
            sizeof(ft_set)
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
        original,
        "Source string was modified",
    )

    test.buffer("ft_set").equals(
        trim_set,
        "Set string was modified",
    )

    test.buffer("ft_result").equals(
        expected,
        "Returned buffer mismatch",
    )

    test.assert_now()


def test_malloc_failures(c, original, trim_set, expected):
    original_c = c_bytes(original)
    trim_set_c = c_bytes(trim_set)

    test = c.include("libft.h", "stdlib.h").code(f"""
        unsigned char ft_s1[] = {{{original_c}}};
        unsigned char ft_set[] = {{{trim_set_c}}};

        char *ft = ft_strtrim(
            (char *)ft_s1,
            (char *)ft_set
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s1",
            ft_s1,
            sizeof(ft_s1)
        );

        TEST_BUFFER(
            "ft_set",
            ft_set,
            sizeof(ft_set)
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
        original,
        "Source string was modified",
    )

    test.buffer("ft_set").equals(
        trim_set,
        "Set string was modified",
    )

    test.buffer("ft_result").equals(
        expected,
        "Returned buffer mismatch",
    )

    test.assert_now()

    test = c.include("libft.h").code(f"""
        unsigned char ft_s1[] = {{{original_c}}};
        unsigned char ft_set[] = {{{trim_set_c}}};

        char *ft = ft_strtrim(
            (char *)ft_s1,
            (char *)ft_set
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s1",
            ft_s1,
            sizeof(ft_s1)
        );

        TEST_BUFFER(
            "ft_set",
            ft_set,
            sizeof(ft_set)
        );

        return 0;
    """)

    test.malloc.fail_at(0)

    test.value("ft_is_null").equals(
        "1",
        "malloc failure at call 0",
    )

    test.buffer("ft_s1").equals(
        original,
        "Source string was modified",
    )

    test.buffer("ft_set").equals(
        trim_set,
        "Set string was modified",
    )

    test.assert_now()


@suite.case("empty string")
def test_empty(c):
    compare(
        c,
        b"\0",
        b" \t\n\0",
        b"\0",
    )


@suite.case("empty set")
def test_empty_set(c):
    compare(
        c,
        b"hello world\0",
        b"\0",
        b"hello world\0",
    )


@suite.case("trim both sides")
def test_both(c):
    compare(
        c,
        b"   hello world   \0",
        b" \0",
        b"hello world\0",
    )


@suite.case("trim left side")
def test_left(c):
    compare(
        c,
        b"   hello world\0",
        b" \0",
        b"hello world\0",
    )


@suite.case("trim right side")
def test_right(c):
    compare(
        c,
        b"hello world   \0",
        b" \0",
        b"hello world\0",
    )


@suite.case("multiple trim characters")
def test_multiple_characters(c):
    compare(
        c,
        b"\t\n\r  hello world  \r\n\t\0",
        b" \t\n\r\0",
        b"hello world\0",
    )


@suite.case("different characters at each side")
def test_different_characters(c):
    compare(
        c,
        b"xxx---hello world---yyy\0",
        b"xy\0",
        b"---hello world---\0",
    )


@suite.case("mixed trim characters")
def test_mixed(c):
    compare(
        c,
        b"xxxyyyhello worldyyyxxx\0",
        b"xy\0",
        b"hello world\0",
    )


@suite.case("no characters to trim")
def test_no_trim(c):
    compare(
        c,
        b"hello world\0",
        b"xyz\0",
        b"hello world\0",
    )


@suite.case("all characters trimmed")
def test_all_trimmed(c):
    compare(
        c,
        b"   \t\n\r   \0",
        b" \t\n\r\0",
        b"\0",
    )


@suite.case("single character")
def test_single_character(c):
    compare(
        c,
        b"---a---\0",
        b"-\0",
        b"a\0",
    )


@suite.case("single character completely trimmed")
def test_single_character_trimmed(c):
    compare(
        c,
        b"---\0",
        b"-\0",
        b"\0",
    )


@suite.case("set contains repeated characters")
def test_repeated_set(c):
    compare(
        c,
        b"---hello---\0",
        b"--abc---\0",
        b"hello\0",
    )


@suite.case("special characters")
def test_special(c):
    compare(
        c,
        b"!@#$%^&*()hello world()&^%$#@!\0",
        b"!@#$%^&*()\0",
        b"hello world\0",
    )


@suite.case("spaces inside string")
def test_spaces_inside(c):
    compare(
        c,
        b"   hello   world   \0",
        b" \0",
        b"hello   world\0",
    )


@suite.case("binary data")
def test_binary(c):
    compare(
        c,
        b"\x01\x02\x03hello\x04\x05\x06\0",
        b"\x01\x02\x03\x04\x05\x06\0",
        b"hello\0",
    )


@suite.case("binary data with high bytes")
def test_binary_high_bytes(c):
    compare(
        c,
        b"\x80\x81\xfe\xffhello\xfe\xff\x80\x81\0",
        b"\x80\x81\xfe\xff\0",
        b"hello\0",
    )


@suite.case("high bytes not in set")
def test_high_bytes_not_trimmed(c):
    compare(
        c,
        b"\x80\x81hello\xfe\xff\0",
        b"\x01\x02\x03\0",
        b"\x80\x81hello\xfe\xff\0",
    )


@suite.case("large string")
def test_large(c):
    original = b" " * 100 + b"0123456789" * 100 + b" " * 100 + b"\0"

    compare(
        c,
        original,
        b" \0",
        b"0123456789" * 100 + b"\0",
    )


@suite.case("malloc failure 1")
def test_malloc_failure_1(c):
    test_malloc_failures(
        c,
        b"   hello world   \0",
        b" \0",
        b"hello world\0",
    )


@suite.case("malloc failure 2")
def test_malloc_failure_2(c):
    test_malloc_failures(
        c,
        b"\t\n\r  hello world  \r\n\t\0",
        b" \t\n\r\0",
        b"hello world\0",
    )


@suite.case("malloc failure binary data")
def test_malloc_failure_binary(c):
    test_malloc_failures(
        c,
        b"\x01\x02hello\xfe\xff\0",
        b"\x01\x02\xfe\xff\0",
        b"hello\0",
    )
