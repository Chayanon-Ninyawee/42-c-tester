from framework import TestSuite, c_bytes

suite = TestSuite("ft_strnstr")


def compare(c, big_original, little_original, len_value, expected_offset):
    big_c = c_bytes(big_original)
    little_c = c_bytes(little_original)

    test = c.include("libft.h", "bsd/string.h").code(f"""
        unsigned char ft_big[] = {{{big_c}}};
        unsigned char ft_little[] = {{{little_c}}};

        unsigned char libc_big[] = {{{big_c}}};
        unsigned char libc_little[] = {{{little_c}}};

        char *ft = ft_strnstr(
            (char *)ft_big,
            (char *)ft_little,
            {len_value}
        );

        char *libc = strnstr(
            (char *)libc_big,
            (char *)libc_little,
            {len_value}
        );

        ptrdiff_t ft_offset = ft
            ? ft - (char *)ft_big
            : -1;

        ptrdiff_t libc_offset = libc
            ? libc - (char *)libc_big
            : -1;

        TEST_VALUE("ft", "%td", ft_offset);
        TEST_VALUE("libc", "%td", libc_offset);

        TEST_BUFFER(
            "ft_big",
            ft_big,
            sizeof(ft_big)
        );

        TEST_BUFFER(
            "ft_little",
            ft_little,
            sizeof(ft_little)
        );

        TEST_BUFFER(
            "libc_big",
            libc_big,
            sizeof(libc_big)
        );

        TEST_BUFFER(
            "libc_little",
            libc_little,
            sizeof(libc_little)
        );

        return 0;
    """)

    test.value("ft").equals(
        str(expected_offset if expected_offset is not None else -1),
        "Test ft_strnstr() returned pointer",
    )

    test.value("libc").equals(
        str(expected_offset if expected_offset is not None else -1),
        "Reference returned pointer from strnstr() from libc",
    ).reference()

    test.buffer("ft_big").equals(
        big_original,
        "Big buffer was modified",
    )

    test.buffer("ft_little").equals(
        little_original,
        "Little buffer was modified",
    )

    test.buffer("libc_big").equals(
        big_original,
        "Big buffer was modified by strnstr() from libc",
    ).reference()

    test.buffer("libc_little").equals(
        little_original,
        "Little buffer was modified by strnstr() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("finds substring")
def test_normal(c):
    big_original = b"hello world\x00"
    little_original = b"world\x00"
    len_value = "11"
    expected_offset = 6

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("finds first occurrence")
def test_first_occurrence(c):
    big_original = b"hello hello\x00"
    little_original = b"hello\x00"
    len_value = "11"
    expected_offset = 0

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("finds first occurrence only")
def test_multiple_occurrences(c):
    big_original = b"abcabcabc\x00"
    little_original = b"abc\x00"
    len_value = "9"
    expected_offset = 0

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("substring not found")
def test_not_found(c):
    big_original = b"hello world\x00"
    little_original = b"xyz\x00"
    len_value = "11"
    expected_offset = None

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("empty little")
def test_empty_little(c):
    big_original = b"hello world\x00"
    little_original = b"\x00"
    len_value = "11"
    expected_offset = 0

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("empty big")
def test_empty_big(c):
    big_original = b"\x00"
    little_original = b"hello\x00"
    len_value = "1"
    expected_offset = None

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("empty big and little")
def test_both_empty(c):
    big_original = b"\x00"
    little_original = b"\x00"
    len_value = "1"
    expected_offset = 0

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("length stops before match")
def test_length_too_short(c):
    big_original = b"hello world\x00"
    little_original = b"world\x00"
    len_value = "10"
    expected_offset = None

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("length includes match")
def test_length_includes_match(c):
    big_original = b"hello world\x00"
    little_original = b"world\x00"
    len_value = "11"
    expected_offset = 6

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("match ends exactly at length")
def test_match_at_boundary(c):
    big_original = b"hello world\x00"
    little_original = b"world\x00"
    len_value = "11"
    expected_offset = 6

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("partial match at end")
def test_partial_match(c):
    big_original = b"hello wor\x00"
    little_original = b"world\x00"
    len_value = "9"
    expected_offset = None

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("zero length")
def test_zero_length(c):
    big_original = b"hello world\x00"
    little_original = b"hello\x00"
    len_value = "0"
    expected_offset = None

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("one byte length")
def test_one_byte(c):
    big_original = b"hello\x00"
    little_original = b"h\x00"
    len_value = "1"
    expected_offset = 0

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("substring starts at boundary")
def test_boundary(c):
    big_original = b"1234567890abc\x00"
    little_original = b"abc\x00"
    len_value = "13"
    expected_offset = 10

    compare(c, big_original, little_original, len_value, expected_offset)


@suite.case("binary data")
def test_binary(c):
    big_original = b"\x01\x02\x80\xff\x00\x7f"
    little_original = b"\x80\xff\x00"
    len_value = "6"
    expected_offset = 2

    compare(c, big_original, little_original, len_value, expected_offset)
