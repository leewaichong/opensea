from pmle.schemas import BoardState
from pmle.data.agenda import AGENDA

_EMOJI = {"agreed": ":white_check_mark:", "crux": ":red_circle:",
          "fake_agreement": ":large_orange_circle:", "needs_clarification": ":large_blue_circle:",
          "open": ":white_circle:"}

# Items that still need the live meeting · items nobody weighed in on · items resolved into
# the pre-read. "open" (no stance collected) is its OWN bucket — never consensus.
_DISCUSS = ("crux", "fake_agreement", "needs_clarification")
_NO_INPUT = ("open",)
_RESOLVED = ("agreed",)
_AGENDA_TEXT = {a.id: a.text for a in AGENDA}


def _no_input_lines(board: BoardState, agenda_text: dict | None = None) -> list[str]:
    """Agenda items no participant addressed — flagged, not folded into consensus."""
    text_for = agenda_text or _AGENDA_TEXT
    return [f":white_circle: *{i.item_id}* — {text_for.get(i.item_id) or i.summary}"
            for i in board.items if i.status in _NO_INPUT]


def _summary_parts(board: BoardState) -> list[str]:
    """Footer counts derived from the actual items — not the action-item framing, which is
    empty (and misleading) in dynamic mode. Action items only appear if there are any."""
    need = sum(1 for i in board.items if i.status in _DISCUSS)
    agreed = sum(1 for i in board.items if i.status in _RESOLVED)
    waiting = sum(1 for i in board.items if i.status in _NO_INPUT)
    parts = [f"{need} for the meeting", f"{agreed} already aligned"]
    if waiting:
        parts.append(f"{waiting} awaiting input")
    cleared = sum(1 for a in board.action_items if a.status == "resolved")
    needs_owner = sum(1 for a in board.action_items if a.status == "needs_owner")
    if cleared:
        parts.append(f"{cleared} action items cleared")
    if needs_owner:
        parts.append(f"{needs_owner} action items need an owner")
    return parts


def _consensus_lines(board: BoardState, agenda_text: dict | None = None) -> list[str]:
    """Items the group is already aligned on: agreed agenda items (by their agenda text) +
    any resolved action items (by their resolution, with who cleared them). The pre-read."""
    text_for = agenda_text or _AGENDA_TEXT
    lines = []
    for i in board.items:
        if i.status in _RESOLVED:
            label = text_for.get(i.item_id) or i.summary
            lines.append(f":white_check_mark: *{i.item_id}* — {label}")
    for a in board.action_items:
        if a.status == "resolved":
            who = f"  _({', '.join(a.resolved_by)})_" if a.resolved_by else ""
            lines.append(f":white_check_mark: {a.resolution or a.text}{who}")
    return lines


def render_text(board: BoardState, agenda_text: dict | None = None) -> str:
    n = board.meeting_item_count()
    lines = [f"PerMyLastEmail — {board.decision}",
             f"Agenda compressed: {len(board.items)} → {n} items need a meeting", ""]

    lines.append("Needs the live meeting:")
    for i in board.items:
        if i.status in _DISCUSS:
            lines.append(f"  {_EMOJI[i.status]} {i.item_id}: {i.summary}"
                         + (f"  [{i.divergence}]" if i.divergence else ""))

    noinput = _no_input_lines(board, agenda_text)
    if noinput:
        lines.append("")
        lines.append("No input yet:")
        lines.extend("  " + c.replace("*", "") for c in noinput)

    cons = _consensus_lines(board, agenda_text)
    if cons:
        lines.append("")
        lines.append("Already aligned — skip in the meeting:")
        lines.extend("  " + c.replace("*", "") for c in cons)

    no_owner = [a for a in board.action_items if a.status == "needs_owner"]
    for a in no_owner:
        lines.append(f"  :warning: needs owner — {a.text}")
    lines.append("")
    lines.append("Summary: " + ", ".join(_summary_parts(board)))
    lines.append(f"Decision owner: {board.owner}")
    return "\n".join(lines)


def _section(text: str) -> dict:
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def render_blocks(board: BoardState, agenda_text: dict | None = None) -> list[dict]:
    n = board.meeting_item_count()
    blocks = [
        {"type": "header", "text": {"type": "plain_text",
         "text": f"Pre-meeting: {len(board.items)} → {n} items"}},
        _section(f"*{board.decision}*"),
        {"type": "divider"},
    ]

    discuss = [i for i in board.items if i.status in _DISCUSS]
    if discuss:
        blocks.append(_section("*:rotating_light: Needs the live meeting*"))
        for i in discuss:
            txt = f"{_EMOJI[i.status]} *{i.item_id}* — {i.summary}"
            if i.divergence:
                txt += f"\n> {i.divergence}"
            blocks.append(_section(txt))

    noinput = _no_input_lines(board, agenda_text)
    if noinput:
        blocks.append({"type": "divider"})
        blocks.append(_section("*:white_circle: No input yet — nobody weighed in*"))
        blocks.append(_section("\n".join(noinput)))

    cons = _consensus_lines(board, agenda_text)
    if cons:
        blocks.append({"type": "divider"})
        blocks.append(_section("*:white_check_mark: Already aligned — skip in the meeting*"))
        blocks.append(_section("\n".join(cons)))

    for a in board.action_items:
        if a.status == "needs_owner":
            blocks.append(_section(f":warning: *needs owner* — {a.text}"))

    owner = board.owner or "—"
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn",
        "text": f"Owner: *{owner}* · " + " · ".join(_summary_parts(board))}]})
    return blocks
