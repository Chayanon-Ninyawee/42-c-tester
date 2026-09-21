from framework import TestSuite, c_bytes

suite = TestSuite("ft_memchr")


def compare(c, original, argument, n, expected_offset):
    original_c = c_bytes(original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_buffer[] = {{{original_c}}};
        unsigned char libc_buffer[] = {{{original_c}}};

        void *ft = ft_memchr(
            ft_buffer,
            {argument},
            {n}
        );

        void *libc = memchr(
            libc_buffer,
            {argument},
            {n}
        );

        ptrdiff_t ft_offset = ft
            ? (unsigned char *)ft - ft_buffer
            : -1;

        ptrdiff_t libc_offset = libc
            ? (unsigned char *)libc - libc_buffer
            : -1;

        TEST_VALUE("ft", "%td", ft_offset);
        TEST_VALUE("libc", "%td", libc_offset);

        TEST_BUFFER(
            "ft_buffer",
            ft_buffer,
            sizeof(ft_buffer)
        );

        TEST_BUFFER(
            "libc_buffer",
            libc_buffer,
            sizeof(libc_buffer)
        );

        return 0;
    """)

    test.value("ft").equals(
        str(expected_offset if expected_offset is not None else -1),
        "Test ft_memchr() returned pointer",
    )

    test.value("libc").equals(
        str(expected_offset if expected_offset is not None else -1),
        "Reference returned pointer from memchr() from libc",
    ).reference()

    test.buffer("ft_buffer").equals(
        original,
        "Input buffer was modified",
    )

    test.buffer("libc_buffer").equals(
        original,
        "Input buffer was modified by memchr() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("finds first occurrence")
def test_first_occurrence(c):
    compare(
        c,
        b"hello world",
        ord("l"),
        "11",
        2,
    )


@suite.case("finds later occurrence")
def test_later_occurrence(c):
    compare(
        c,
        b"hello world",
        ord("w"),
        "11",
        6,
    )


@suite.case("finds last occurrence")
def test_last_occurrence(c):
    compare(
        c,
        b"hello world",
        ord("d"),
        "11",
        10,
    )


@suite.case("character not found")
def test_not_found(c):
    compare(
        c,
        b"hello world",
        ord("z"),
        "11",
        None,
    )


@suite.case("does not search past n")
def test_stops_at_n(c):
    compare(
        c,
        b"hello world",
        ord("w"),
        "5",
        None,
    )


@suite.case("finds character at n - 1")
def test_at_end_of_range(c):
    compare(
        c,
        b"hello world",
        ord("o"),
        "5",
        4,
    )


@suite.case("zero bytes")
def test_zero(c):
    compare(
        c,
        b"hello world",
        ord("h"),
        "0",
        None,
    )


@suite.case("one byte")
def test_one(c):
    compare(
        c,
        b"hello world",
        ord("h"),
        "1",
        0,
    )


@suite.case("binary data")
def test_binary(c):
    compare(
        c,
        b"\x01\x02\x80\xff\x00\x7f",
        0x80,
        "6",
        2,
    )


@suite.case("unsigned char comparison")
def test_unsigned_char(c):
    compare(
        c,
        b"\xff\x80\x01\x7f",
        255,
        "4",
        0,
    )


@suite.case("negative c matches unsigned byte")
def test_negative_c(c):
    compare(
        c,
        b"\xff\x80\x01\x7f",
        -1,
        "4",
        0,
    )


@suite.case("empty buffer")
def test_empty(c):
    compare(
        c,
        b"abcd",
        ord("a"),
        "0",
        None,
    )
