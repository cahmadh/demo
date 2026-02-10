"""Small calculator CLI application."""

from __future__ import annotations

import argparse
from typing import Iterable


def calculate(left: float, operator: str, right: float) -> float:
    """Return the result for a basic arithmetic operation."""

    if operator == "+":
        return left + right
    if operator == "-":
        return left - right
    if operator == "*":
        return left * right
    if operator == "/":
        if right == 0:
            raise ValueError("Division by zero is not allowed.")
        return left / right
    raise ValueError(f"Unsupported operator: {operator}")


def parse_args(argv: Iterable[str] | None = None) -> argparse.Namespace:
    """Parse command-line arguments for the calculator."""

    parser = argparse.ArgumentParser(description="Small calculator app")
    parser.add_argument("left", type=float, help="Left operand")
    parser.add_argument("operator", choices=["+", "-", "*", "/"], help="Operator")
    parser.add_argument("right", type=float, help="Right operand")
    return parser.parse_args(argv)


def main(argv: Iterable[str] | None = None) -> int:
    """Run the calculator application."""

    args = parse_args(argv)
    try:
        result = calculate(args.left, args.operator, args.right)
    except ValueError as exc:
        print(f"Error: {exc}")
        return 1

    print(result)
    return 0


if __name__ == "__main__":  # pragma: no cover - CLI entry point
    raise SystemExit(main())
