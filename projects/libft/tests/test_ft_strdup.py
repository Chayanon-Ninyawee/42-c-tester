from framework import TestSuite

suite = TestSuite("ft_strdup")


def compare(c, original):
    ft_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s",
    )

    libc_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="libc_s",
    )

    ft = c.ft_strdup(ft_s)
    libc = c.strdup(libc_s)

    ft.capture_return_buffer(len(original))
    libc.capture_return_buffer(len(original))

    ft.run()
    libc.run()

    ft.is_not_null(
        "Test return value",
    )
    ft.malloc_count_equals(
        1,
        "Test malloc count",
    )
    ft.malloc_size_equals(
        0,
        len(original),
        "Test malloc size",
    )
    ft.buffer_equals(
        ft_s,
        original,
        "Source buffer was modified",
    )
    ft.returned_buffer_equals(
        original,
        "Returned buffer mismatch",
    )

    libc.is_not_null(
        "Test return value from strdup() from libc",
    )
    libc.buffer_equals(
        libc_s,
        original,
        "Source buffer was modified by strdup() from libc",
    )
    libc.returned_buffer_equals(
        original,
        "Returned buffer mismatch from strdup() from libc",
    )

    libc.assert_reference()
    ft.assert_now()


def test_malloc_failures(c, original):
    c.malloc.reset()

    ft_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s",
    )

    ft = c.ft_strdup(ft_s)

    ft.capture_return_buffer(len(original))
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
        len(original),
        "Test malloc size",
    )
    ft.buffer_equals(
        ft_s,
        original,
        "Source buffer was modified",
    )
    ft.returned_buffer_equals(
        original,
        "Returned buffer mismatch",
    )
    ft.assert_now()

    malloc_count = ft.malloc_count

    for fail_at in range(malloc_count):
        c.malloc.fail_at(fail_at)

        ft = c.ft_strdup(
            ft_s,
        )
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
    compare(c, (b"0123456789" * 100 + b"\0"))


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
