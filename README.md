# 42 C Testing Framework

A Python-based testing framework for testing C functions in 42 projects.

The framework generates small C test harnesses, compiles them against the student's project, executes them, and exposes the results through a Python API.

It is designed primarily for testing functions such as those found in `libft`, but can be used for other C projects as well.

______________________________________________________________________

# Table of Contents

<!-- toc -->

- [Features](#features)
- [Basic Usage](#basic-usage)
- [Calling Functions](#calling-functions)
- [Return Values](#return-values)
  - [`equals()`](#equals)
  - [`not_equal()`](#not_equal)
  - [`parsed_value`](#parsed_value)
  - [String Returns](#string-returns)
  - [NULL Checks](#null-checks)
- [Buffers](#buffers)
  - [Buffer Size](#buffer-size)
  - [Buffer Types](#buffer-types)
  - [Buffer Offsets](#buffer-offsets)
- [Checking Modified Buffers](#checking-modified-buffers)
- [Returned Allocated Memory](#returned-allocated-memory)
- [Capture Types](#capture-types)
  - [`Capture.buffer(size)`](#capturebuffersize)
  - [`Capture.pointer_raw()`](#capturepointer_raw)
  - [`Capture.pointer_array(size)`](#capturepointer_arraysize)
- [Assertions](#assertions)
  - [Buffer Equality](#buffer-equality)
  - [Pointer Equality](#pointer-equality)
  - [NULL Pointer](#null-pointer)
  - [Non-NULL Pointer](#non-null-pointer)
  - [Pointer Arrays](#pointer-arrays)
- [Return Capture Assertions](#return-capture-assertions)
- [Checking Returned Pointers](#checking-returned-pointers)
- [Callbacks](#callbacks)
  - [Callback Names](#callback-names)
- [Malloc Testing](#malloc-testing)
  - [Malloc Count](#malloc-count)
  - [Malloc Size](#malloc-size)
- [Simulating Malloc Failures](#simulating-malloc-failures)
  - [Malloc Failure Sweeps](#malloc-failure-sweeps)
- [`assert_now()` vs `assert_reference()`](#assert_now-vs-assert_reference)
  - [`assert_now()`](#assert_now)
  - [`assert_reference()`](#assert_reference)
- [Chaining](#chaining)
- [Project Configuration](#project-configuration)
- [Headers](#headers)
- [Project Includes](#project-includes)
- [Compiler Flags](#compiler-flags)
- [Libraries](#libraries)
- [Build Configuration](#build-configuration)
- [Makefile Requirements](#makefile-requirements)
- [AddressSanitizer](#addresssanitizer)
- [Debug Mode](#debug-mode)
- [Test Lifecycle](#test-lifecycle)
- [Example: `ft_strmapi`](#example-ft_strmapi)
- [Design Notes](#design-notes)
  - [Generated C](#generated-c)
  - [Temporary Files](#temporary-files)
  - [Pointer Ownership](#pointer-ownership)
- [Current Limitations](#current-limitations)
  - [Function pointers](#function-pointers)
  - [C type compatibility](#c-type-compatibility)
  - [Build systems](#build-systems)
- [API Summary](#api-summary)
  - [Context](#context)
  - [Function](#function)
  - [Call Result](#call-result)
  - [Capture](#capture)
  - [Assertions](#assertions-1)

<!-- tocstop -->

______________________________________________________________________

# Features

- Call C functions directly from Python.
- Test return values.
- Test and compare modified input buffers.
- Test functions returning allocated memory.
- Capture returned buffers and pointer arrays.
- Test callbacks and function-pointer arguments.
- Check `malloc()` call counts and allocation sizes.
- Simulate `malloc()` failures.
- Run tests with AddressSanitizer.
- Optionally run generated test programs under a debugger.
- Configure project-specific headers, libraries, compiler flags, and build commands.

______________________________________________________________________

# Basic Usage

A project is represented by a `Project` and a testing context by `CContext`.

A typical test looks like:

```python
from framework.ctesting import CContext


def test_strlen(c):
    ft_strlen = c.function(
        "ft_strlen",
        returns="size_t",
        args=["char const *"],
    )

    result = ft_strlen("hello").run()

    result.equals(5)
    result.assert_now()
```

The `CFunction` object is callable, so this:

```python
ft_strlen("hello")
```

creates a `CCallResult`.

The C function is not executed until:

```python
.run()
```

is called.

______________________________________________________________________

# Calling Functions

Functions can be obtained explicitly:

```python
ft_strlen = c.function(
    "ft_strlen",
    returns="size_t",
    args=["char const *"],
)
```

or dynamically:

```python
ft_strlen = c.ft_strlen
```

When a function is defined in the project's `FunctionConfig`, its configured return type, arguments, headers, libraries, and compiler-error settings are automatically used.

A function can then be called:

```python
result = ft_strlen("hello").run()
```

The number of arguments is checked before the C test is generated.

______________________________________________________________________

# Return Values

## `equals()`

Checks a normal return value.

```python
c.ft_strlen("hello").run().equals(5).assert_now()
```

A custom error message can be supplied:

```python
c.ft_strlen("hello").run().equals(
    5,
    "strlen returned the wrong length",
).assert_now()
```

`equals()` should not be used for `bytes`.

For buffers, use `buffer_equals()` or return captures instead.

______________________________________________________________________

## `not_equal()`

Checks that the return value is not equal to a value.

```python
c.ft_strlen("hello").run().not_equal(10).assert_now()
```

______________________________________________________________________

## `parsed_value`

The raw return value is stored internally as text.

`parsed_value` converts it using the configured C return type:

```python
result = c.ft_strlen("hello").run()

print(result.parsed_value)
```

______________________________________________________________________

## String Returns

For functions returning strings:

```python
result = c.some_string_function().run()

result.equals_string("hello")
result.assert_now()
```

______________________________________________________________________

## NULL Checks

For pointer-returning functions, simple NULL checks are available:

```python
result = c.some_function().run()

result.is_null()
result.assert_now()
```

or:

```python
result = c.some_function().run()

result.is_not_null()
result.assert_now()
```

______________________________________________________________________

# Buffers

`CBuffer` represents memory allocated by the test harness and passed to the student's function.

```python
buffer = c.buffer(
    data=b"hello",
    name="buffer",
)
```

The generated C code will contain an array initialized with the supplied data.

For example:

```python
buffer = c.buffer(
    data=b"hello",
    name="buffer",
)

c.ft_strcpy(buffer, "world").run()
```

______________________________________________________________________

## Buffer Size

The size can be larger than the initial data:

```python
buffer = c.buffer(
    data=b"hello",
    size=32,
    name="buffer",
)
```

The remaining bytes are zero-initialized by C.

The supplied data cannot be larger than the buffer:

```python
c.buffer(
    data=b"hello",
    size=3,
)
```

raises an error.

Zero-sized C buffers are currently not supported.

______________________________________________________________________

## Buffer Types

The default type is:

```text
unsigned char
```

A different C type can be supplied:

```python
buffer = c.buffer(
    data=b"hello",
    name="buffer",
    type="char",
)
```

______________________________________________________________________

## Buffer Offsets

A pointer into a buffer can be created with:

```python
buffer.offset(2)
```

For example:

```python
buffer = c.buffer(
    data=b"hello",
    name="buffer",
)

pointer = buffer.offset(2)

c.some_function(pointer)
```

The generated C argument is equivalent to:

```c
buffer + 2
```

An offset from `0` through `buffer.size` is allowed.

The offset equal to `buffer.size` represents the one-past-the-end pointer.

______________________________________________________________________

# Checking Modified Buffers

After a test runs, buffers passed to the function are copied back and can be checked with:

```python
result.buffer_equals(
    buffer,
    b"expected",
)
```

Example:

```python
buffer = c.buffer(
    data=b"hello",
    name="buffer",
)

result = c.some_function(buffer).run()

result.buffer_equals(
    buffer,
    b"world",
)

result.assert_now()
```

A byte-level diff is included when the contents differ.

______________________________________________________________________

# Returned Allocated Memory

Functions that return pointers can have their returned memory captured.

Use:

```python
Capture.buffer(size)
```

For example:

```python
from framework.ctesting import Capture, Assert

expected = b"hello"

result = c.ft_strdup(expected).capture_return(
    Capture.buffer(len(expected))
).run()

result.assert_return(
    Assert.buffer_equals(expected),
)

result.assert_now()
```

The harness reads the returned memory and then frees it.

This is intended for functions where the returned pointer represents memory owned by the caller.

For example:

```c
char *ft_strdup(const char *s);
```

can be tested by capturing the returned buffer.

______________________________________________________________________

# Capture Types

## `Capture.buffer(size)`

Captures `size` bytes from the returned pointer.

```python
Capture.buffer(10)
```

The returned pointer must be non-NULL to produce a buffer capture.

A size of zero is allowed for return captures.

______________________________________________________________________

## `Capture.pointer_raw()`

Captures only the returned pointer value.

```python
Capture.pointer_raw()
```

This does **not** dereference the pointer.

It is useful when testing pointer-returning functions where the pointer itself matters, especially during `malloc()` failure testing.

A raw pointer capture is not automatically freed by the harness.

______________________________________________________________________

## `Capture.pointer_array(size)`

Captures an array of pointers.

Each array element needs a child capture:

```python
capture = Capture.pointer_array(3)

capture.child(Capture.buffer(5))
capture.child(Capture.buffer(5))
capture.child(Capture.buffer(5))
```

The number of children must exactly match the array size.

The returned pointer array and its captured child allocations are freed by the harness according to the capture structure.

______________________________________________________________________

# Assertions

Assertions are represented by `Assert`.

## Buffer Equality

```python
Assert.buffer_equals(b"hello")
```

______________________________________________________________________

## Pointer Equality

```python
Assert.pointer_equals(expected_pointer)
```

______________________________________________________________________

## NULL Pointer

```python
Assert.is_null_pointer()
```

______________________________________________________________________

## Non-NULL Pointer

```python
Assert.is_not_null_pointer()
```

______________________________________________________________________

## Pointer Arrays

Pointer-array assertions are built using child assertions:

```python
assertion = Assert.pointer_array()

assertion.child(
    Assert.buffer_equals(b"hello")
)

assertion.child(
    Assert.buffer_equals(b"world")
)
```

Then:

```python
result.assert_return(assertion)
```

______________________________________________________________________

# Return Capture Assertions

A return capture must be configured before running the call:

```python
result = (
    c.ft_strdup("hello")
    .capture_return(Capture.buffer(5))
    .run()
)

result.assert_return(
    Assert.buffer_equals(b"hello")
)

result.assert_now()
```

`capture_return()` can only be used with pointer-returning functions.

______________________________________________________________________

# Checking Returned Pointers

The framework records the addresses of `CBuffer` objects passed into the function.

This allows testing whether a function returned a pointer to a particular buffer:

```python
buffer = c.buffer(
    data=b"hello",
    name="buffer",
)

result = c.some_function(buffer).run()

result.returned_pointer_is(buffer)
result.assert_now()
```

Buffer offsets are also supported:

```python
result.returned_pointer_is(buffer.offset(2))
```

This checks that the returned pointer equals the address of the buffer plus the requested offset.

______________________________________________________________________

# Callbacks

Functions accepting function pointers can be tested with `CCallback`.

For example, for:

```c
char *ft_strmapi(
    char const *s,
    char (*f)(unsigned int, char)
);
```

define a callback:

```python
increment = c.callback(
    name="increment",
    returns="char",
    args=[
        ("unsigned int", "i"),
        ("char", "c"),
    ],
    body="return c + i;",
)
```

Then pass it to the function:

```python
result = c.ft_strmapi(
    "abc",
    increment,
).run()
```

The generated C harness contains:

```c
static char increment(unsigned int i, char c)
{
    return c + i;
}
```

Callback argument types are checked against the function's declared function-pointer type.

______________________________________________________________________

## Callback Names

Callback names must be valid identifiers.

Each callback must have an explicit name:

```python
c.callback(
    name="increment",
    ...
)
```

Multiple callbacks can therefore be used in one test:

```python
first = c.callback(
    name="first",
    returns="char",
    args=[("char", "c")],
    body="return c + 1;",
)

second = c.callback(
    name="second",
    returns="char",
    args=[("char", "c")],
    body="return c - 1;",
)
```

Callback names must not conflict with generated harness names or the function being tested.

______________________________________________________________________

# Malloc Testing

The framework intercepts `malloc()` using the linker:

```text
-Wl,--wrap=malloc
```

This allows the framework to record:

- number of `malloc()` calls
- size of every allocation
- controlled allocation failures

______________________________________________________________________

## Malloc Count

```python
result = c.some_function(...).run()

result.malloc_count_equals(1)
result.assert_now()
```

______________________________________________________________________

## Malloc Size

Check an individual allocation:

```python
result.malloc_size_equals(
    0,
    42,
)
```

The index is zero-based.

For example:

```python
result.malloc_count_equals(2)
result.malloc_size_equals(0, 16)
result.malloc_size_equals(1, 32)
```

______________________________________________________________________

# Simulating Malloc Failures

A specific `malloc()` call can be forced to fail:

```python
c.malloc.fail_at(0)
```

This makes the first intercepted `malloc()` return `NULL`.

For example:

```python
c.malloc.fail_at(0)

result = c.ft_strdup("hello").run()

result.is_null()
result.assert_now()

c.malloc.reset()
```

The failure index is zero-based.

`reset()` removes the failure condition:

```python
c.malloc.reset()
```

______________________________________________________________________

## Malloc Failure Sweeps

For functions performing multiple allocations, tests can run the function repeatedly while changing the failure index:

```python
for index in range(expected_malloc_count):
    c.malloc.fail_at(index)

    result = c.some_function(...).run()

    # Check expected failure behavior.

c.malloc.reset()
```

When using AddressSanitizer, this can also detect memory leaks and invalid memory accesses caused by incomplete error handling.

For pointer-returning functions during malloc-failure tests, `Capture.pointer_raw()` is useful because it records the pointer without dereferencing or automatically freeing it.

______________________________________________________________________

# `assert_now()` vs `assert_reference()`

Both methods check accumulated assertion failures.

## `assert_now()`

Use this when the test itself is asserting expected behavior:

```python
result.equals(5)
result.assert_now()
```

Failures raise:

```text
AssertionFailure
```

______________________________________________________________________

## `assert_reference()`

Use this when comparing the student's behavior against a reference implementation:

```python
result.assert_reference()
```

Failures raise:

```text
UnexpectedResult
```

This allows the test runner to distinguish:

- an explicit test assertion failure
- a result that differs unexpectedly from the reference implementation

______________________________________________________________________

# Chaining

Most result-checking methods return the `CCallResult`, so checks can be chained:

```python
(
    c.ft_strlen("hello")
    .run()
    .equals(5)
    .not_equal(10)
    .assert_now()
)
```

The call itself must always be executed with `.run()` before result-dependent methods are used.

______________________________________________________________________

# Project Configuration

The framework uses a `Project` configuration.

A simplified configuration looks like:

```python
Project(
    name="libft",
    build=BuildConfig(
        method="make",
    ),
    functions=FunctionConfig(
        functions={
            "ft_strlen": FunctionDefinition(
                returns="size_t",
                args=["char const *"],
            ),
        },
    ),
)
```

Function definitions can specify:

```python
FunctionDefinition(
    returns="char *",
    args=["char const *"],
    headers=["libft.h"],
    link=[],
    err_flags=True,
)
```

______________________________________________________________________

# Headers

Headers required by a function can be configured:

```python
FunctionDefinition(
    returns="size_t",
    args=["char const *"],
    headers=["libft.h"],
)
```

The generated harness will include:

```c
#include <libft.h>
```

When headers are not configured, the framework generates an `extern` declaration for the function.

______________________________________________________________________

# Project Includes

Project-wide include directories can be configured using:

```python
FunctionConfig(
    includes=[
        "include",
    ],
)
```

These are passed to the generated harness as:

```text
-I <project>/include
```

______________________________________________________________________

# Compiler Flags

Project-wide flags for compiling the generated test harness are configured with:

```python
FunctionConfig(
    cflags=[
        "-D_SOME_DEFINE",
    ],
)
```

These flags are applied when compiling the generated C test program.

______________________________________________________________________

# Libraries

Project-wide libraries/objects can be specified using:

```python
FunctionConfig(
    link=[
        "libft.a",
    ],
)
```

Function-specific libraries can be configured with:

```python
FunctionDefinition(
    link=["m"],
)
```

Function-specific libraries are passed as:

```text
-lm
```

______________________________________________________________________

# Build Configuration

The project build configuration supports:

```python
BuildConfig(
    method="make",
    target=None,
    compiler="cc",
    flags=[],
    sources=[],
    output="a.out",
)
```

The current ASan build implementation supports **Makefiles only**.

______________________________________________________________________

# Makefile Requirements

If a project uses a Makefile, the Makefile **must use the `CFLAGS` variable** when compiling C files.

For example:

```make
CC = cc
CFLAGS = -Wall -Wextra -Werror

%.o: %.c
	$(CC) $(CFLAGS) -c $< -o $@
```

Do **not** hard-code the compiler flags:

```make
%.o: %.c
	cc -Wall -Wextra -Werror -c $< -o $@
```

The reason is that AddressSanitizer builds override `CFLAGS` by invoking:

```bash
make -B CFLAGS="..."
```

The framework adds:

```text
-fsanitize=address
-fno-omit-frame-pointer
```

to the project's configured build flags.

Therefore, a Makefile that ignores `$(CFLAGS)` will not be rebuilt correctly with AddressSanitizer.

The variable name must be exactly:

```text
CFLAGS
```

not:

```text
CFLAG
```

______________________________________________________________________

# AddressSanitizer

ASan can be enabled when creating the testing context:

```python
c = CContext(
    project,
    config,
    asan=True,
)
```

The framework builds the project with:

```text
-fsanitize=address
-fno-omit-frame-pointer
```

and also compiles the generated test harness with ASan.

ASan errors are reported as test failures.

ASan is particularly useful for:

- buffer overflows
- use-after-free
- invalid memory accesses
- memory leaks
- incorrect malloc-failure cleanup

______________________________________________________________________

# Debug Mode

Debug mode can be enabled with:

```python
c = CContext(
    project,
    config,
    debug=True,
)
```

Debug mode prints:

- build commands
- generated C test harnesses
- additional execution information

The generated test executable is run through the framework's debug-process helper.

______________________________________________________________________

# Test Lifecycle

A typical test follows this sequence:

```text
Create CContext
       |
       v
Get CFunction
       |
       v
Create arguments / buffers / callbacks
       |
       v
Create CCallResult
       |
       v
Configure return capture if needed
       |
       v
.run()
       |
       v
Generate C harness
       |
       v
Compile harness
       |
       v
Execute C function
       |
       v
Capture return value / buffers / malloc information
       |
       v
Perform assertions
       |
       v
.assert_now() / .assert_reference()
```

______________________________________________________________________

# Example: `ft_strmapi`

Given:

```c
char *ft_strmapi(
    char const *s,
    char (*f)(unsigned int, char)
);
```

a test can be written as:

```python
from framework.ctesting import Capture, Assert


def test_ft_strmapi(c):
    increment = c.callback(
        name="increment",
        returns="char",
        args=[
            ("unsigned int", "i"),
            ("char", "c"),
        ],
        body="return c + i;",
    )

    expected = b"ace"

    result = c.ft_strmapi(
        "abc",
        increment,
    ).capture_return(
        Capture.buffer(len(expected))
    ).run()

    result.assert_return(
        Assert.buffer_equals(expected),
        "ft_strmapi returned incorrect string",
    )

    result.assert_now()
```

______________________________________________________________________

# Design Notes

## Generated C

Tests are not interpreted as C directly.

Instead, the framework generates a temporary C source file containing:

- required headers
- callback definitions
- function declarations
- test arguments
- the function call
- buffer capture code
- malloc information
- return-value output
- cleanup code

The generated source is then compiled and executed.

______________________________________________________________________

## Temporary Files

Generated harnesses and captured buffer data are stored in a temporary directory.

The directory is automatically removed after the test finishes.

______________________________________________________________________

## Pointer Ownership

Return captures currently imply ownership depending on the capture type.

`Capture.buffer()` and pointer-array captures cause the generated harness to free the captured allocations.

`Capture.pointer_raw()` intentionally does not free the pointer.

This distinction is particularly important when testing allocation failures or when the returned pointer must only be observed rather than dereferenced.

______________________________________________________________________

# Current Limitations

The current implementation intentionally keeps the type system and C parser simple.

## Function pointers

Function-pointer declarations currently support simple forms such as:

```c
char (*)(unsigned int, char)
```

Complex nested function-pointer types are not currently fully parsed.

## C type compatibility

Callback types are currently compared using their textual representation.

For example:

```c
const char *
```

and:

```c
char const *
```

are semantically equivalent C types but are not currently treated as identical by the callback validator.

## Build systems

ASan builds currently require:

```text
make
```

and a Makefile that correctly uses `CFLAGS`.

______________________________________________________________________

# API Summary

## Context

```python
c.function(...)
c.buffer(...)
c.callback(...)
c.program(...)
c.malloc.fail_at(...)
c.malloc.reset()
```

## Function

```python
function(...)
```

A `CFunction` is callable and produces a `CCallResult`.

## Call Result

```python
result.run()

result.equals(...)
result.not_equal(...)
result.equals_string(...)

result.is_null(...)
result.is_not_null(...)

result.buffer_equals(...)
result.returned_buffer_equals(...)
result.returned_pointer_is(...)

result.capture_return(...)
result.assert_return(...)

result.malloc_count_equals(...)
result.malloc_size_equals(...)

result.assert_now()
result.assert_reference()
```

## Capture

```python
Capture.buffer(size)
Capture.pointer_raw()
Capture.pointer_array(size)
capture.child(...)
```

## Assertions

```python
Assert.buffer_equals(...)
Assert.pointer_equals(...)
Assert.is_null_pointer(...)
Assert.is_not_null_pointer(...)
Assert.pointer_array(...)
assertion.child(...)
```
