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

    ft = c.ft_strdup(
        ft_s,
    )

    libc = c.strdup(
        libc_s,
    )

    ft.is_not_null(
        "Test return value",
    )
    ft.malloc_count_equals(
        1,
        "Test malloc count",
    )
    ft.malloc_size_equals(
        0,
        # no need to +1 since the len already included the null terminator
        len(original) + 1,
        "Test malloc size",
    )
    ft.buffer_equals(
        ft_s,
        original,
        "Source buffer was modified",
    )

    libc.is_not_null(
        "Test return value from strdup() from libc",
    )
    libc.buffer_equals(
        libc_s,
        original,
        "Source buffer was modified by strdup() from libc",
    ).assert_reference()

    ft.assert_now()


def test_malloc_failures(c, original):
    c.malloc.reset()

    ft_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s",
    )

    result = c.ft_strdup(
        ft_s,
    )
    result.assert_now()

    malloc_count = result.malloc_count

    for fail_at in range(malloc_count):
        c.malloc.fail_at(fail_at)

        result = c.ft_strdup(
            ft_s,
        )

        result.is_null(
            f"malloc failure at call {fail_at}",
        ).assert_now()

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
    compare(c, (b"0123456789" * 100))  # + b"\0",


@suite.case("large string 2")
def test_large_2(c):
    compare(
        c,
        b"This is a test string that might be quite long, since I am going to keep typing. But im too lazy now so my language will not be formal anymore. welp i think it's long enough idk. i will just add some random letter then. iohqwerauiohfjlnuiohefknldvioh maybe some special char too #!@$%&#%^TYUO@I$*@#$^@&(%#^@&$%^@*^$&*(@)$@$(@%$@())) 12345678923235647389058676$%&$%^#%^%^*()*&GCBHJKEGYIGCSB^ROP}P}{{{}||}\0",
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
