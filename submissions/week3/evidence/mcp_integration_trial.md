# MCP Integration Trial Evidence

## Trial Goal

Connect one local/tool MCP-style capability in both an IDE workflow and a CLI
workflow, then confirm that the agent can call a tool and return structured
output.

## IDE Context

Environment:

```text
VSCode / IDE agent workflow
Project: ShiftNotes
Tool target: local file/system tool access for repository inspection
```

Successful call transcript:

```text
Prompt: Inspect the ShiftNotes repo and identify the files related to MCP,
Gmail ingestion, and briefing delivery.

Tool call: repository text search

Observed output:
- ARCHITECTURE.md documents Gmail MCP integration points.
- SPEC.MD documents planned MCP swaps for ingest_email and send_briefing.
- shiftnotes_agent/nodes/ingest_email.py includes Gmail MCP fallback behavior.
- shiftnotes_agent/nodes/send_briefing.py includes Gmail MCP send fallback.
```

## CLI Context

Environment:

```text
Claude Code / CLI workflow
Project: ShiftNotes
Tool target: local shell and file tools
```

Successful call transcript:

```text
Command:
rg -n "MCP|Gmail|send_briefing|ingest_email" ARCHITECTURE.md SPEC.MD shiftnotes_agent

Observed result:
ARCHITECTURE.md identifies Node 1 as Gmail/MCP ingestion and Node 5 as
Gmail/MCP briefing delivery.

SPEC.MD documents the MCP integration plan and fallback behavior.

shiftnotes_agent/nodes/ingest_email.py and send_briefing.py contain the
implementation placeholders/fallbacks.
```

## Observed Limitation

The trial showed that tool calls can expose project context, but production
Gmail access still requires account authorization, OAuth configuration, and
privacy review. This is why the final ShiftNotes prototype moved toward JotForm
API ingestion and local reproducible fixtures while documenting Gmail delivery
as future production work.

## Sprint 2 Impact

The MCP trial changed the implementation strategy:

- MCP was treated as an integration boundary, not the core intelligence layer.
- The project kept fallback paths so the prototype could run without live Gmail
  credentials.
- Source validation remained inside ShiftNotes even when external tools were
  used.
