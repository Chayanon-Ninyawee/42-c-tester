# 42 C Testing Framework

A Python-based testing framework for testing C functions in 42 projects.

The framework generates small C test programs, compiles them against the student's project, executes them, and exposes the results through a Python API.

It is designed primarily for testing functions such as those found in `libft`, but can also be used for other C projects.

______________________________________________________________________

# Table of Contents

<!-- toc -->

- [Features](#features)
- [Basic Usage](#basic-usage)
- [Test Suites](#test-suites)
- [Writing Tests](#writing-tests)
  - [C Code](#c-code)
  - [Standard Output](#standard-output)
  - [Return Values](#return-values)
  - [File Descriptors](#file-descriptors)
  - [Values](#values)
  - [Buffers](#buffers)
- [Assertions](#assertions)
  - [`equals()`](#equals)
  - [`reference()`](#reference)
  - [`assert_now()`](#assert_now)
- [Test-Owned C Code](#test-owned-c-code)
  - [Variables](#variables)
  - [Helper Functions](#helper-functions)
  - [Includes](#includes)
- [Malloc Testing](#malloc-testing)
  - [Malloc Count](#malloc-count)
  - [Malloc Size](#malloc-size)
- [Simulating Malloc Failures](#simulating-malloc-failures)
- [AddressSanitizer](#addresssanitizer)
- [Debug Mode](#debug-mode)
- [Test Lifecycle](#test-lifecycle)
- [Examples](#examples)
  - [`ft_strlen`](#ft_strlen)
  - [`ft_memcpy`](#ft_memcpy)
  - [`ft_lstmap`](#ft_lstmap)
- [Generated C](#generated-c)
- [Temporary Files](#temporary-files)
- [Project Configuration](#project-configuration)
  - [Make](#make)
  - [Direct Compiler Builds](#direct-compiler-builds)
  - [Project Includes](#project-includes)
  - [Compiler Flags](#compiler-flags)
  - [Libraries](#libraries)
- [Current Limitations](#current-limitations)
  - [Function Pointers](#function-pointers)
  - [C Type Compatibility](#c-type-compatibility)
- [API Summary](#api-summary)
  - [`TestSuite`](#testsuite)
  - [`CContext`](#ccontext)
    - [`c.code()`](#ccode)
    - [`c.include()`](#cinclude)
    - [`c.function()`](#cfunction)
  - [`CCode`](#ccode)
  - [`CCodeBuilder`](#ccodebuilder)
  - [Return Value](#return-value)
  - [Standard Output](#standard-output-1)
  - [File Descriptors](#file-descriptors-1)
  - [Values](#values-1)
  - [Buffers](#buffers-1)
  - [Malloc](#malloc)
- [Design Notes](#design-notes)
- [Pointer Ownership](#pointer-ownership)
  - [Test-owned memory](#test-owned-memory)
  - [Function-owned memory](#function-owned-memory)
- [Debugging Failed Tests](#debugging-failed-tests)

<!-- tocstop -->

______________________________________________________________________

# Features

- Write C tests directly from Python.
- Generate complete C test programs automatically.
- Test return values.
- Test standard output.
- Capture arbitrary file descriptors.
- Test and compare buffers.
- Report named values from generated C code.
- Create test-owned C variables.
- Add file-scope helper functions to generated tests.
- Test callbacks and function-pointer arguments.
- Check `malloc()` call counts.
- Check individual allocation sizes.
- Simulate `malloc()` failures.
- Run tests with AddressSanitizer.
- Optionally run generated test programs under a debugger.
- Configure project-specific headers, libraries, compiler flags, and build commands.
- Detect memory leaks and invalid memory accesses through AddressSanitizer.
- Keep test code close to the C being tested instead of hiding behavior behind large Python abstractions.

______________________________________________________________________

# Basic Usage

A test suite is created with `TestSuite`:

```python
from framework import TestSuite

suite = TestSuite("ft_strlen")
```

A test receives a `CContext`:

```python
@suite.case("basic")
def test_basic(c):
    test = c.code("""
        char *str = "hello";

        TEST_VALUE(
            "length",
            "%zu",
            ft_strlen(str)
        );
    """)

    test.value("length").equals(
        "5",
        "Incorrect string length",
    )

    test.assert_now()
```

The Python code generates a C test program, compiles it against the student's project, runs it, and checks the reported results.

Tests are normally organized into cases:

```python
@suite.case("empty")
def test_empty(c):
    ...

@suite.case("basic")
def test_basic(c):
    ...

@suite.case("long string")
def test_long(c):
    ...
```

______________________________________________________________________

# Test Suites

A `TestSuite` groups all tests for one function or feature.

```python
from framework import TestSuite

suite = TestSuite("ft_strlen")
```

Each test case is registered with:

```python
@suite.case("case name")
def test_name(c):
    ...
```

The case name is displayed when the test suite runs:

```text
ft_strlen
  [PASS] empty
  [PASS] basic
  [PASS] long string
```

A suite can contain as many cases as needed.

This makes it possible to test different properties separately instead of putting every check into one large test.

______________________________________________________________________

# Writing Tests

## C Code

The main way to create a test is `c.code()`.

```python
test = c.code("""
    int result = ft_strlen("hello");

    TEST_VALUE(
        "result",
        "%d",
        result
    );
""")
```

`c.code()` contains C code that is placed inside the generated test function.

The code can use functions from the student's project normally:

```python
test = c.code("""
    char buffer[20];

    ft_memset(buffer, 'A', 10);

    TEST_BUFFER(
        "buffer",
        buffer,
        10
    );
""")
```

The C code is not executed when `c.code()` is called. It becomes part of the generated test program and is executed when `assert_now()` runs.

______________________________________________________________________

## Standard Output

Standard output can be captured with:

```python
test = c.code("""
    ft_putstr_fd("hello", 1);
""")

test.stdout().equals(
    b"hello",
    "Incorrect output",
)

test.assert_now()
```

The captured output is returned as bytes.

For example:

```python
test.stdout().equals(b"hello\n")
```

checks the exact output, including newlines.

______________________________________________________________________

## Return Values

The return value of the generated test code can be checked with:

```python
test = c.code("""
    return 42;
""")

test.return_value().equals(
    42,
    "Incorrect return value",
)

test.assert_now()
```

The `return` statement in the generated C test represents the return value of the test code.

It is separate from the process exit status used internally by the test runner.

Multiple assertions can be attached to one test:

```python
test = c.code("""
    write(3, "hello", 5);
    write(4, "world", 5);

    return 42;
""")

test.fd(3).equals(b"hello")
test.fd(4).equals(b"world")
test.return_value().equals(42)

test.assert_now()
```

______________________________________________________________________

## File Descriptors

Arbitrary file descriptors can be captured with:

```python
test.fd(3)
```

For example:

```python
test = c.code("""
    write(3, "hello", 5);
""")

test.fd(3).equals(
    b"hello",
    "Incorrect file descriptor output",
)

test.assert_now()
```

This is useful for functions such as:

```c
ft_putchar_fd
ft_putstr_fd
ft_putendl_fd
ft_putnbr_fd
```

and for testing code that writes directly to a specific descriptor.

______________________________________________________________________

## Values

Generated C code can report arbitrary values using `TEST_VALUE`.

For example:

```python
test = c.code("""
    int result = 42;

    TEST_VALUE(
        "result",
        "%d",
        result
    );
""")
```

The Python side can then check the value:

```python
test.value("result").equals(
    "42",
    "Incorrect result",
)
```

Values are transferred as strings. The C format string determines how the value is represented.

For example:

```c
TEST_VALUE("size", "%zu", size);
TEST_VALUE("pointer", "%p", pointer);
TEST_VALUE("flag", "%d", flag);
```

A value must have a unique name within a test.

______________________________________________________________________

## Buffers

Binary buffers can be captured with `TEST_BUFFER`:

```python
test = c.code("""
    unsigned char buffer[] = {
        0x00, 0x01, 0xff, 0x42
    };

    TEST_BUFFER(
        "buffer",
        buffer,
        sizeof(buffer)
    );
""")
```

The Python side receives the result as `bytes`:

```python
test.buffer("buffer").equals(
    b"\x00\x01\xff\x42",
)
```

This is useful for testing functions where comparing strings is insufficient.

For example:

```python
test = c.code("""
    unsigned char buffer[4] = {
        0xde, 0xad, 0xbe, 0xef
    };

    ft_memset(buffer, 0, 2);

    TEST_BUFFER(
        "buffer",
        buffer,
        sizeof(buffer)
    );
""")

test.buffer("buffer").equals(
    b"\x00\x00\xbe\xef",
)
```

Zero-length buffers are also supported.

______________________________________________________________________

# Assertions

Assertions are attached to a captured result.

For example:

```python
test.value("result").equals("42")
```

does not execute the test immediately.

The test is executed when:

```python
test.assert_now()
```

is called.

______________________________________________________________________

## `equals()`

`equals()` checks that the actual result exactly matches the expected result.

```python
test.value("result").equals("42")
```

For buffers:

```python
test.buffer("buffer").equals(b"hello")
```

For return values:

```python
test.return_value().equals(0)
```

An optional message can explain the failure:

```python
test.value("result").equals(
    "42",
    "Incorrect result",
)
```

______________________________________________________________________

## `reference()`

A result can be marked as a reference:

```python
test.value("result").equals("42").reference()
```

Reference assertions are used when the result of the student's implementation is compared against a reference implementation.

A mismatch is reported as an unexpected result rather than a normal test failure.

`reference()` only marks the assertion. It does not execute the test.

______________________________________________________________________

## `assert_now()`

`assert_now()` executes the generated test and evaluates all assertions attached to it.

```python
test = c.code("""
    TEST_VALUE(
        "result",
        "%d",
        42
    );
""")

test.value("result").equals("42")

test.assert_now()
```

Multiple assertions can be attached before calling `assert_now()`:

```python
test.value("value").equals("42")
test.buffer("buffer").equals(b"hello")
test.return_value().equals(0)

test.assert_now()
```

______________________________________________________________________

# Test-Owned C Code

Tests often need C variables or helper functions that exist outside the function being tested.

The framework provides methods for adding these directly to the generated program.

______________________________________________________________________

## Variables

Test-owned variables can be created when constructing C code.

For example, a test can allocate and initialize data directly in C:

```python
test = c.code("""
    int value = 42;

    TEST_VALUE(
        "value",
        "%d",
        value
    );
""")
```

The test owns `value`, so it is responsible for ensuring any dynamically allocated memory is cleaned up.

______________________________________________________________________

## Helper Functions

Some functions require callbacks:

```c
void ft_lstiter(t_list *lst, void (*f)(void *));
```

These callbacks can be defined as file-scope helper functions with `function()`:

```python
test = (
    c.include("libft.h")
    .function("""
        static int __calls;

        static void test_f(void *content)
        {
            int *value = content;

            (*value)++;
            __calls++;
        }
    """)
    .code("""
        int value = 41;

        t_list node;

        node.content = &value;
        node.next = NULL;

        ft_lstiter(&node, test_f);

        TEST_VALUE(
            "value",
            "%d",
            value
        );

        TEST_VALUE(
            "calls",
            "%d",
            __calls
        );
    """)
)
```

Helper functions are emitted at file scope before the generated test function.

This allows them to be used as normal C function pointers.

______________________________________________________________________

## Includes

Additional headers can be added with:

```python
test = c.include(
    "stdlib.h",
    "string.h",
)
```

For example:

```python
test = (
    c.include(
        "libft.h",
        "stdlib.h",
        "string.h",
    )
    .code("""
        ...
    """)
)
```

Includes are inserted into the generated C program.

______________________________________________________________________

# Malloc Testing

The framework can intercept `malloc()` calls made by the generated test program.

This allows tests to check both normal allocation behavior and allocation-failure handling.

______________________________________________________________________

## Malloc Count

The number of successful allocations can be checked with:

```python
test.malloc.count(
    4,
    "Test malloc count",
)
```

For example, if a test creates three list nodes and three separate content allocations:

```python
test.malloc.count(
    6,
    "Test malloc count",
)
```

This can detect unexpected allocations as well as missing allocations.

______________________________________________________________________

## Malloc Size

Individual allocation sizes can be checked:

```python
test.malloc.size(
    0,
    16,
    "Incorrect first allocation size",
)
```

The allocation index starts at zero.

For example:

```python
test.malloc.size(0, 16)
test.malloc.size(1, 32)
```

checks the first two successful allocations.

This is useful for functions such as `ft_calloc`, `ft_strdup`, and `ft_lstnew`.

______________________________________________________________________

# Simulating Malloc Failures

The framework can force a particular `malloc()` allocation to fail.

The generated C test can reset the malloc strike state:

```c
malloc_strike_reset();
```

and configure a failure:

```c
malloc_strike_fail_at(3);
```

This causes the selected allocation to fail.

For example:

```python
test = c.code("""
    malloc_strike_reset();
    malloc_strike_fail_at(0);

    void *ptr = malloc(100);

    TEST_VALUE(
        "null",
        "%d",
        ptr == NULL
    );
""")
```

This is especially useful for testing cleanup paths.

For example, `ft_lstmap` needs to clean up already-created nodes if allocation of a later node fails.

A failure test can therefore verify both:

- the function returns `NULL`
- all previously allocated resources are released

______________________________________________________________________

# AddressSanitizer

Tests can be executed with AddressSanitizer enabled.

AddressSanitizer can detect:

- memory leaks
- use-after-free
- buffer overflows
- invalid memory accesses
- other memory errors

For example, a test that forgets to free an allocated list will produce an AddressSanitizer error rather than silently passing.

This is particularly useful for list functions and allocation-failure tests where ownership can become complicated.

A test is considered an error if AddressSanitizer reports a runtime memory error.

______________________________________________________________________

# Debug Mode

Generated test programs can optionally be run under a debugger.

Debug mode prints the generated C program before execution and exposes the program output.

A typical debug output looks like:

```text
──────────────────── C CODE ────────────────────
[yellow generated C code]
────────────────────────────────────────────────

[DEBUG] Program output
────────────────────────────────────
...
────────────────────────────────────

[PASS]
```

This is useful when a test fails during development and the generated C needs to be inspected.

______________________________________________________________________

# Test Lifecycle

A typical test follows this sequence:

```text
Python test
    |
    v
Generate C code
    |
    v
Add includes/helpers
    |
    v
Compile
    |
    v
Run generated program
    |
    +--> Capture stdout
    +--> Capture file descriptors
    +--> Capture values
    +--> Capture buffers
    +--> Capture return value
    +--> Track malloc
    |
    v
Evaluate assertions
    |
    v
PASS / FAIL / UNEXPECTED / ERROR
```

The important distinction is that constructing a test does not immediately execute the student's function.

For example:

```python
test = c.code("""
    ...
""")

test.value("result").equals("42")
```

only constructs the test and its assertions.

Execution happens at:

```python
test.assert_now()
```

______________________________________________________________________

# Examples

## `ft_strlen`

A simple return-value test:

```python
from framework import TestSuite

suite = TestSuite("ft_strlen")


@suite.case("basic")
def test_basic(c):
    test = c.code("""
        TEST_VALUE(
            "result",
            "%zu",
            ft_strlen("hello")
        );
    """)

    test.value("result").equals(
        "5",
        "Incorrect string length",
    )

    test.assert_now()
```

______________________________________________________________________

## `ft_memcpy`

A buffer can be checked after calling the function:

```python
@suite.case("basic")
def test_basic(c):
    test = c.code("""
        char source[] = "hello";
        char destination[6];

        ft_memcpy(
            destination,
            source,
            sizeof(source)
        );

        TEST_BUFFER(
            "destination",
            destination,
            sizeof(destination)
        );
    """)

    test.buffer("destination").equals(
        b"hello\x00",
        "Incorrect copied buffer",
    )

    test.assert_now()
```

______________________________________________________________________

## `ft_lstmap`

Functions involving callbacks can define helper functions at file scope.

```python
@suite.case("basic")
def test_basic(c):
    test = (
        c.include(
            "libft.h",
            "stdlib.h",
        )
        .function("""
        static void *test_f(void *content)
        {
            int *value = content;
            int *result = malloc(sizeof(int));

            if (result == NULL)
                return NULL;

            *result = *value + 100;
            return result;
        }

        static void test_del(void *content)
        {
            free(content);
        }
        """)
        .code("""
        int value = 42;

        t_list node;

        node.content = &value;
        node.next = NULL;

        t_list *mapped = ft_lstmap(
            &node,
            test_f,
            test_del
        );

        TEST_VALUE(
            "result",
            "%d",
            mapped != NULL
            && *(int *)mapped->content == 142
        );

        if (mapped != NULL)
        {
            free(mapped->content);
            free(mapped);
        }
        """)
    )

    test.value("result").equals(
        "1",
        "Incorrect mapped list",
    )

    test.assert_now()
```

For more complicated functions, tests should explicitly verify ownership, node addresses, links, content pointers, and cleanup behavior rather than checking only the returned value.

______________________________________________________________________

# Generated C

The framework generates a complete temporary C source file for each test.

Conceptually, the generated program looks like:

```c
#include <...>
#include "libft.h"

static void helper_function(...)
{
    ...
}

static int __test_code(void)
{
    ...
}

int main(void)
{
    ...
}
```

User-defined helper functions are emitted at file scope.

The test code passed to `c.code()` is placed inside the generated test function.

The framework also inserts the required capture and malloc-testing infrastructure.

The generated source can be printed in debug mode when investigating a failing test.

______________________________________________________________________

# Temporary Files

Generated test programs and their build artifacts are stored in temporary directories.

A typical generated test might be located at:

```text
/tmp/tmpxxxxxx/test.c
```

The temporary directory contains the generated source and executable required to run the test.

Temporary files are not part of the student's project.

______________________________________________________________________

# Project Configuration

Projects are represented by a `Project` object.

A project specifies:

- project name
- build method
- build options
- test includes
- compiler flags
- libraries
- test files

For example:

```python
from framework import BuildConfig, Project

project = Project(
    name="libft",
    build=BuildConfig(
        method="make",
        target="all",
    ),
)
```

______________________________________________________________________

## Make

The default build method uses `make`.

```python
BuildConfig(
    method="make",
)
```

A specific target can be selected:

```python
BuildConfig(
    method="make",
    target="bonus",
)
```

The framework executes:

```text
make
```

or:

```text
make bonus
```

in the project directory.

______________________________________________________________________

## Direct Compiler Builds

Projects can also be compiled directly with a C compiler:

```python
BuildConfig(
    method="cc",
    compiler="cc",
    flags=[
        "-Wall",
        "-Wextra",
        "-Werror",
    ],
    sources=[
        "main.c",
        "foo.c",
    ],
    output="a.out",
)
```

The generated command is conceptually:

```text
cc -Wall -Wextra -Werror main.c foo.c -o a.out
```

The compiler can be changed:

```python
BuildConfig(
    method="cc",
    compiler="gcc",
)
```

or:

```python
BuildConfig(
    method="cc",
    compiler="clang",
)
```

______________________________________________________________________

## Project Includes

Project-specific headers can be configured through the test configuration:

```python
TestConfig(
    includes=[
        "libft.h",
    ],
)
```

Individual tests can also add headers using:

```python
c.include(
    "stdlib.h",
    "string.h",
)
```

______________________________________________________________________

## Compiler Flags

Additional compiler flags can be configured through `TestConfig`:

```python
TestConfig(
    cflags=[
        "-Wall",
        "-Wextra",
    ],
)
```

Build flags and test-specific compiler flags are kept separate so that project compilation and generated test compilation can be configured independently.

______________________________________________________________________

## Libraries

Libraries required when compiling generated tests can be specified through the project configuration.

For example:

```python
TestConfig(
    link=[
        "-lm",
    ],
)
```

The resulting test command links the generated test program against the specified libraries.

______________________________________________________________________

# Current Limitations

## Function Pointers

Function-pointer arguments are supported through file-scope helper functions.

For example:

```python
.function("""
    static void test_callback(void *content)
    {
        ...
    }
""")
```

The helper can then be passed normally:

```c
ft_lstiter(lst, test_callback);
```

Function pointers are not represented as ordinary Python values.

______________________________________________________________________

## C Type Compatibility

The framework generates real C code and relies on the C compiler for type checking.

The Python API does not attempt to completely model the C type system.

When testing complicated types, structs, callbacks, or pointer conversions, it is generally better to write the required C directly inside `c.code()` and let the compiler validate it.

______________________________________________________________________

# API Summary

## `TestSuite`

```python
suite = TestSuite("ft_strlen")
```

Register a test case:

```python
@suite.case("basic")
def test_basic(c):
    ...
```

______________________________________________________________________

## `CContext`

The test context provides methods for constructing generated C code.

### `c.code()`

```python
test = c.code("""
    ...
""")
```

### `c.include()`

```python
test = c.include(
    "stdlib.h",
    "string.h",
)
```

### `c.function()`

```python
test = c.function("""
    static void helper(void)
    {
        ...
    }
""")
```

`include()` and `function()` can be chained with `code()`:

```python
test = (
    c.include("libft.h", "stdlib.h")
    .function("""
        static void helper(void)
        {
            ...
        }
    """)
    .code("""
        ...
    """)
)
```

______________________________________________________________________

## `CCode`

`c.code()` returns a `CCode` object.

It supports assertions on captured results:

```python
test.stdout()
test.fd(3)
test.value("name")
test.buffer("name")
test.return_value()
test.malloc
```

The test is executed with:

```python
test.assert_now()
```

______________________________________________________________________

## `CCodeBuilder`

Helper functions can be added before generating the test:

```python
test = (
    c.include("libft.h")
    .function("""
        static void helper(void)
        {
            ...
        }
    """)
    .code("""
        ...
    """)
)
```

`function()` can be called multiple times to add multiple helpers.

______________________________________________________________________

## Return Value

```python
test.return_value()
```

Example:

```python
test.return_value().equals(
    42,
    "Incorrect return value",
)
```

______________________________________________________________________

## Standard Output

```python
test.stdout()
```

Example:

```python
test.stdout().equals(
    b"hello\n",
)
```

______________________________________________________________________

## File Descriptors

```python
test.fd(3)
```

Example:

```python
test.fd(3).equals(
    b"hello",
)
```

______________________________________________________________________

## Values

```python
test.value("name")
```

Example:

```python
test.value("result").equals(
    "42",
)
```

______________________________________________________________________

## Buffers

```python
test.buffer("name")
```

Example:

```python
test.buffer("buffer").equals(
    b"\x00\x01\x02",
)
```

______________________________________________________________________

## Malloc

```python
test.malloc.count(4)
test.malloc.size(0, 16)
test.malloc.fail_at(3)
```

Malloc failures can also be configured directly inside generated C:

```c
malloc_strike_reset();
malloc_strike_fail_at(3);
```

______________________________________________________________________

# Design Notes

The framework intentionally keeps a large part of the test logic in generated C.

This has several advantages:

- C types are handled by the C compiler.
- Structs can be tested naturally.
- Function pointers work like normal C function pointers.
- Pointer identity can be compared directly.
- Complex ownership and cleanup behavior can be tested.
- The framework does not need to reimplement the C type system in Python.

Python is primarily responsible for:

- generating the test
- configuring the build
- running the executable
- capturing results
- evaluating assertions
- presenting failures

The actual behavior being tested remains ordinary C code.

______________________________________________________________________

# Pointer Ownership

Tests should explicitly consider ownership of dynamically allocated memory.

## Test-owned memory

If the test allocates memory, the test is responsible for freeing it.

For example:

```c
int *value = malloc(sizeof(int));

/* test */

free(value);
```

This is particularly important because AddressSanitizer reports leaks even when the function being tested is correct.

## Function-owned memory

If a function returns newly allocated memory, the test is responsible for freeing it after checking the result.

For example:

```c
char *result = ft_strdup("hello");

TEST_BUFFER(
    "result",
    result,
    strlen(result)
);

free(result);
```

For list functions, the test should preserve the appropriate node/content pointers when necessary so cleanup does not depend on the function under test behaving correctly.

______________________________________________________________________

# Debugging Failed Tests

When a test unexpectedly fails, the most useful things to check are:

1. The generated C code.
1. The actual captured output.
1. The expected value.
1. The actual value.
1. AddressSanitizer output.
1. Malloc count and allocation sizes.
1. Whether the test itself correctly owns and frees its allocations.

For list functions in particular, tests should avoid traversing a potentially corrupted list during cleanup. Save node pointers before calling the function when testing whether links or nodes were modified.

For example:

```c
t_list *nodes[3];

nodes[0] = lst;
nodes[1] = lst->next;
nodes[2] = lst->next->next;

/* call function under test */

/* cleanup using nodes[] */
```

This allows the test to detect list corruption without relying on the corrupted structure for cleanup.
