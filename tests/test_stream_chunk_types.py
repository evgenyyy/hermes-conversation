"""Tests for Hermes Conversation streaming chunk handling."""

import ast
from pathlib import Path


CONVERSATION_PY = (
    Path(__file__).parents[1]
    / "custom_components"
    / "hermes_conversation"
    / "conversation.py"
)


def test_status_chunks_are_recognised_as_stream_content() -> None:
    """Status chunks are intentionally surfaced as HA progress/holding content."""
    tree = ast.parse(CONVERSATION_PY.read_text(encoding="utf-8"))
    tuple_literals: list[set[str]] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Tuple):
            values = {
                item.value
                for item in node.elts
                if isinstance(item, ast.Constant) and isinstance(item.value, str)
            }
            if {"item", "final"}.issubset(values):
                tuple_literals.append(values)

    assert any("status" in values for values in tuple_literals)
