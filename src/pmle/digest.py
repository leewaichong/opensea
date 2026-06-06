from pmle.schemas import BoardState

_EMOJI = {"agreed": ":white_check_mark:", "crux": ":red_circle:",
          "fake_agreement": ":large_orange_circle:", "needs_clarification": ":large_blue_circle:",
          "open": ":white_circle:"}


def render_text(board: BoardState) -> str:
    n = board.meeting_item_count()
    lines = [f"PerMyLastEmail — {board.decision}",
             f"Agenda compressed: {len(board.items)} → {n} items need a meeting", ""]
    for i in board.items:
        if i.status in ("crux", "fake_agreement"):
            lines.append(f"  {_EMOJI[i.status]} {i.item_id}: {i.summary}"
                         + (f"  [{i.divergence}]" if i.divergence else ""))
    lines.append("")
    res = sum(1 for a in board.action_items if a.status == "resolved")
    no_owner = [a for a in board.action_items if a.status == "needs_owner"]
    lines.append(f"Action items: {res} resolved, {len(no_owner)} need an owner")
    for a in no_owner:
        lines.append(f"  :warning: {a.text}")
    lines.append(f"\nDecision owner: {board.owner} (owner call with logged dissents)")
    return "\n".join(lines)


def render_blocks(board: BoardState) -> list[dict]:
    n = board.meeting_item_count()
    blocks = [
        {"type": "header", "text": {"type": "plain_text",
         "text": f"Pre-meeting: {len(board.items)} → {n} items"}},
        {"type": "section", "text": {"type": "mrkdwn", "text": f"*{board.decision}*"}},
        {"type": "divider"},
    ]
    for i in board.items:
        if i.status in ("crux", "fake_agreement"):
            txt = f"{_EMOJI[i.status]} *{i.item_id}* — {i.summary}"
            if i.divergence:
                txt += f"\n> {i.divergence}"
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": txt}})
    res = sum(1 for a in board.action_items if a.status == "resolved")
    no_owner = sum(1 for a in board.action_items if a.status == "needs_owner")
    blocks.append({"type": "context", "elements": [{"type": "mrkdwn",
        "text": f"*Action items:* {res} resolved · {no_owner} need an owner"}]})
    return blocks
