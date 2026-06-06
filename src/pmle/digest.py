from pmle.schemas import BoardState
from pmle.data.agenda import AGENDA

_EMOJI = {"agreed": ":white_check_mark:", "crux": ":red_circle:",
          "fake_agreement": ":large_orange_circle:", "needs_clarification": ":large_blue_circle:",
          "open": ":white_circle:"}

# Items that still need the live meeting vs. items the bot resolved into the pre-read.
_DISCUSS = ("crux", "fake_agreement", "needs_clarification")
_RESOLVED = ("agreed", "open")
_AGENDA_TEXT = {a.id: a.text for a in AGENDA}


def _consensus_lines(board: BoardState) -> list[str]:
    """The async-resolved consensus: agreed agenda items (by their agenda text) + resolved
    action items (by their resolution, with who cleared them). This is the pre-read."""
    lines = []
    for i in board.items:
        if i.status in _RESOLVED:
            label = _AGENDA_TEXT.get(i.item_id, i.summary)
            lines.append(f":white_check_mark: *{i.item_id}* — {label}")
    for a in board.action_items:
        if a.status == "resolved":
            who = f"  _({', '.join(a.resolved_by)})_" if a.resolved_by else ""
            lines.append(f":white_check_mark: {a.resolution or a.text}{who}")
    return lines


def render_text(board: BoardState) -> str:
    n = board.meeting_item_count()
    lines = [f"PerMyLastEmail — {board.decision}",
             f"Agenda compressed: {len(board.items)} → {n} items need a meeting", ""]

    lines.append("Needs the live meeting:")
    for i in board.items:
        if i.status in _DISCUSS:
            lines.append(f"  {_EMOJI[i.status]} {i.item_id}: {i.summary}"
                         + (f"  [{i.divergence}]" if i.divergence else ""))

    cons = _consensus_lines(board)
    if cons:
        lines.append("")
        lines.append("Resolved async — pre-read consensus:")
        lines.extend("  " + c.replace("*", "") for c in cons)

    lines.append("")
    res = sum(1 for a in board.action_items if a.status == "resolved")
    no_owner = [a for a in board.action_items if a.status == "needs_owner"]
    lines.append(f"Action items: {res} resolved, {len(no_owner)} need an owner")
    for a in no_owner:
        lines.append(f"  :warning: {a.text}")
    lines.append(f"\nDecision owner: {board.owner} (owner call with logged dissents)")
    return "\n".join(lines)


def _section(text: str) -> dict:
    return {"type": "section", "text": {"type": "mrkdwn", "text": text}}


def render_blocks(board: BoardState) -> list[dict]:
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

    cons = _consensus_lines(board)
    if cons:
        blocks.append({"type": "divider"})
        blocks.append(_section("*:white_check_mark: Resolved async — pre-read consensus*"))
        blocks.append(_section("\n".join(cons)))

    no_owner = [a for a in board.action_items if a.status == "needs_owner"]
    for a in no_owner:
        blocks.append(_section(f":warning: *needs owner* — {a.text}"))

    res = sum(1 for a in board.action_items if a.status == "resolved")
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn",
        "text": f"Decision owner: *{board.owner}* · {res} resolved · {len(no_owner)} need an owner"}]})
    return blocks
