"""Tests for Hermes Conversation response control metadata."""

import importlib.util
from pathlib import Path
import sys

_MODULE_PATH = (
    Path(__file__).parents[1]
    / "custom_components"
    / "hermes_conversation"
    / "response_control.py"
)
_SPEC = importlib.util.spec_from_file_location("response_control", _MODULE_PATH)
assert _SPEC is not None
response_control = importlib.util.module_from_spec(_SPEC)
sys.modules["response_control"] = response_control
assert _SPEC.loader is not None
_SPEC.loader.exec_module(response_control)

ConversationResponseControl = response_control.ConversationResponseControl
apply_response_control = response_control.apply_response_control
extract_response_control = response_control.extract_response_control


class DummyConversationResult:
    """Tiny stand-in for homeassistant.components.conversation.ConversationResult."""

    def __init__(self) -> None:
        self.conversation_id = "original"
        self.continue_conversation = False


def test_extract_response_control_defaults_to_no_override() -> None:
    """Chunks without control metadata should not override HA defaults."""
    control = extract_response_control({"type": "item", "content": "Hello"})

    assert control == ConversationResponseControl()


def test_extract_response_control_accepts_continue_conversation_on_chunk() -> None:
    """Webhook chunks can opt into keeping the HA conversation open."""
    control = extract_response_control(
        {"type": "item", "content": "Hello", "continue_conversation": True}
    )

    assert control == ConversationResponseControl(continue_conversation=True)


def test_extract_response_control_accepts_final_control_chunk() -> None:
    """A final/control chunk can carry conversation metadata without speech."""
    control = extract_response_control(
        {
            "type": "final",
            "continue_conversation": True,
            "conversation_id": "abc123",
        }
    )

    assert control == ConversationResponseControl(
        continue_conversation=True,
        conversation_id="abc123",
    )


def test_extract_response_control_ignores_non_bool_continue_conversation() -> None:
    """Invalid control metadata should be ignored instead of changing behavior."""
    control = extract_response_control(
        {"type": "final", "continue_conversation": "true"}
    )

    assert control == ConversationResponseControl()


def test_apply_response_control_overrides_conversation_result() -> None:
    """Control metadata should update the final HA ConversationResult."""
    result = DummyConversationResult()
    control = ConversationResponseControl(
        continue_conversation=True,
        conversation_id="new-id",
    )

    apply_response_control(result, control)

    assert result.continue_conversation is True
    assert result.conversation_id == "new-id"
