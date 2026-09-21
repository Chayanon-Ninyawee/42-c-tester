from framework import TestSuite

suite = TestSuite("ft_tolower")


def compare(c, argument, expected):
    test = c.include("libft.h", "ctype.h").code(f"""
        int ft = ft_tolower({argument});
        int libc = tolower({argument});

        TEST_VALUE("ft", "%d", ft);
        TEST_VALUE("libc", "%d", libc);

        return 0;
    """)

    test.value("ft").equals(
        str(expected),
        "Test ft_tolower() returned value",
    )

    test.value("libc").equals(
        str(expected),
        "Reference returned value from tolower() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("uppercase letters")
def test_uppercase(c):
    for argument in range(ord("A"), ord("Z") + 1):
        compare(c, argument, argument + 32)


@suite.case("lowercase letters")
def test_lowercase(c):
    for argument in range(ord("a"), ord("z") + 1):
        compare(c, argument, argument)


@suite.case("digits")
def test_digits(c):
    for argument in range(ord("0"), ord("9") + 1):
        compare(c, argument, argument)


@suite.case("punctuation")
def test_punctuation(c):
    for argument in [
        ord("!"),
        ord("@"),
        ord("["),
        ord("`"),
        ord("{"),
        ord("~"),
    ]:
        compare(c, argument, argument)


@suite.case("whitespace")
def test_whitespace(c):
    for argument in [
        ord(" "),
        ord("\t"),
        ord("\n"),
        ord("\r"),
    ]:
        compare(c, argument, argument)


@suite.case("negative value")
def test_negative(c):
    compare(c, -1, -1)


@suite.case("127")
def test_127(c):
    compare(c, 127, 127)


@suite.case("128")
def test_128(c):
    compare(c, 128, 128)


@suite.case("255")
def test_255(c):
    compare(c, 255, 255)
