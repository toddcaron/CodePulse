"""Run without installing a global command or executing application code."""

import sys

if sys.version_info < (3, 11):
    print("CodePulse Feature Parity requires Python 3.11+", file=sys.stderr)
    raise SystemExit(1)

try:
    from feature_parity.cli import main
except ModuleNotFoundError:
    print("Feature Parity dependencies are unavailable; follow the engine setup instructions", file=sys.stderr)
    raise SystemExit(1)

if __name__ == "__main__":
    raise SystemExit(main())