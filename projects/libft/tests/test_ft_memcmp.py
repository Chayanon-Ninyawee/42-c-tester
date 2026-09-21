from framework import TestSuite, c_bytes

# NOTE: memcmp() only guarantees the return value to be
# less than, equal to, or greater than 0. It does not
# guarantee the exact difference between the bytes.
suite = TestSuite("ft_memcmp")


def compare(c, s1_original, s2_original, n, expected):
    s1_c = c_bytes(s1_original)
    s2_c = c_bytes(s2_original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_s1[] = {{{s1_c}}};
        unsigned char ft_s2[] = {{{s2_c}}};

        unsigned char libc_s1[] = {{{s1_c}}};
        unsigned char libc_s2[] = {{{s2_c}}};

        int ft = ft_memcmp(
            ft_s1,
            ft_s2,
            {n}
        );

        int libc = memcmp(
            libc_s1,
            libc_s2,
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
        "Test ft_memcmp() returned value",
    )

    test.value("libc").equals(
        str(expected),
        "Reference returned value from memcmp() from libc",
    ).reference()

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
        "s1 buffer was modified by memcmp() from libc",
    ).reference()

    test.buffer("libc_s2").equals(
        s2_original,
        "s2 buffer was modified by memcmp() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("identical buffers")
def test_identical(c):
    compare(
        c,
        b"hello",
        b"hello",
        "5",
        0,
    )


@suite.case("s1 is smaller")
def test_s1_smaller(c):
    compare(
        c,
        b"hello",
        b"jello",
        "5",
        ord("h") - ord("j"),
    )


@suite.case("s1 is greater")
def test_s1_greater(c):
    compare(
        c,
        b"jello",
        b"hello",
        "5",
        ord("j") - ord("h"),
    )


@suite.case("difference in middle")
def test_middle_difference(c):
    compare(
        c,
        b"hello",
        b"heLlo",
        "5",
        ord("l") - ord("L"),
    )


@suite.case("difference at last byte")
def test_last_difference(c):
    compare(
        c,
        b"hella",
        b"hello",
        "5",
        ord("a") - ord("o"),
    )


@suite.case("difference after n")
def test_difference_after_n(c):
    compare(
        c,
        b"helloX",
        b"helloY",
        "5",
        0,
    )


@suite.case("difference at n - 1")
def test_difference_at_n_minus_one(c):
    compare(
        c,
        b"helloX",
        b"helloY",
        "6",
        ord("X") - ord("Y"),
    )


@suite.case("zero bytes")
def test_zero(c):
    compare(
        c,
        b"hello",
        b"world",
        "0",
        0,
    )


@suite.case("one byte")
def test_one(c):
    compare(
        c,
        b"hello",
        b"jello",
        "1",
        ord("h") - ord("j"),
    )


@suite.case("different lengths")
def test_different_lengths(c):
    compare(
        c,
        b"hello",
        b"hello world",
        "5",
        0,
    )


@suite.case("null byte")
def test_null_byte(c):
    compare(
        c,
        b"hello\x00wor\x00ld",
        b"hello\x00wor\x00ld",
        "11",
        0,
    )


@suite.case("binary data")
def test_binary(c):
    compare(
        c,
        b"\x01\x80\xff\x7f",
        b"\x01\x80\x7f\x7f",
        "4",
        0xFF - 0x7F,
    )


@suite.case("unsigned byte comparison")
def test_unsigned_bytes(c):
    compare(
        c,
        b"\xff",
        b"\x01",
        "1",
        0xFF - 0x01,
    )


@suite.case("empty buffers")
def test_empty(c):
    compare(
        c,
        b"abcd",
        b"efgh",
        "0",
        0,
    )
