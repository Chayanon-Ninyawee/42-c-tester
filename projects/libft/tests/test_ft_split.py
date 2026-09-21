from framework import TestSuite, c_bytes

suite = TestSuite("ft_split")


def compare(c, original, delimiter, expected):
    original_c = c_bytes(original)

    buffer_reports = "\n".join(f"""
        TEST_BUFFER(
            "ft_result_{i}",
            ft[{i}],
            {len(word)}
        );
        """ for i, word in enumerate(expected))

    free_results = "\n".join(f"free(ft[{i}]);" for i in range(len(expected)))

    test = c.include("libft.h", "stdlib.h").code(f"""
        unsigned char ft_s[] = {{{original_c}}};

        char **ft = ft_split(
            (char *)ft_s,
            {delimiter}
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s",
            ft_s,
            sizeof(ft_s)
        );

        if (ft != NULL) {{
            {buffer_reports}

            int ft_is_terminated = (ft[{len(expected)}] == NULL);

            TEST_VALUE(
                "ft_is_terminated",
                "%d",
                ft_is_terminated
            );

            {free_results}
            free(ft);
        }}

        return 0;
    """)

    test.value("ft_is_null").equals(
        "0",
        "Test return value",
    )

    test.value("ft_is_terminated").equals(
        "1",
        "Returned char * array is not NULL terminated",
    )

    test.malloc.count(
        len(expected) + 1,
        "Test malloc count",
    )

    test.malloc.size(
        0,
        (len(expected) + 1) * 8,
        "Test malloc size",
    )

    for i, word in enumerate(expected):
        test.malloc.size(
            i + 1,
            len(word),
            "Test malloc size",
        )

        test.buffer(f"ft_result_{i}").equals(
            word,
            "Returned buffer mismatch",
        )

    test.buffer("ft_s").equals(
        original,
        "Source buffer was modified",
    )

    test.assert_now()


def test_malloc_failures(c, original, delimiter, expected):
    original_c = c_bytes(original)

    buffer_reports = "\n".join(f"""
        TEST_BUFFER(
            "ft_result_{i}",
            ft[{i}],
            {len(word)}
        );
        """ for i, word in enumerate(expected))

    free_results = "\n".join(f"free(ft[{i}]);" for i in range(len(expected)))

    test = c.include("libft.h", "stdlib.h").code(f"""
        unsigned char ft_s[] = {{{original_c}}};

        char **ft = ft_split(
            (char *)ft_s,
            {delimiter}
        );

        int ft_is_null = (ft == NULL);

        TEST_VALUE("ft_is_null", "%d", ft_is_null);

        TEST_BUFFER(
            "ft_s",
            ft_s,
            sizeof(ft_s)
        );

        if (ft != NULL) {{
            {buffer_reports}

            int ft_is_terminated = (ft[{len(expected)}] == NULL);

            TEST_VALUE(
                "ft_is_terminated",
                "%d",
                ft_is_terminated
            );

            {free_results}
            free(ft);
        }}

        return 0;
    """)

    test.value("ft_is_null").equals(
        "0",
        "Test return value",
    )

    test.value("ft_is_terminated").equals(
        "1",
        "Returned char * array is not NULL terminated",
    )

    test.malloc.count(
        len(expected) + 1,
        "Test malloc count",
    )

    test.malloc.size(
        0,
        (len(expected) + 1) * 8,
        "Test malloc size",
    )

    for i, word in enumerate(expected):
        test.malloc.size(
            i + 1,
            len(word),
            "Test malloc size",
        )

        test.buffer(f"ft_result_{i}").equals(
            word,
            "Returned buffer mismatch",
        )

    test.buffer("ft_s").equals(
        original,
        "Source buffer was modified",
    )

    test.assert_now()

    for fail_at in range(len(expected) + 1):
        test = c.include("libft.h").code(f"""
            unsigned char ft_s[] = {{{original_c}}};

            char **ft = ft_split(
                (char *)ft_s,
                {delimiter}
            );

            int ft_is_null = (ft == NULL);

            TEST_VALUE("ft_is_null", "%d", ft_is_null);

            TEST_BUFFER(
                "ft_s",
                ft_s,
                sizeof(ft_s)
            );

            return 0;
        """)

        test.malloc.fail_at(fail_at)

        test.value("ft_is_null").equals(
            "1",
            f"malloc failure at call {fail_at}",
        )

        test.buffer("ft_s").equals(
            original,
            "Source buffer was modified",
        )

        test.assert_now()


@suite.case("empty string")
def test_empty(c):
    compare(
        c,
        b"\0",
        ord(","),
        [],
    )


@suite.case("single word")
def test_single_word(c):
    compare(
        c,
        b"hello\0",
        ord(","),
        [b"hello\0"],
    )


@suite.case("two words")
def test_two_words(c):
    compare(
        c,
        b"hello,world\0",
        ord(","),
        [b"hello\0", b"world\0"],
    )


@suite.case("multiple words")
def test_multiple_words(c):
    compare(
        c,
        b"hello,world,test,string\0",
        ord(","),
        [
            b"hello\0",
            b"world\0",
            b"test\0",
            b"string\0",
        ],
    )


@suite.case("leading delimiters")
def test_leading_delimiters(c):
    compare(
        c,
        b",,,hello,world\0",
        ord(","),
        [
            b"hello\0",
            b"world\0",
        ],
    )


@suite.case("trailing delimiters")
def test_trailing_delimiters(c):
    compare(
        c,
        b"hello,world,,,\0",
        ord(","),
        [
            b"hello\0",
            b"world\0",
        ],
    )


@suite.case("consecutive delimiters")
def test_consecutive_delimiters(c):
    compare(
        c,
        b"hello,,,world\0",
        ord(","),
        [
            b"hello\0",
            b"world\0",
        ],
    )


@suite.case("only delimiters")
def test_only_delimiters(c):
    compare(
        c,
        b",,,,,\0",
        ord(","),
        [],
    )


@suite.case("spaces")
def test_spaces(c):
    compare(
        c,
        b"hello world test\0",
        ord(" "),
        [
            b"hello\0",
            b"world\0",
            b"test\0",
        ],
    )


@suite.case("special delimiter")
def test_special_delimiter(c):
    compare(
        c,
        b"hello.world.test\0",
        ord("."),
        [
            b"hello\0",
            b"world\0",
            b"test\0",
        ],
    )


@suite.case("delimiter not present")
def test_no_delimiter(c):
    compare(
        c,
        b"hello world\0",
        ord(","),
        [
            b"hello world\0",
        ],
    )


@suite.case("single character words")
def test_single_character_words(c):
    compare(
        c,
        b"a,b,c,d,e\0",
        ord(","),
        [
            b"a\0",
            b"b\0",
            b"c\0",
            b"d\0",
            b"e\0",
        ],
    )


@suite.case("long words")
def test_long_words(c):
    compare(
        c,
        b"0123456789" * 50 + b"," + b"abcdefghijklmnopqrstuvwxyz" * 50 + b"\0",
        ord(","),
        [
            b"0123456789" * 50 + b"\0",
            b"abcdefghijklmnopqrstuvwxyz" * 50 + b"\0",
        ],
    )


@suite.case("binary characters")
def test_binary(c):
    compare(
        c,
        b"hello\x01world\x01test\0",
        1,
        [
            b"hello\0",
            b"world\0",
            b"test\0",
        ],
    )


@suite.case("high byte delimiter")
def test_high_byte(c):
    compare(
        c,
        b"hello\xffworld\xfftest\0",
        255,
        [
            b"hello\0",
            b"world\0",
            b"test\0",
        ],
    )


@suite.case("malloc failure 1")
def test_malloc_failure_1(c):
    test_malloc_failures(
        c,
        b"hello,world\0",
        ord(","),
        [
            b"hello\0",
            b"world\0",
        ],
    )


@suite.case("malloc failure 2")
def test_malloc_failure_2(c):
    test_malloc_failures(
        c,
        b"hello,,,world,test,string\0",
        ord(","),
        [
            b"hello\0",
            b"world\0",
            b"test\0",
            b"string\0",
        ],
    )


@suite.case("malloc failure many words")
def test_malloc_failure_many(c):
    test_malloc_failures(
        c,
        b"a,b,c,d,e,f,g,h,i,j,k,l,m,n,o,p,q,r,s,t\0",
        ord(","),
        [
            b"a\0",
            b"b\0",
            b"c\0",
            b"d\0",
            b"e\0",
            b"f\0",
            b"g\0",
            b"h\0",
            b"i\0",
            b"j\0",
            b"k\0",
            b"l\0",
            b"m\0",
            b"n\0",
            b"o\0",
            b"p\0",
            b"q\0",
            b"r\0",
            b"s\0",
            b"t\0",
        ],
    )
