#!/usr/bin/env python3
"""pv -- one command to drive the pressure-vessel-design skill.

A thin dispatcher so you (or Claude) never has to remember paths or import
quirks. Run from anywhere:

    python pv.py                 show this help
    python pv.py check           verify which calc modules import (smoke test)
    python pv.py test            run the validation + regression suite
    python pv.py list            list runnable worked examples
    python pv.py run <example>   run a worked example (e.g. `run heads`)
    python pv.py index           regenerate the module index

Examples: cylinder, heads, flange, noncircular.
"""
import os
import runpy
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _HERE)

_EXAMPLES = {
    "cylinder": "example_cylinder.py",
    "heads": "example_heads.py",
    "flange": "example_flange.py",
    "noncircular": "example_noncircular.py",
}


def _run_file(name: str) -> int:
    runpy.run_path(os.path.join(_HERE, name), run_name="__main__")
    return 0


def cmd_check() -> int:
    from pv_env import smoke_test
    return smoke_test()


def cmd_test() -> int:
    # tests.py calls unittest.main(), which parses sys.argv -- reset it so the
    # dispatcher's own args aren't read as test names.
    sys.argv = ["tests.py"]
    return _run_file("tests.py")


def cmd_list() -> int:
    print("Runnable examples (python pv.py run <name>):")
    for key, fn in _EXAMPLES.items():
        print(f"  {key:<12} -> {fn}")
    return 0


def cmd_run(args) -> int:
    if not args or args[0] not in _EXAMPLES:
        print("Usage: python pv.py run <example>")
        cmd_list()
        return 2
    return _run_file(_EXAMPLES[args[0]])


def cmd_index() -> int:
    sys.argv = ["index_modules.py", "--write"]
    return _run_file("index_modules.py") or 0


def main(argv) -> int:
    if not argv or argv[0] in ("-h", "--help", "help"):
        print(__doc__)
        return 0
    cmd, rest = argv[0], argv[1:]
    dispatch = {
        "check": cmd_check, "smoke": cmd_check,
        "test": cmd_test, "tests": cmd_test,
        "list": cmd_list,
        "index": cmd_index,
    }
    if cmd == "run":
        return cmd_run(rest)
    if cmd in dispatch:
        return dispatch[cmd]()
    print(f"Unknown command {cmd!r}.\n")
    print(__doc__)
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
