from framework import TestSuite

suite = TestSuite("ft_strjoin")


def compare(c, s1, s2, expected):
    ft_s1 = c.buffer(
        s1,
        size=len(s1),
        type="char",
        name="ft_s1",
    )

    ft_s2 = c.buffer(
        s2,
        size=len(s2),
        type="char",
        name="ft_s2",
    )

    ft = c.ft_strjoin(
        ft_s1,
        ft_s2,
    )

    ft.capture_return_buffer(len(expected))
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
        s1,
        "First source buffer was modified",
    )
    ft.buffer_equals(
        ft_s2,
        s2,
        "Second source buffer was modified",
    )
    ft.returned_buffer_equals(
        expected,
        "Returned buffer mismatch",
    )
    ft.assert_now()


def test_malloc_failures(c, s1, s2, expected):
    c.malloc.reset()

    ft_s1 = c.buffer(
        s1,
        size=len(s1),
        type="char",
        name="ft_s1",
    )

    ft_s2 = c.buffer(
        s2,
        size=len(s2),
        type="char",
        name="ft_s2",
    )

    ft = c.ft_strjoin(
        ft_s1,
        ft_s2,
    )

    ft.capture_return_buffer(len(expected))
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
        s1,
        "First source buffer was modified",
    )
    ft.buffer_equals(
        ft_s2,
        s2,
        "Second source buffer was modified",
    )
    ft.returned_buffer_equals(
        expected,
        "Returned buffer mismatch",
    )
    ft.assert_now()

    malloc_count = ft.malloc_count

    for fail_at in range(malloc_count):
        c.malloc.fail_at(fail_at)

        ft = c.ft_strjoin(
            ft_s1,
            ft_s2,
        )
        ft.run()

        ft.is_null(
            f"malloc failure at call {fail_at}",
        )
        ft.buffer_equals(
            ft_s1,
            s1,
            "First source buffer was modified",
        )
        ft.buffer_equals(
            ft_s2,
            s2,
            "Second source buffer was modified",
        )
        ft.assert_now()

    c.malloc.reset()


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
