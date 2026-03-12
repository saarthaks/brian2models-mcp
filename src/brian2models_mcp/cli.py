"""CLI for brian2models: seed and rebuild the model library."""

import argparse
import sys


def main():
    parser = argparse.ArgumentParser(
        prog="brian2models",
        description="Manage the Brian2 model library",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("seed", help="Fetch Brian2 examples and build models.json")
    subparsers.add_parser("rebuild", help="Rebuild the model library (alias for seed)")

    args = parser.parse_args()

    if args.command in ("seed", "rebuild"):
        from .seeder import seed
        seed()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
