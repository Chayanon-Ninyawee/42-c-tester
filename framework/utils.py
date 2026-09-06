import selectors
import subprocess

from .color import Color, color


def run_debug_process(command, cwd):
    process = subprocess.Popen(
        command,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        bufsize=0,
    )

    selector = selectors.DefaultSelector()

    selector.register(
        process.stdout,
        selectors.EVENT_READ,
        "STDOUT",
    )

    selector.register(
        process.stderr,
        selectors.EVENT_READ,
        "STDERR",
    )

    stdout = bytearray()
    stderr = bytearray()

    print()
    print(color("  [DEBUG] Program output", Color.CYAN))
    print(color("  ────────────────────────────────────", Color.CYAN))

    while selector.get_map():
        for key, _ in selector.select():
            stream = key.fileobj
            name = key.data

            data = stream.read(4096)

            if not data:
                selector.unregister(stream)
                continue

            if name == "STDOUT":
                stdout.extend(data)
                prefix = color("  STDOUT:", Color.BLUE)
            else:
                stderr.extend(data)
                prefix = color("  STDERR:", Color.MAGENTA)

            text = data.decode(errors="replace")

            for line in text.splitlines():
                print(f"{prefix} {line}")

    returncode = process.wait()

    selector.close()

    print(color("  ────────────────────────────────────", Color.CYAN))

    return subprocess.CompletedProcess(
        command,
        returncode,
        bytes(stdout),
        bytes(stderr),
    )


def format_bytes(data: bytes) -> str:
    return "".join(repr(bytes([byte]))[2:-1] for byte in data)


def format_buffer_diff(
    expected: bytes,
    received: bytes,
    context: int = 20,
):
    limit = min(len(expected), len(received))

    index = 0

    while index < limit and expected[index] == received[index]:
        index += 1

    if index == limit:
        if len(expected) != len(received):
            return (
                f"  length mismatch at index {index}\n"
                f"  expected length: {len(expected)}\n"
                f"  received length: {len(received)}"
            )

        return ""

    start = max(0, index - context)
    end = min(
        max(len(expected), len(received)),
        index + context + 1,
    )

    expected_context = expected[start:end]
    received_context = received[start:end]

    expected_display = format_bytes(expected_context)
    received_display = format_bytes(received_context)

    # Account for the "b'" before the first byte.
    pointer_offset = 2 + len(format_bytes(received[start:index]))

    pointer = " " * pointer_offset + "^"

    return (
        f"  first mismatch at index: {index}\n\n"
        f"  expected byte: 0x{expected[index]:02x}\n"
        f"  received byte: 0x{received[index]:02x}\n\n"
        f"  context:\n"
        f"    expected: b'{expected_display}'\n"
        f"    received: b'{received_display}'\n"
        f"              {pointer}"
    )
