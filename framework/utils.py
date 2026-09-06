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
