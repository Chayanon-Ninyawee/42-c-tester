from framework import Assert, Capture, TestSuite

suite = TestSuite("ft_substr")


def compare(c, original, start, length, expected):
    ft_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s",
    )

    ft = c.ft_substr(
        ft_s,
        str(start),
        str(length),
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
        ft_s,
        original,
        "Source buffer was modified",
    )
    ft.assert_return(
        Assert.buffer_equals(expected),
        "Returned buffer mismatch",
    )

    ft.assert_now()


def test_malloc_failures(c, original, start, length, expected):
    c.malloc.reset()

    ft_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s",
    )

    # Successful run to determine allocation count.
    ft = c.ft_substr(
        ft_s,
        str(start),
        str(length),
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
        ft_s,
        original,
        "Source buffer was modified",
    )
    ft.assert_return(
        Assert.buffer_equals(expected),
        "Returned buffer mismatch",
    )

    ft.assert_now()

    malloc_count = ft.malloc_count

    for fail_at in range(malloc_count):
        c.malloc.fail_at(fail_at)

        ft = c.ft_substr(
            ft_s,
            str(start),
            str(length),
        )

        # Expect pointer to be null so no need to free, and no need to read what inside
        ft.run()

        ft.is_null(
            f"malloc failure at call {fail_at}",
        )
        ft.buffer_equals(
            ft_s,
            original,
            "Source buffer was modified",
        )

        ft.assert_now()

    c.malloc.reset()


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
