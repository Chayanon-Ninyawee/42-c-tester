from framework import TestSuite, c_bytes

suite = TestSuite("ft_striteri")


def compare(c, original, expected, callback_name, callback_body):
    original_c = c_bytes(original)

    test = (
        c.include(
            "libft.h",
        )
        .function(f"""
        static void {callback_name}(unsigned int i, char *c)
        {{
            {callback_body}
        }}
        """)
        .code(f"""
        unsigned char ft_s[] = {{{original_c}}};

        ft_striteri(
            (char *)ft_s,
            {callback_name}
        );

        TEST_BUFFER(
            "ft_s",
            ft_s,
            sizeof(ft_s)
        );

        return 0;
        """)
    )

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.buffer("ft_s").equals(
        expected,
        "String was not modified correctly",
    )

    test.assert_now()


@suite.case("identity")
def test_identity(c):
    compare(
        c,
        b"hello world\0",
        b"hello world\0",
        "identity",
        """
        (void)i;
        (void)c;
        """,
    )


@suite.case("empty string")
def test_empty(c):
    compare(
        c,
        b"\0",
        b"\0",
        "empty",
        """
        (void)i;
        (void)c;
        """,
    )


@suite.case("modify character")
def test_modify_character(c):
    compare(
        c,
        b"hello world\0",
        b"HELLO WORLD\0",
        "uppercase",
        """
        (void)i;

        if (*c >= 'a' && *c <= 'z')
            *c -= 'a' - 'A';
        """,
    )


@suite.case("index is passed correctly")
def test_index(c):
    compare(
        c,
        b"abcdef\0",
        b"012345\0",
        "char_index",
        """
        *c = '0' + i;
        """,
    )


@suite.case("character is passed by address")
def test_character_address(c):
    compare(
        c,
        b"abcdef\0",
        b"bcdefg\0",
        "increment",
        """
        (void)i;
        (*c)++;
        """,
    )


@suite.case("index and character")
def test_index_and_character(c):
    compare(
        c,
        b"abcde\0",
        b"acegi\0",
        "index_character",
        """
        *c += i;
        """,
    )


@suite.case("index based transformation")
def test_index_transformation(c):
    compare(
        c,
        b"abcdef\0",
        b"badcfe\0",
        "index_transform",
        """
        if (i % 2 == 0)
            *c += 1;
        else
            *c -= 1;
        """,
    )


@suite.case("character based transformation")
def test_character_transformation(c):
    compare(
        c,
        b"Hello WORLD 123!\0",
        b"hELLO world 123!\0",
        "character_transform",
        """
        (void)i;

        if (*c >= 'a' && *c <= 'z')
            *c = *c - 'a' + 'A';
        else if (*c >= 'A' && *c <= 'Z')
            *c = *c - 'A' + 'a';
        """,
    )


@suite.case("conditional index")
def test_conditional_index(c):
    compare(
        c,
        b"abcdef\0",
        b"klmfch\0",
        "conditional_index",
        """
        if (i < 3)
            *c += 10;
        else if (i % 2 == 0)
            *c -= 2;
        else
            *c += 2;
        """,
    )


@suite.case("multiple operations")
def test_multiple_operations(c):
    compare(
        c,
        b"abcdef\0",
        b"\xbf\xc3\xc7\xcb\xcf\xd3\0",
        "multiple_operations",
        """
        int value;

        value = *c;
        value += i;
        value *= 2;
        value -= 3;

        *c = value;
        """,
    )


@suite.case("character classification")
def test_character_classification(c):
    compare(
        c,
        b"aZ5 !b2C\0",
        b"LUDS?LDU\0",
        "classify",
        """
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


@suite.case("same callback result")
def test_same_result(c):
    compare(
        c,
        b"hello world\0",
        b"***********\0",
        "star",
        """
        (void)i;
        *c = '*';
        """,
    )


@suite.case("special characters")
def test_special(c):
    compare(
        c,
        b"!@#$%^&*()[]{};:'\",.<>/?\0",
        b"!@#$%^&*()[]{};:'\",.<>/?\0",
        "special",
        """
        (void)i;
        (void)c;
        """,
    )


@suite.case("spaces and whitespace")
def test_whitespace(c):
    compare(
        c,
        b" \t\n\rhello world\t\n\0",
        b"_TNRhello_worldTN\0",
        "whitespace",
        """
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


@suite.case("binary data")
def test_binary(c):
    compare(
        c,
        b"\x01\x02\x03hello\x04\x05\x06\0",
        b"\x01\x03\x05kiqrv\x0c\x0e\x10\0",
        "binary",
        """
        *c += i;
        """,
    )


@suite.case("high bytes")
def test_high_bytes(c):
    compare(
        c,
        b"\x80\x81\xfe\xffhello\0",
        b"\x80\x81\xfe\xffhello\0",
        "high_bytes",
        """
        (void)i;
        (void)c;
        """,
    )


@suite.case("large string")
def test_large(c):
    original = b"HelloWorld" * 1000 + b"\0"
    expected = b"hELLOwORLD" * 1000 + b"\0"

    compare(
        c,
        original,
        expected,
        "large",
        """
        (void)i;
        *c ^= 0x20;
        """,
    )
