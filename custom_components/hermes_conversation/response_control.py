"""Conversation response control helpers for Hermes Conversation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(slots=True)
class ConversationResponseControl:
    """Optional metadata that overrides Home Assistant conversation defaults."""

    continue_conversation: bool | None = None
    conversation_id: str | None = None

    def merge(self, other: ConversationResponseControl) -> None:
        """Merge explicitly provided values from another control object."""
        if other.continue_conversation is not None:
            self.continue_conversation = other.continue_conversation
        if other.conversation_id is not None:
            self.conversation_id = other.conversation_id


def extract_response_control(data: dict[str, Any]) -> ConversationResponseControl:
    """Extract conversation control metadata from a webhook response/chunk.

    Supported in both non-streaming JSON responses and streaming NDJSON chunks:

    ```json
    {"output": "Hello", "continue_conversation": true}
    {"type": "final", "continue_conversation": true}
    {"type": "control", "conversation_id": "...", "continue_conversation": false}
    ```

    Invalid metadata is ignored so existing webhook payloads keep current behavior.
    """
    control = ConversationResponseControl()

    continue_conversation = data.get("continue_conversation")
    if isinstance(continue_conversation, bool):
        control.continue_conversation = continue_conversation

    conversation_id = data.get("conversation_id")
    if isinstance(conversation_id, str) and conversation_id:
        control.conversation_id = conversation_id

    return control


def apply_response_control(
    result: Any,
    control: ConversationResponseControl,
) -> Any:
    """Apply webhook-provided control metadata to a ConversationResult."""
    if control.continue_conversation is not None:
        result.continue_conversation = control.continue_conversation
    if control.conversation_id is not None:
        result.conversation_id = control.conversation_id
    return result
