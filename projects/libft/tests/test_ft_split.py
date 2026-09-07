from framework import Assert, Capture, TestSuite

suite = TestSuite("ft_split")


def compare(c, original, delimiter, expected):
    ft_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s",
    )

    ft = c.ft_split(
        ft_s,
        delimiter,
    )

    capture = Capture.pointer_array(len(expected) + 1)

    for word in expected:
        capture.child(Capture.buffer(len(word)))

    capture.child(Capture.pointer_raw())

    ft.capture_return(capture)
    ft.run()

    ft.malloc_count_equals(
        len(expected) + 1,
        "Test malloc count",
    )
    ft.malloc_size_equals(
        0,
        (len(expected) + 1) * 8,
        "Test malloc size",
    )
    for i in range(len(expected)):
        ft.malloc_size_equals(
            i + 1,
            len(expected[i]),
            "Test malloc size",
        )
    ft.buffer_equals(
        ft_s,
        original,
        "Source buffer was modified",
    )

    assert_capture = Assert.pointer_array()

    for word in expected:
        assert_capture.child(Assert.buffer_equals(word))

    assert_capture.child(
        Assert.is_null_pointer("returned char * array is not NULL terminated")
    )

    ft.assert_return(
        assert_capture,
        "Test return value",
    )

    ft.assert_now()


def test_malloc_failures(c, original, delimiter, expected):
    c.malloc.reset()

    ft_s = c.buffer(
        original,
        size=len(original),
        type="char",
        name="ft_s",
    )

    # First run must succeed so we can determine how many allocations
    # the function normally performs.
    ft = c.ft_split(
        ft_s,
        delimiter,
    )

    capture = Capture.pointer_array(len(expected) + 1)

    for word in expected:
        capture.child(Capture.buffer(len(word)))

    capture.child(Capture.pointer_raw())

    ft.capture_return(capture)
    ft.run()

    ft.malloc_count_equals(
        len(expected) + 1,
        "Test malloc count",
    )
    ft.malloc_size_equals(
        0,
        (len(expected) + 1) * 8,
        "Test malloc size",
    )
    for i in range(len(expected)):
        ft.malloc_size_equals(
            i + 1,
            len(expected[i]),
            "Test malloc size",
        )
    ft.buffer_equals(
        ft_s,
        original,
        "Source buffer was modified",
    )

    assert_capture = Assert.pointer_array()

    for word in expected:
        assert_capture.child(Assert.buffer_equals(word))

    assert_capture.child(
        Assert.is_null_pointer("returned char * array is not NULL terminated")
    )

    ft.assert_return(
        assert_capture,
        "Initial allocation test",
    )
    ft.assert_now()

    malloc_count = ft.malloc_count

    # Fail every allocation individually.
    for fail_at in range(malloc_count):
        c.malloc.fail_at(fail_at)

        ft = c.ft_split(
            ft_s,
            delimiter,
        )

        # On allocation failure, ft_split should return NULL.
        ft.capture_return(Capture.pointer_raw())

        ft.run()

        ft.buffer_equals(
            ft_s,
            original,
            "Source buffer was modified",
        )

        ft.assert_return(
            Assert.is_null_pointer(f"malloc failure at call {fail_at}"),
            f"malloc failure at call {fail_at}",
        )

        ft.assert_now()

    c.malloc.reset()


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
