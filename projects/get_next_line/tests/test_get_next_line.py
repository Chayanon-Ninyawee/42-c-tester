import os
import tempfile

from framework import TestSuite, c_bytes


suite = TestSuite("get_next_line")


def check_malloc(test, expected_lines=()):
    """Check malloc tracking and returned-line allocation sizes."""
    count = test.malloc.actual_count
    sizes = test.malloc_sizes

    if count != len(sizes):
        test.fail(
            f"malloc count mismatch: {count} calls, "
            f"{len(sizes)} sizes recorded"
        )

    if any(size <= 0 for size in sizes):
        test.fail(f"Unexpected malloc sizes: {sizes}")

    for line in expected_lines:
        required_size = len(line) + 1

        if not any(size >= required_size for size in sizes):
            test.fail(
                f"No allocation of at least {required_size} bytes "
                f"for a returned line; malloc sizes: {sizes}"
            )


def compare_pipe(
    c,
    input_data,
    expected_lines,
    use_stdin=False,
    buffer_size=42,
    eof_checks=1,
):
    """Test get_next_line using a pipe."""
    input_bytes = c_bytes(input_data) if input_data else "0x00"
    input_size = len(input_data)
    line_count = len(expected_lines)
    total_calls = line_count + eof_checks

    calls = []

    for index in range(total_calls):
        calls.append(
            f"""
        line = get_next_line(fd);
        TEST_VALUE("null_{index}", "%d", line == NULL);

        if (line != NULL)
            TEST_BUFFER("line_{index}", line, strlen(line));

        free(line);
"""
        )

    source = f"""
    int pipe_fds[2];
    int fd;
    char *line;
    unsigned char input[] = {{{input_bytes}}};

    if (pipe(pipe_fds) < 0)
        return 1;

    if ({input_size} > 0)
    {{
        if (write(pipe_fds[1], input, {input_size}) != {input_size})
            return 2;
    }}

    close(pipe_fds[1]);

    fd = pipe_fds[0];

    if ({1 if use_stdin else 0})
    {{
        if (dup2(pipe_fds[0], STDIN_FILENO) < 0)
            return 3;

        close(pipe_fds[0]);
        fd = STDIN_FILENO;
    }}

    {"".join(calls)}

    if (fd != STDIN_FILENO)
        close(fd);

    return 0;
    """

    test = c.include(
        "get_next_line.h",
        "unistd.h",
        "stdlib.h",
        "string.h",
    ).code(source)

    test.cflags(["-D", f"BUFFER_SIZE={buffer_size}"])

    for index, line in enumerate(expected_lines):
        test.value(f"null_{index}").equals(
            "0",
            f"Line {index} should not be NULL",
        )
        test.buffer(f"line_{index}").equals(
            line,
            f"Incorrect line {index}",
        )

    for index in range(line_count, total_calls):
        test.value(f"null_{index}").equals(
            "1",
            f"Call {index} should return NULL at EOF",
        )

    test.run()
    check_malloc(test, expected_lines)
    test.assert_now()


def test_malloc_failure(c, input_data, fail_at=0, buffer_size=42):
    """Test get_next_line when a malloc call fails."""
    input_bytes = c_bytes(input_data) if input_data else "0x00"
    input_size = len(input_data)

    test = c.include(
        "get_next_line.h",
        "unistd.h",
        "stdlib.h",
    ).code(
        f"""
        int pipe_fds[2];
        char *line;
        unsigned char input[] = {{{input_bytes}}};

        if (pipe(pipe_fds) < 0)
            return 1;

        if ({input_size} > 0)
        {{
            if (write(pipe_fds[1], input, {input_size}) != {input_size})
                return 2;
        }}

        close(pipe_fds[1]);

        line = get_next_line(pipe_fds[0]);

        TEST_VALUE("is_null", "%d", line == NULL);

        free(line);
        close(pipe_fds[0]);

        return 0;
        """
    )

    test.cflags(["-D", f"BUFFER_SIZE={buffer_size}"])
    test.malloc.fail_at(fail_at)
    test.value("is_null").equals(
        "1",
        "get_next_line should return NULL when malloc fails",
    )
    test.assert_now()


@suite.case("multiple lines")
def _(c):
    compare_pipe(
        c,
        b"hello\nworld\n42\n",
        [b"hello\n", b"world\n", b"42\n"],
    )


@suite.case("final line without newline")
def _(c):
    compare_pipe(
        c,
        b"hello\nworld",
        [b"hello\n", b"world"],
    )


@suite.case("empty input")
def _(c):
    compare_pipe(c, b"", [])


@suite.case("consecutive newlines")
def _(c):
    compare_pipe(
        c,
        b"\n\n\n",
        [b"\n", b"\n", b"\n"],
    )


@suite.case("single character")
def _(c):
    compare_pipe(c, b"a", [b"a"])


@suite.case("single newline")
def _(c):
    compare_pipe(c, b"\n", [b"\n"])


@suite.case("one empty line followed by text")
def _(c):
    compare_pipe(
        c,
        b"\nhello\n",
        [b"\n", b"hello\n"],
    )


@suite.case("text followed by multiple empty lines")
def _(c):
    compare_pipe(
        c,
        b"hello\n\n\n",
        [b"hello\n", b"\n", b"\n"],
    )


@suite.case("no newline at all")
def _(c):
    compare_pipe(c, b"hello", [b"hello"])


@suite.case("newline at the end")
def _(c):
    compare_pipe(
        c,
        b"hello\n",
        [b"hello\n"],
    )


@suite.case("CRLF input")
def _(c):
    compare_pipe(
        c,
        b"hello\r\nworld\r\n",
        [b"hello\r\n", b"world\r\n"],
    )


@suite.case("long line")
def _(c):
    line = b"a" * 2048 + b"\n"
    compare_pipe(c, line, [line])


@suite.case("multiple long lines")
def _(c):
    first = b"a" * 2048 + b"\n"
    second = b"b" * 4096 + b"\n"
    third = b"c" * 1024

    compare_pipe(
        c,
        first + second + third,
        [first, second, third],
    )


@suite.case("large input without newline")
def _(c):
    line = b"a" * 16384
    compare_pipe(c, line, [line])


@suite.case("buffer size 1")
def _(c):
    compare_pipe(
        c,
        b"hello\nworld\n",
        [b"hello\n", b"world\n"],
        buffer_size=1,
    )


@suite.case("buffer size 2")
def _(c):
    compare_pipe(
        c,
        b"hello\nworld\n",
        [b"hello\n", b"world\n"],
        buffer_size=2,
    )


@suite.case("buffer size 7")
def _(c):
    compare_pipe(
        c,
        b"hello\nworld\n",
        [b"hello\n", b"world\n"],
        buffer_size=7,
    )


@suite.case("buffer size 42")
def _(c):
    compare_pipe(
        c,
        b"hello\nworld\n",
        [b"hello\n", b"world\n"],
        buffer_size=42,
    )


@suite.case("buffer size 9999")
def _(c):
    compare_pipe(
        c,
        b"hello\nworld\n",
        [b"hello\n", b"world\n"],
        buffer_size=9999,
    )


@suite.case("newline at buffer boundary")
def _(c):
    compare_pipe(
        c,
        b"abcd\nxyz",
        [b"abcd\n", b"xyz"],
        buffer_size=5,
    )


@suite.case("newline just after buffer boundary")
def _(c):
    compare_pipe(
        c,
        b"abcde\nxyz",
        [b"abcde\n", b"xyz"],
        buffer_size=5,
    )


@suite.case("line shorter than buffer")
def _(c):
    compare_pipe(
        c,
        b"abc\n",
        [b"abc\n"],
        buffer_size=10,
    )


@suite.case("line exactly buffer size")
def _(c):
    compare_pipe(
        c,
        b"abcd\n",
        [b"abcd\n"],
        buffer_size=5,
    )


@suite.case("line longer than buffer")
def _(c):
    compare_pipe(
        c,
        b"abcdefghij\n",
        [b"abcdefghij\n"],
        buffer_size=5,
    )


@suite.case("multiple lines in one buffer")
def _(c):
    compare_pipe(
        c,
        b"a\nb\nc\n",
        [b"a\n", b"b\n", b"c\n"],
        buffer_size=42,
    )


@suite.case("repeated EOF calls")
def _(c):
    compare_pipe(
        c,
        b"hello\n",
        [b"hello\n"],
        eof_checks=5,
    )


@suite.case("read from standard input")
def _(c):
    compare_pipe(
        c,
        b"stdin\nsecond line\n",
        [b"stdin\n", b"second line\n"],
        use_stdin=True,
    )


@suite.case("read from regular file")
def _(c):
    input_data = b"first line\nsecond line\nlast line"
    input_bytes = c_bytes(input_data)

    test = c.include(
        "get_next_line.h",
        "unistd.h",
        "fcntl.h",
        "stdlib.h",
        "string.h",
    ).code(
        f"""
        char path[] = "/tmp/gnl_test_XXXXXX";
        unsigned char input[] = {{{input_bytes}}};
        int fd;
        char *line;

        fd = mkstemp(path);

        if (fd < 0)
            return 1;

        if (write(fd, input, {len(input_data)}) != {len(input_data)})
            return 2;

        if (lseek(fd, 0, SEEK_SET) < 0)
            return 3;

        line = get_next_line(fd);
        TEST_VALUE("null_0", "%d", line == NULL);
        if (line != NULL)
            TEST_BUFFER("line_0", line, strlen(line));
        free(line);

        line = get_next_line(fd);
        TEST_VALUE("null_1", "%d", line == NULL);
        if (line != NULL)
            TEST_BUFFER("line_1", line, strlen(line));
        free(line);

        line = get_next_line(fd);
        TEST_VALUE("null_2", "%d", line == NULL);
        if (line != NULL)
            TEST_BUFFER("line_2", line, strlen(line));
        free(line);

        line = get_next_line(fd);
        TEST_VALUE("null_3", "%d", line == NULL);
        free(line);

        close(fd);
        unlink(path);

        return 0;
        """
    )

    test.cflags(["-D", "BUFFER_SIZE=7"])
    test.value("null_0").equals("0")
    test.buffer("line_0").equals(b"first line\n")
    test.value("null_1").equals("0")
    test.buffer("line_1").equals(b"second line\n")
    test.value("null_2").equals("0")
    test.buffer("line_2").equals(b"last line")
    test.value("null_3").equals("1")
    check_malloc(
        test,
        [b"first line\n", b"second line\n", b"last line"],
    )
    test.assert_now()


@suite.case("invalid file descriptor")
def _(c):
    test = c.include(
        "get_next_line.h",
        "stdlib.h",
    ).code(
        """
        char *line;

        line = get_next_line(-1);
        TEST_VALUE("is_null", "%d", line == NULL);
        free(line);

        return 0;
        """
    )

    test.value("is_null").equals("1")
    test.assert_now()


@suite.case("closed file descriptor")
def _(c):
    test = c.include(
        "get_next_line.h",
        "unistd.h",
        "stdlib.h",
    ).code(
        """
        int pipe_fds[2];
        char *line;

        if (pipe(pipe_fds) < 0)
            return 1;

        close(pipe_fds[0]);
        close(pipe_fds[1]);

        line = get_next_line(pipe_fds[0]);
        TEST_VALUE("is_null", "%d", line == NULL);
        free(line);

        return 0;
        """
    )

    test.value("is_null").equals("1")
    test.assert_now()


@suite.case("malloc failure on first allocation")
def _(c):
    test_malloc_failure(c, b"hello\n", fail_at=0)


@suite.case("malloc failure with long line")
def _(c):
    test_malloc_failure(
        c,
        b"a" * 2048 + b"\n",
        fail_at=0,
    )


@suite.case("malloc failure with buffer size 1")
def _(c):
    test_malloc_failure(
        c,
        b"hello\n",
        fail_at=0,
        buffer_size=1,
    )
