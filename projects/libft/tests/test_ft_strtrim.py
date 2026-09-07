from framework import Assert, Capture, TestSuite

suite = TestSuite("ft_strtrim")


def compare(c, original, trim_set, expected):
    ft_s1 = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s1",
    )

    ft_set = c.buffer(
        trim_set,
        size=len(trim_set),
        type="char",
        name="ft_set",
    )

    ft = c.ft_strtrim(
        ft_s1,
        ft_set,
    )

    ft.capture_return(
        Capture.buffer(len(expected)),
    )
    ft.run()

    ft.is_not_null(
        "Test return value",
    )
    ft.malloc_count_equals(
        1,
        "Test malloc count",
    )
    ft.malloc_size_equals(
        0,
        len(expected),
        "Test malloc size",
    )
    ft.buffer_equals(
        ft_s1,
        original,
        "Source string was modified",
    )
    ft.buffer_equals(
        ft_set,
        trim_set,
        "Set string was modified",
    )
    ft.assert_return(
        Assert.buffer_equals(expected),
        "Returned buffer mismatch",
    )
    ft.assert_now()


def test_malloc_failures(c, original, trim_set, expected):
    c.malloc.reset()

    ft_s1 = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s1",
    )

    ft_set = c.buffer(
        trim_set,
        size=len(trim_set),
        type="char",
        name="ft_set",
    )

    ft = c.ft_strtrim(
        ft_s1,
        ft_set,
    )

    # Successful run to determine allocation count.
    ft.capture_return(
        Capture.buffer(len(expected)),
    )
    ft.run()

    ft.is_not_null(
        "Test return value",
    )
    ft.malloc_count_equals(
        1,
        "Test malloc count",
    )
    ft.malloc_size_equals(
        0,
        len(expected),
        "Test malloc size",
    )
    ft.buffer_equals(
        ft_s1,
        original,
        "Source string was modified",
    )
    ft.buffer_equals(
        ft_set,
        trim_set,
        "Set string was modified",
    )
    ft.assert_return(
        Assert.buffer_equals(expected),
        "Returned buffer mismatch",
    )
    ft.assert_now()

    malloc_count = ft.malloc_count

    for fail_at in range(malloc_count):
        c.malloc.fail_at(fail_at)

        ft = c.ft_strtrim(
            ft_s1,
            ft_set,
        )

        # Expect pointer to be null so no need to free, and no need to read what inside
        ft.run()

        ft.is_null(
            f"malloc failure at call {fail_at}",
        )
        ft.buffer_equals(
            ft_s1,
            original,
            "Source string was modified",
        )
        ft.buffer_equals(
            ft_set,
            trim_set,
            "Set string was modified",
        )
        ft.assert_now()

    c.malloc.reset()


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
