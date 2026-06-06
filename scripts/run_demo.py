import asyncio
from pmle import orchestrator
from pmle.digest import render_text

async def main():
    board = await orchestrator.run_meeting()
    print(render_text(board))

if __name__ == "__main__":
    asyncio.run(main())
