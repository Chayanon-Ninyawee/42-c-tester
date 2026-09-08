from framework import TestSuite

suite = TestSuite("ft_striteri")


def compare(c, original, expected, callback):
    ft_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s",
    )

    ft = c.ft_striteri(
        ft_s,
        callback,
    )

    ft.run()

    ft.buffer_equals(
        ft_s,
        expected,
        "String was not modified correctly",
    )
    ft.assert_now()


@suite.case("identity")
def test_identity(c):
    identity = c.callback(
        name="identity",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="(void)i; (void)c;",
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
        name="empty",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="(void)i; (void)c;",
    )

    compare(
        c,
        b"\0",
        b"\0",
        identity,
    )


@suite.case("modify character")
def test_modify_character(c):
    uppercase = c.callback(
        name="uppercase",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            (void)i;
            if (*c >= 'a' && *c <= 'z')
                *c -= 'a' - 'A';
        """,
    )

    compare(
        c,
        b"hello world\0",
        b"HELLO WORLD\0",
        uppercase,
    )


@suite.case("index is passed correctly")
def test_index(c):
    char_index = c.callback(
        name="char_index",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            *c = '0' + i;
        """,
    )

    compare(
        c,
        b"abcdef\0",
        b"012345\0",
        char_index,
    )


@suite.case("character is passed by address")
def test_character_address(c):
    increment = c.callback(
        name="increment",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            (void)i;
            (*c)++;
        """,
    )

    compare(
        c,
        b"abcdef\0",
        b"bcdefg\0",
        increment,
    )


@suite.case("index and character")
def test_index_and_character(c):
    transform = c.callback(
        name="index_character",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            *c += i;
        """,
    )

    compare(
        c,
        b"abcde\0",
        b"acegi\0",
        transform,
    )


@suite.case("index based transformation")
def test_index_transformation(c):
    transform = c.callback(
        name="index_transform",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            if (i % 2 == 0)
                *c += 1;
            else
                *c -= 1;
        """,
    )

    compare(
        c,
        b"abcdef\0",
        b"badcfe\0",
        transform,
    )


@suite.case("character based transformation")
def test_character_transformation(c):
    transform = c.callback(
        name="character_transform",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            (void)i;

            if (*c >= 'a' && *c <= 'z')
                *c = *c - 'a' + 'A';
            else if (*c >= 'A' && *c <= 'Z')
                *c = *c - 'A' + 'a';
        """,
    )

    compare(
        c,
        b"Hello WORLD 123!\0",
        b"hELLO world 123!\0",
        transform,
    )


@suite.case("conditional index")
def test_conditional_index(c):
    transform = c.callback(
        name="conditional_index",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            if (i < 3)
                *c += 10;
            else if (i % 2 == 0)
                *c -= 2;
            else
                *c += 2;
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
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            int value;

            value = *c;
            value += i;
            value *= 2;
            value -= 3;

            *c = value;
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
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            (void)i;

            if (*c >= '0' && *c <= '9')
                *c = 'D';
            else if (*c >= 'a' && *c <= 'z')
                *c = 'L';
            else if (*c >= 'A' && *c <= 'Z')
                *c = 'U';
            else if (*c == ' ')
                *c = 'S';
            else
                *c = '?';
        """,
    )

    compare(
        c,
        b"aZ5 !b2C\0",
        b"LUDS?LDU\0",
        classify,
    )


@suite.case("same callback result")
def test_same_result(c):
    star = c.callback(
        name="star",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            (void)i;
            *c = '*';
        """,
    )

    compare(
        c,
        b"hello world\0",
        b"***********\0",
        star,
    )


@suite.case("special characters")
def test_special(c):
    identity = c.callback(
        name="special",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="(void)i; (void)c;",
    )

    compare(
        c,
        b"!@#$%^&*()[]{};:'\",.<>/?\0",
        b"!@#$%^&*()[]{};:'\",.<>/?\0",
        identity,
    )


@suite.case("spaces and whitespace")
def test_whitespace(c):
    transform = c.callback(
        name="whitespace",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            (void)i;

            if (*c == ' ')
                *c = '_';
            else if (*c == '\\t')
                *c = 'T';
            else if (*c == '\\n')
                *c = 'N';
            else if (*c == '\\r')
                *c = 'R';
        """,
    )

    compare(
        c,
        b" \t\n\rhello world\t\n\0",
        b"_TNRhello_worldTN\0",
        transform,
    )


@suite.case("binary data")
def test_binary(c):
    increment = c.callback(
        name="binary",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            *c += i;
        """,
    )

    compare(
        c,
        b"\x01\x02\x03hello\x04\x05\x06\0",
        b"\x01\x03\x05kiqrv\x0c\x0e\x10\0",
        increment,
    )


@suite.case("high bytes")
def test_high_bytes(c):
    identity = c.callback(
        name="high_bytes",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="(void)i; (void)c;",
    )

    compare(
        c,
        b"\x80\x81\xfe\xffhello\0",
        b"\x80\x81\xfe\xffhello\0",
        identity,
    )


@suite.case("large string")
def test_large(c):
    transform = c.callback(
        name="large",
        returns="void",
        args=[
            ("unsigned int", "i"),
            ("char *", "c"),
        ],
        body="""
            (void)i;
            *c ^= 0x20;
        """,
    )

    original = b"HelloWorld" * 1000 + b"\0"
    expected = b"hELLOwORLD" * 1000 + b"\0"

    compare(
        c,
        original,
        expected,
        transform,
    )
