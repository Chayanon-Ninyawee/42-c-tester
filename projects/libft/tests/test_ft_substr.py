from framework import TestSuite, c_bytes

suite = TestSuite("ft_substr")


def compare(c, original, start, length, expected):
    original_c = c_bytes(original)
    expected_c = c_bytes(expected)

    test = c.include("libft.h", "stdlib.h").code(f"""
        unsigned char ft_s[] = {{{original_c}}};

        char *ft = ft_substr(
            (char *)ft_s,
            {start},
            {length}
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

    test.value("ft_is_null").equals(
        "0",
        "Test return value",
    )

    test.buffer("ft_s").equals(
        original,
        "Source buffer was modified",
    )

    test.buffer("ft_result").equals(
        expected,
        "Returned buffer mismatch",
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

    test.assert_now()


def test_malloc_failures(c, original, start, length, expected):
    original_c = c_bytes(original)
    expected_c = c_bytes(expected)

    test = c.include("libft.h", "stdlib.h").code(f"""
        unsigned char ft_s[] = {{{original_c}}};

        char *ft = ft_substr(
            (char *)ft_s,
            {start},
            {length}
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

    test.value("ft_is_null").equals(
        "0",
        "Test return value",
    )

    test.buffer("ft_s").equals(
        original,
        "Source buffer was modified",
    )

    test.buffer("ft_result").equals(
        expected,
        "Returned buffer mismatch",
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

    test.assert_now()

    test = c.include("libft.h").code(f"""
        unsigned char ft_s[] = {{{original_c}}};

        char *ft = ft_substr(
            (char *)ft_s,
            {start},
            {length}
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

    test.malloc.fail_at(0)

    test.value("ft_is_null").equals(
        "1",
        "malloc failure at call 0",
    )

    test.buffer("ft_s").equals(
        original,
        "Source buffer was modified",
    )

    test.assert_now()


@suite.case("empty string")
def test_empty(c):
    compare(
        c,
        b"\0",
        0,
        10,
        b"\0",
    )


@suite.case("simple substring")
def test_simple(c):
    compare(
        c,
        b"hello world\0",
        0,
        5,
        b"hello\0",
    )


@suite.case("substring from middle")
def test_middle(c):
    compare(
        c,
        b"hello world\0",
        3,
        5,
        b"lo wo\0",
    )


@suite.case("substring to end")
def test_to_end(c):
    compare(
        c,
        b"hello world\0",
        6,
        5,
        b"world\0",
    )


@suite.case("length exceeds remaining string")
def test_length_exceeds(c):
    compare(
        c,
        b"hello world\0",
        6,
        100,
        b"world\0",
    )


@suite.case("start at string length")
def test_start_at_end(c):
    compare(
        c,
        b"hello\0",
        5,
        10,
        b"\0",
    )


@suite.case("start beyond string length")
def test_start_beyond_end(c):
    compare(
        c,
        b"hello\0",
        100,
        10,
        b"\0",
    )


@suite.case("zero length")
def test_zero_length(c):
    compare(
        c,
        b"hello world\0",
        3,
        0,
        b"\0",
    )


@suite.case("single character")
def test_single_character(c):
    compare(
        c,
        b"hello world\0",
        1,
        1,
        b"e\0",
    )


@suite.case("special characters")
def test_special(c):
    compare(
        c,
        b"!@#$%^&*()_+-=[]{}\0",
        3,
        10,
        b"$%^&*()_+-\0",
    )


@suite.case("large string")
def test_large(c):
    original = b"0123456789" * 100 + b"\0"

    compare(
        c,
        original,
        50,
        100,
        original[50:150] + b"\0",
    )


@suite.case("binary data")
def test_binary(c):
    original = b"\x01\x02\x03\x04\x05\x06\x07\x08\0"

    compare(
        c,
        original,
        2,
        4,
        b"\x03\x04\x05\x06\0",
    )


@suite.case("binary data with high bytes")
def test_binary_high_bytes(c):
    original = b"\x01\x02\x7f\x80\x81\xfe\xff\0"

    compare(
        c,
        original,
        1,
        5,
        b"\x02\x7f\x80\x81\xfe\0",
    )


@suite.case("binary data mixed with text")
def test_binary_mixed(c):
    original = b"hello\x01\x02\x03\x7f\x80\xfe\xffworld\0"

    compare(
        c,
        original,
        5,
        8,
        b"\x01\x02\x03\x7f\x80\xfe\xffw\0",
    )


@suite.case("all byte values")
def test_all_bytes(c):
    original = bytes(range(1, 256)) + b"\0"

    compare(
        c,
        original,
        50,
        100,
        original[50:150] + b"\0",
    )


@suite.case("malloc failure 1")
def test_malloc_failure_1(c):
    test_malloc_failures(
        c,
        b"hello world\0",
        3,
        5,
        b"lo wo\0",
    )


@suite.case("malloc failure 2")
def test_malloc_failure_2(c):
    test_malloc_failures(
        c,
        b"This is a test string that might be quite long, since I am going to keep typing. But im too lazy now so my language will not be formal anymore. welp i think it's long enough idk. i will just add some random letter then. iohqwerauiohfjlnuiohefknldvioh maybe some special char too #!@$%&#%^TYUO@I$*@#$^@&(%#^@&$%^@*^$&*(@)$@$(@%$@())) 12345678923235647389058676$%&$%^#%^%^*()*&GCBHJKEGYIGCSB^ROP}P}{{{}||}\0",
        20,
        100,
        b"g that might be quite long, since I am going to keep typing. But im too lazy now so my language will\0",
    )


@suite.case("malloc failure binary data")
def test_malloc_failure_binary(c):
    test_malloc_failures(
        c,
        b"\x01\x02\x03\x04\x05\x06\x07\x08\0",
        2,
        4,
        b"\x03\x04\x05\x06\0",
    )
