from framework import TestSuite, c_bytes

suite = TestSuite("ft_strncmp")


def compare(c, s1_original, s2_original, n, expected):
    s1_c = c_bytes(s1_original)
    s2_c = c_bytes(s2_original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_s1[] = {{{s1_c}}};
        unsigned char ft_s2[] = {{{s2_c}}};

        unsigned char libc_s1[] = {{{s1_c}}};
        unsigned char libc_s2[] = {{{s2_c}}};

        int ft = ft_strncmp(
            (char *)ft_s1,
            (char *)ft_s2,
            {n}
        );

        int libc = strncmp(
            (char *)libc_s1,
            (char *)libc_s2,
            {n}
        );

        TEST_VALUE("ft", "%d", ft);
        TEST_VALUE("libc", "%d", libc);

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

        TEST_BUFFER(
            "libc_s1",
            libc_s1,
            sizeof(libc_s1)
        );

        TEST_BUFFER(
            "libc_s2",
            libc_s2,
            sizeof(libc_s2)
        );

        return 0;
    """)

    test.value("ft").equals(
        str(expected),
        "Test ft_strncmp() returned value",
    )

    # NOTE: libc only care about if it's == 0, < 0, or > 0
    # test.value("libc").equals(
    #     str(expected),
    #     "Reference returned value from strncmp() from libc",
    # ).reference()

    test.buffer("ft_s1").equals(
        s1_original,
        "s1 buffer was modified",
    )

    test.buffer("ft_s2").equals(
        s2_original,
        "s2 buffer was modified",
    )

    test.buffer("libc_s1").equals(
        s1_original,
        "s1 buffer was modified by strncmp() from libc",
    ).reference()

    test.buffer("libc_s2").equals(
        s2_original,
        "s2 buffer was modified by strncmp() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("identical strings")
def test_identical(c):
    compare(
        c,
        b"hello\x00",
        b"hello\x00",
        "5",
        0,
    )


@suite.case("different strings")
def test_different(c):
    compare(
        c,
        b"hello\x00",
        b"world\x00",
        "5",
        ord("h") - ord("w"),
    )


@suite.case("s1 is smaller")
def test_s1_smaller(c):
    compare(
        c,
        b"abc\x00",
        b"abd\x00",
        "3",
        ord("c") - ord("d"),
    )


@suite.case("s1 is greater")
def test_s1_greater(c):
    compare(
        c,
        b"abd\x00",
        b"abc\x00",
        "3",
        ord("d") - ord("c"),
    )


@suite.case("difference after n")
def test_difference_after_n(c):
    compare(
        c,
        b"helloX\x00",
        b"helloY\x00",
        "5",
        0,
    )


@suite.case("difference at n")
def test_difference_at_n(c):
    compare(
        c,
        b"helloX\x00",
        b"helloY\x00",
        "6",
        ord("X") - ord("Y"),
    )


@suite.case("n is zero")
def test_zero(c):
    compare(
        c,
        b"hello\x00",
        b"world\x00",
        "0",
        0,
    )


@suite.case("n is one")
def test_one(c):
    compare(
        c,
        b"hello\x00",
        b"world\x00",
        "1",
        ord("h") - ord("w"),
    )


@suite.case("empty first string")
def test_empty_first(c):
    compare(
        c,
        b"\x00",
        b"hello\x00",
        "5",
        -ord("h"),
    )


@suite.case("empty second string")
def test_empty_second(c):
    compare(
        c,
        b"hello\x00",
        b"\x00",
        "5",
        ord("h"),
    )


@suite.case("one string is prefix")
def test_prefix(c):
    compare(
        c,
        b"hello\x00",
        b"hello world\x00",
        "10",
        -ord(" "),
    )


@suite.case("binary data")
def test_binary(c):
    compare(
        c,
        b"\x01\x80\xff\x00",
        b"\x01\x80\x7f\x00",
        "4",
        0xFF - 0x7F,
    )


@suite.case("comparison stops at null")
def test_null_terminator(c):
    compare(
        c,
        b"abc\x00xxx",
        b"abc\x00yyy",
        "7",
        0,
    )
