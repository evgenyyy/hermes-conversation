# Hermes Conversation

Home Assistant custom integration for routing Assist / Conversation requests to a webhook with Hermes-friendly response control.

This is a Hermes-oriented fork/variant of Webhook Conversation. The key difference is that streaming webhook responses can control Home Assistant's final `ConversationResult`, including `continue_conversation`.

## Why

The stock Webhook Conversation streaming path treats every streamed `item` chunk as assistant speech and then lets Home Assistant infer the final result from the chat log. That means fields like `continue_conversation` cannot be controlled by the webhook.

Hermes voice flows need a richer protocol:

- progress/status chunks should not accidentally close the Assist run
- the final spoken answer should be short and TTS-friendly
- the webhook should be able to request `continue_conversation: true`
- rich details can still be sent separately to Telegram by Hermes

## HACS installation from this repository

Until this is published in the default HACS store:

1. In Home Assistant, open **HACS**.
2. Open the three-dot menu → **Custom repositories**.
3. Add this repository URL:

   ```text
   https://github.com/evgenyyy/hermes-conversation
   ```

4. Category: **Integration**.
5. Install **Hermes Conversation**.
6. Restart Home Assistant.
7. Go to **Settings → Devices & services → Add integration** and search for **Hermes Conversation**.
8. Add a **Conversation Agent** subentry pointing at your Hermes bridge URL, for example:

   ```text
   http://192.168.1.112:3210/ha/conversation
   ```

## Streaming response protocol

Responses are newline-delimited JSON. Existing Webhook Conversation chunks still work:

```json
{"type":"item","content":"Short spoken answer."}
{"type":"end"}
```

Hermes Conversation additionally reads response-control metadata from any chunk:

```json
{"type":"item","content":"Short spoken answer.","continue_conversation":true}
{"type":"end"}
```

Or as a metadata-only final/control chunk:

```json
{"type":"item","content":"Short spoken answer."}
{"type":"final","continue_conversation":true}
{"type":"end"}
```

Supported control fields:

- `continue_conversation`: boolean; overrides Home Assistant's final `ConversationResult.continue_conversation`
- `conversation_id`: string; overrides the final result conversation ID

Invalid control metadata is ignored to preserve compatibility.

## Non-streaming response protocol

For non-streaming mode, include the normal output field plus optional control metadata:

```json
{
  "output": "Short spoken answer.",
  "continue_conversation": true
}
```

## Development checks

```bash
python3 -m pytest tests/test_response_control.py -q
python3 -m py_compile custom_components/hermes_conversation/*.py
ruff check custom_components/hermes_conversation tests
```

## Credits

Based on the excellent Webhook Conversation integration by Lennard Beers / EuleMitKeule, adapted for Hermes-specific Home Assistant voice semantics.
