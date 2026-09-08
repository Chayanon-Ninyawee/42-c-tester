from framework import Assert, Capture, TestSuite

suite = TestSuite("ft_strmapi")


def compare(c, original, expected, callback):
    ft_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s",
    )

    ft = c.ft_strmapi(
        ft_s,
        callback,
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
        "Source string was modified",
    )
    ft.assert_return(
        Assert.buffer_equals(expected),
        "Returned buffer mismatch",
    )
    ft.assert_now()


def test_malloc_failures(c, original, expected, callback):
    c.malloc.reset()

    ft_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s",
    )

    ft = c.ft_strmapi(
        ft_s,
        callback,
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
        ft_s,
        original,
        "Source string was modified",
    )
    ft.assert_return(
        Assert.buffer_equals(expected),
        "Returned buffer mismatch",
    )
    ft.assert_now()

    malloc_count = ft.malloc_count

    for fail_at in range(malloc_count):
        c.malloc.fail_at(fail_at)

        ft = c.ft_strmapi(
            ft_s,
            callback,
        )

        # Expect pointer to be null so no need to free, and no need to read what inside
        ft.run()

        ft.is_null(
            f"malloc failure at call {fail_at}",
        )
        ft.buffer_equals(
            ft_s,
            original,
            "Source string was modified",
        )
        ft.assert_now()

    c.malloc.reset()


@suite.case("identity")
def test_identity(c):
    identity = c.callback(
        name="identity",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; return c;",
    )

    compare(
        c,
        b"hello world\0",
        b"hello world\0",
        identity,
    )


@suite.case("empty string")
def test_empty(c):
    identity = c.callback(
        name="identity",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; return c;",
    )

    compare(
        c,
        b"\0",
        b"\0",
        identity,
    )


@suite.case("index is passed correctly")
def test_index(c):
    char_index = c.callback(
        name="char_index",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)c; return '0' + i;",
    )

    compare(
        c,
        b"abcdef\0",
        b"012345\0",
        char_index,
    )


@suite.case("character is passed correctly")
def test_character(c):
    identity = c.callback(
        name="character",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; return c;",
    )

    compare(
        c,
        b"ABCxyz123\0",
        b"ABCxyz123\0",
        identity,
    )


@suite.case("index and character")
def test_index_and_character(c):
    increment = c.callback(
        name="increment",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="return c + i;",
    )

    compare(
        c,
        b"abcde\0",
        b"acegi\0",
        increment,
    )


@suite.case("decrement")
def test_decrement(c):
    decrement = c.callback(
        name="decrement",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="return c - i;",
    )

    compare(
        c,
        b"edcba\0",
        b"eca_]\0",
        decrement,
    )


@suite.case("same callback result")
def test_same_result(c):
    star = c.callback(
        name="star",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; (void)c; return '*';",
    )

    compare(
        c,
        b"hello world\0",
        b"***********\0",
        star,
    )


@suite.case("index based transformation")
def test_index_transformation(c):
    transform = c.callback(
        name="index_transform",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="""
            if (i % 2 == 0)
                return c + 1;
            return c - 1;
        """,
    )

    compare(
        c,
        b"abcdefhh\0",
        b"badcfeig\0",
        transform,
    )


@suite.case("character based transformation")
def test_character_transformation(c):
    transform = c.callback(
        name="character_transform",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="""
            (void)i;
            if (c >= 'a' && c <= 'z')
                return c - 'a' + 'A';
            if (c >= 'A' && c <= 'Z')
                return c - 'A' + 'a';
            return c;
        """,
    )

    compare(
        c,
        b"Hello WORLD 123!\0",
        b"hELLO world 123!\0",
        transform,
    )


@suite.case("index and character dependent transformation")
def test_index_character_transformation(c):
    transform = c.callback(
        name="complex_transform",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="""
            if (c >= 'a' && c <= 'z')
                c -= 'a';

            return (c + i * 3) % 26 + 'A';
        """,
    )

    compare(
        c,
        b"abcdef\0",
        b"AEIMQU\0",
        transform,
    )


@suite.case("conditional index transformation")
def test_conditional_index(c):
    transform = c.callback(
        name="conditional_index",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="""
            if (i < 3)
                return c + 10;

            if (i % 2 == 0)
                return c - 2;

            return c + 2;
        """,
    )

    compare(
        c,
        b"abcdef\0",
        b"klmfch\0",
        transform,
    )


@suite.case("multiple operations")
def test_multiple_operations(c):
    transform = c.callback(
        name="multiple_operations",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="""
            int value;

            value = c;
            value += i;
            value *= 2;
            value -= 3;

            return value;
        """,
    )

    compare(
        c,
        b"abcdef\0",
        b"\xbf\xc3\xc7\xcb\xcf\xd3\0",
        transform,
    )


@suite.case("character classification")
def test_character_classification(c):
    classify = c.callback(
        name="classify",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="""
            (void)i;
            if (c >= '0' && c <= '9')
                return 'D';

            if (c >= 'a' && c <= 'z')
                return 'L';

            if (c >= 'A' && c <= 'Z')
                return 'U';

            if (c == ' ')
                return 'S';

            return '?';
        """,
    )

    compare(
        c,
        b"aZ5 !b2C\0",
        b"LUDS?LDU\0",
        classify,
    )


@suite.case("special characters")
def test_special(c):
    identity = c.callback(
        name="special",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; return c;",
    )

    compare(
        c,
        b"!@#$%^&*()[]{};:'\",.<>/?\0",
        b"!@#$%^&*()[]{};:'\",.<>/?\0",
        identity,
    )


@suite.case("spaces and whitespace")
def test_whitespace(c):
    identity = c.callback(
        name="whitespace",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; return c;",
    )

    compare(
        c,
        b" \t\n\rhello world\t\n\0",
        b" \t\n\rhello world\t\n\0",
        identity,
    )


@suite.case("binary data")
def test_binary(c):
    identity = c.callback(
        name="binary",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; return c;",
    )

    compare(
        c,
        b"\x01\x02\x03hello\x04\x05\x06\0",
        b"\x01\x02\x03hello\x04\x05\x06\0",
        identity,
    )


@suite.case("high bytes")
def test_high_bytes(c):
    identity = c.callback(
        name="high_bytes",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; return c;",
    )

    compare(
        c,
        b"\x80\x81\xfe\xffhello\0",
        b"\x80\x81\xfe\xffhello\0",
        identity,
    )


@suite.case("large string")
def test_large(c):
    identity = c.callback(
        name="large",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; return c;",
    )

    original = b"0123456789" * 1000 + b"\0"

    compare(
        c,
        original,
        original,
        identity,
    )


@suite.case("malloc failure")
def test_malloc_failure(c):
    identity = c.callback(
        name="malloc_failure",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; return c;",
    )

    test_malloc_failures(
        c,
        b"hello world\0",
        b"hello world\0",
        identity,
    )


@suite.case("malloc failure empty string")
def test_malloc_failure_empty(c):
    identity = c.callback(
        name="malloc_failure_empty",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; return c;",
    )

    test_malloc_failures(
        c,
        b"\0",
        b"\0",
        identity,
    )


@suite.case("malloc failure binary data")
def test_malloc_failure_binary(c):
    identity = c.callback(
        name="malloc_failure_binary",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="(void)i; return c;",
    )

    test_malloc_failures(
        c,
        b"\x01\x02hello\xfe\xff\0",
        b"\x01\x02hello\xfe\xff\0",
        identity,
    )
