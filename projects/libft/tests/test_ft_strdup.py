from framework import TestSuite, c_bytes

suite = TestSuite("ft_strdup")


def compare(c, original):
    original_c = c_bytes(original)
    size = len(original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_s[] = {{{original_c}}};
        unsigned char libc_s[] = {{{original_c}}};

        char *ft = ft_strdup((char *)ft_s);
        char *libc = strdup((char *)libc_s);

        int ft_is_null = (ft == NULL);
        int libc_is_null = (libc == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);
        TEST_VALUE("libc_is_null", "%d", libc_is_null);

        TEST_BUFFER(
            "ft_s",
            ft_s,
            sizeof(ft_s)
        );

        TEST_BUFFER(
            "libc_s",
            libc_s,
            sizeof(libc_s)
        );

        if (ft != NULL)
            TEST_BUFFER(
                "ft_result",
                ft,
                {size}
            );

        if (libc != NULL)
            TEST_BUFFER(
                "libc_result",
                libc,
                {size}
            );

        if (ft)
            free(ft);
        if (libc)
            free(libc);

        return 0;
    """)

    test.value("ft_is_null").equals(
        "0",
        "Test return value",
    )

    test.value("libc_is_null").equals(
        "0",
        "Reference return value from strdup() from libc",
    ).reference()

    test.buffer("ft_s").equals(
        original,
        "Source buffer was modified",
    )

    test.buffer("libc_s").equals(
        original,
        "Source buffer was modified by strdup() from libc",
    ).reference()

    test.buffer("ft_result").equals(
        original,
        "Returned buffer mismatch",
    )

    test.buffer("libc_result").equals(
        original,
        "Returned buffer mismatch from strdup() from libc",
    ).reference()

    test.malloc.count(
        1,
        "Test malloc count",
    )

    test.malloc.size(
        0,
        size,
        "Test malloc size",
    )

    test.assert_now()


def test_malloc_failures(c, original):
    original_c = c_bytes(original)
    size = len(original)

    test = c.include("libft.h").code(f"""
        unsigned char ft_s[] = {{{original_c}}};

        char *ft = ft_strdup((char *)ft_s);

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s",
            ft_s,
            sizeof(ft_s)
        );

        if (ft != NULL)
            TEST_BUFFER(
                "ft_result",
                ft,
                {size}
            );

        if (ft)
            free(ft);

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
        original,
        "Returned buffer mismatch",
    )

    test.malloc.count(
        1,
        "Test malloc count",
    )

    test.malloc.size(
        0,
        size,
        "Test malloc size",
    )

    test.assert_now()

    test = c.include("libft.h").code(f"""
        unsigned char ft_s[] = {{{original_c}}};

        char *ft = ft_strdup((char *)ft_s);

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
    )


@suite.case("simple string")
def test_simple(c):
    compare(
        c,
        b"hello\0",
    )


@suite.case("string with spaces")
def test_spaces(c):
    compare(
        c,
        b"hello world\0",
    )


@suite.case("special characters")
def test_special(c):
    compare(
        c,
        b"!@#$%^&*()_+-=[]{}\0",
    )


@suite.case("large string 1")
def test_large_1(c):
    compare(
        c,
        b"0123456789" * 100 + b"\0",
    )


@suite.case("large string 2")
def test_large_2(c):
    compare(
        c,
        b"This is a test string that might be quite long, since I am going to keep typing. But im too lazy now so my language will not be formal anymore. welp i think it's long enough idk. i will just add some random letter then. iohqwerauiohfjlnuiohefknldvioh maybe some special char too #!@$%&#%^TYUO@I$*@#$^@&(%#^@&$%^@*^$&*(@)$@$(@%$@())) 12345678923235647389058676$%&$%^#%^%^*()*&GCBHJKEGYIGCSB^ROP}P}{{{}||}\0",
    )


@suite.case("binary data")
def test_binary(c):
    compare(
        c,
        b"\x01\x02\x03\x04\x05\x06\x07\x08\0",
    )


@suite.case("binary data with high bytes")
def test_binary_high_bytes(c):
    compare(
        c,
        b"\x67\x01\x02\x7f\x80\x81\xfe\xff\0",
    )


@suite.case("binary data mixed with text")
def test_binary_mixed(c):
    compare(
        c,
        b"hello\x01\x02\x03\x7f\x80\xfe\xffworld\0",
    )


@suite.case("all byte values")
def test_all_bytes(c):
    compare(
        c,
        bytes(range(1, 256)) + b"\0",
    )


@suite.case("malloc failure 1")
def test_malloc_failure_1(c):
    test_malloc_failures(
        c,
        b"hello world\0",
    )


@suite.case("malloc failure 2")
def test_malloc_failure_2(c):
    test_malloc_failures(
        c,
        b"This is a test string that might be quite long, since I am going to keep typing. But im too lazy now so my language will not be formal anymore. welp i think it's long enough idk. i will just add some random letter then. iohqwerauiohfjlnuiohefknldvioh maybe some special char too #!@$%&#%^TYUO@I$*@#$^@&(%#^@&$%^@*^$&*(@)$@$(@%$@())) 12345678923235647389058676$%&$%^#%^%^*()*&GCBHJKEGYIGCSB^ROP}P}{{{}||}\0",
    )


@suite.case("malloc failure binary data")
def test_malloc_failure_binary(c):
    test_malloc_failures(
        c,
        b"\x01\x02\x03\x04\x05\x06\x07\x08\0",
    )
