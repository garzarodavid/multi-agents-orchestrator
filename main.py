import sys
from typing import List, Optional

from orchestrator import Orchestrator


def main(argv: Optional[List[str]] = None) -> int:
    argv = argv or sys.argv[1:]
    orchestrator = Orchestrator()

    if argv:
        return orchestrator.non_interactive_run(" ".join(argv))

    orchestrator.interactive_loop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
