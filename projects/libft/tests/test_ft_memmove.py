from framework import TestSuite, c_bytes

suite = TestSuite("ft_memmove")


def compare(c, dest_original, src_original, expected, count):
    dest_c = c_bytes(dest_original)
    src_c = c_bytes(src_original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_dest[] = {{{dest_c}}};
        unsigned char ft_src[] = {{{src_c}}};

        unsigned char libc_dest[] = {{{dest_c}}};
        unsigned char libc_src[] = {{{src_c}}};

        void *ft_result = ft_memmove(
            ft_dest,
            ft_src,
            {count}
        );

        void *libc_result = memmove(
            libc_dest,
            libc_src,
            {count}
        );

        int ft_pointer_ok = (ft_result == ft_dest);
        int libc_pointer_ok = (libc_result == libc_dest);

        TEST_VALUE("ft_pointer", "%d", ft_pointer_ok);
        TEST_VALUE("libc_pointer", "%d", libc_pointer_ok);

        TEST_BUFFER(
            "ft_dest",
            ft_dest,
            sizeof(ft_dest)
        );

        TEST_BUFFER(
            "ft_src",
            ft_src,
            sizeof(ft_src)
        );

        TEST_BUFFER(
            "libc_dest",
            libc_dest,
            sizeof(libc_dest)
        );

        TEST_BUFFER(
            "libc_src",
            libc_src,
            sizeof(libc_src)
        );

        return 0;
    """)

    test.value("ft_pointer").equals(
        "1",
        "Test returned pointer",
    )

    test.value("libc_pointer").equals(
        "1",
        "Test returned pointer from memmove() from libc",
    ).reference()

    test.buffer("ft_dest").equals(
        expected,
        "Test destination buffer",
    )

    test.buffer("libc_dest").equals(
        expected,
        "Test destination buffer from memmove() from libc",
    ).reference()

    test.buffer("ft_src").equals(
        src_original,
        "Test that source buffer was modified",
    )

    test.buffer("libc_src").equals(
        src_original,
        "Test that source buffer was modified by memmove() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("copies entire buffer")
def test_all_bytes(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello12345",
        b"hello12345",
        "10",
    )


@suite.case("copies first 5 bytes")
def test_partial(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello12345",
        b"helloXXXXX",
        "5",
    )


@suite.case("copies one byte")
def test_one_byte(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello12345",
        b"hXXXXXXXXX",
        "1",
    )


@suite.case("zero bytes does nothing")
def test_zero(c):
    compare(
        c,
        b"XXXXXXXXXX",
        b"hello12345",
        b"XXXXXXXXXX",
        "0",
    )


@suite.case("works with binary data")
def test_binary(c):
    compare(
        c,
        b"\x00\x00\x00\x00\x00",
        b"\xff\x01\x80\x00\x7f",
        b"\xff\x01\x80\x00\x7f",
        "5",
    )


@suite.case("preserves bytes after n")
def test_boundary(c):
    compare(
        c,
        b"0123456789",
        b"abcdefghij",
        b"abcd456789",
        "4",
    )


@suite.case("copies between independent buffers")
def test_different_buffers(c):
    compare(
        c,
        b"abcdefghij",
        b"1234567890",
        b"1234567hij",
        "7",
    )


@suite.case("handles overlapping buffers forward")
def test_overlap_forward(c):
    original = b"123456789\x00"
    expected = b"121234567\x00"

    original_c = c_bytes(original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_buffer[] = {{{original_c}}};
        unsigned char libc_buffer[] = {{{original_c}}};

        void *ft_result = ft_memmove(
            ft_buffer + 2,
            ft_buffer,
            7
        );

        void *libc_result = memmove(
            libc_buffer + 2,
            libc_buffer,
            7
        );

        int ft_pointer_ok = (ft_result == ft_buffer + 2);
        int libc_pointer_ok = (libc_result == libc_buffer + 2);

        TEST_VALUE("ft_pointer", "%d", ft_pointer_ok);
        TEST_VALUE("libc_pointer", "%d", libc_pointer_ok);

        TEST_BUFFER(
            "ft_buffer",
            ft_buffer,
            sizeof(ft_buffer)
        );

        TEST_BUFFER(
            "libc_buffer",
            libc_buffer,
            sizeof(libc_buffer)
        );

        return 0;
    """)

    test.value("ft_pointer").equals(
        "1",
        "Test returned pointer",
    )

    test.value("libc_pointer").equals(
        "1",
        "Test returned pointer from memmove() from libc",
    ).reference()

    test.buffer("ft_buffer").equals(
        expected,
        "Test buffer contents",
    )

    test.buffer("libc_buffer").equals(
        expected,
        "Test buffer contents from memmove() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("handles overlapping buffers backward")
def test_overlap_backward(c):
    original = b"123456789\x00"
    expected = b"345678989\x00"

    original_c = c_bytes(original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_buffer[] = {{{original_c}}};
        unsigned char libc_buffer[] = {{{original_c}}};

        void *ft_result = ft_memmove(
            ft_buffer,
            ft_buffer + 2,
            7
        );

        void *libc_result = memmove(
            libc_buffer,
            libc_buffer + 2,
            7
        );

        int ft_pointer_ok = (ft_result == ft_buffer);
        int libc_pointer_ok = (libc_result == libc_buffer);

        TEST_VALUE("ft_pointer", "%d", ft_pointer_ok);
        TEST_VALUE("libc_pointer", "%d", libc_pointer_ok);

        TEST_BUFFER(
            "ft_buffer",
            ft_buffer,
            sizeof(ft_buffer)
        );

        TEST_BUFFER(
            "libc_buffer",
            libc_buffer,
            sizeof(libc_buffer)
        );

        return 0;
    """)

    test.value("ft_pointer").equals(
        "1",
        "Test returned pointer",
    )

    test.value("libc_pointer").equals(
        "1",
        "Test returned pointer from memmove() from libc",
    ).reference()

    test.buffer("ft_buffer").equals(
        expected,
        "Test buffer contents",
    )

    test.buffer("libc_buffer").equals(
        expected,
        "Test buffer contents from memmove() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("handles large overlapping buffers forward")
def test_large_overlap_forward(c):
    pattern = (
        b"0123456789"
        b"abcdefghij"
        b"KLMNOPQRST"
        b"uvwxyzABCD"
        b"EFGHIJKLMN"
        b"OPQRSTUVWX"
        b"YZ01234567"
        b"89!@#$%^&*"
        b"()_+-=[]{}"
        b"<>?/.,:;"
    )

    original = pattern * 20
    offset = 200
    count = 1600

    expected = original[:offset] + original[:count] + original[offset + count :]

    original_c = c_bytes(original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_buffer[] = {{{original_c}}};
        unsigned char libc_buffer[] = {{{original_c}}};

        void *ft_result = ft_memmove(
            ft_buffer + {offset},
            ft_buffer,
            {count}
        );

        void *libc_result = memmove(
            libc_buffer + {offset},
            libc_buffer,
            {count}
        );

        int ft_pointer_ok = (ft_result == ft_buffer + {offset});
        int libc_pointer_ok = (libc_result == libc_buffer + {offset});

        TEST_VALUE("ft_pointer", "%d", ft_pointer_ok);
        TEST_VALUE("libc_pointer", "%d", libc_pointer_ok);

        TEST_BUFFER(
            "ft_buffer",
            ft_buffer,
            sizeof(ft_buffer)
        );

        TEST_BUFFER(
            "libc_buffer",
            libc_buffer,
            sizeof(libc_buffer)
        );

        return 0;
    """)

    test.value("ft_pointer").equals(
        "1",
        "Test returned pointer",
    )

    test.value("libc_pointer").equals(
        "1",
        "Test returned pointer from memmove() from libc",
    ).reference()

    test.buffer("ft_buffer").equals(
        expected,
        "Test buffer contents",
    )

    test.buffer("libc_buffer").equals(
        expected,
        "Test buffer contents from memmove() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()


@suite.case("handles large overlapping buffers backward")
def test_large_overlap_backward(c):
    pattern = (
        b"0123456789"
        b"abcdefghij"
        b"KLMNOPQRST"
        b"uvwxyzABCD"
        b"EFGHIJKLMN"
        b"OPQRSTUVWX"
        b"YZ01234567"
        b"89!@#$%^&*"
        b"()_+-=[]{}"
        b"<>?/.,:;"
    )

    original = pattern * 20
    offset = 200
    count = 1600

    expected = original[offset : offset + count] + original[count:]

    original_c = c_bytes(original)

    test = c.include("libft.h", "string.h").code(f"""
        unsigned char ft_buffer[] = {{{original_c}}};
        unsigned char libc_buffer[] = {{{original_c}}};

        void *ft_result = ft_memmove(
            ft_buffer,
            ft_buffer + {offset},
            {count}
        );

        void *libc_result = memmove(
            libc_buffer,
            libc_buffer + {offset},
            {count}
        );

        int ft_pointer_ok = (ft_result == ft_buffer);
        int libc_pointer_ok = (libc_result == libc_buffer);

        TEST_VALUE("ft_pointer", "%d", ft_pointer_ok);
        TEST_VALUE("libc_pointer", "%d", libc_pointer_ok);

        TEST_BUFFER(
            "ft_buffer",
            ft_buffer,
            sizeof(ft_buffer)
        );

        TEST_BUFFER(
            "libc_buffer",
            libc_buffer,
            sizeof(libc_buffer)
        );

        return 0;
    """)

    test.value("ft_pointer").equals(
        "1",
        "Test returned pointer",
    )

    test.value("libc_pointer").equals(
        "1",
        "Test returned pointer from memmove() from libc",
    ).reference()

    test.buffer("ft_buffer").equals(
        expected,
        "Test buffer contents",
    )

    test.buffer("libc_buffer").equals(
        expected,
        "Test buffer contents from memmove() from libc",
    ).reference()

    test.malloc.count(
        0,
        "Test malloc count",
    )

    test.assert_now()
