import asyncio
import json
import sys
import getpass
from rich.console import Console
from aiohttp_sse_client2 import client as sse_client

API_URL = "https://platform.donkit.ai/api/public/v2/chat-messages"
console = Console()


async def ask_question(prompt: str, api_key: str):
    headers = {
        "X-API-Key": api_key,
        "Accept": "text/event-stream",
        "Cache-Control": "no-cache",
    }
    payload = {
        "message": prompt,
    }

    async with sse_client.EventSource(
        API_URL,
        option={"method": "POST"},
        json=payload,
        headers=headers,
    ) as event_source:
        try:
            async for event in event_source:
                try:
                    data = json.loads(event.data)
                except json.JSONDecodeError:
                    continue

                event_type = data.get("event")

                if event_type == "message changed":
                    msg = data.get("message", "")
                    sys.stdout.write(msg)
                    sys.stdout.flush()
                elif event_type == "documents changed":
                    console.print("\n[yellow]Documents updated:[/yellow]", data.get("documents"))
                elif event_type == "followup changed":
                    console.print("\n[cyan]Follow-up suggestions:[/cyan]", data.get("followup_questions"))
                elif event_type == "end":
                    console.print(f"\n[green]--- Response complete (answer_id={data.get('answer_id')}) ---[/green]\n")
                    break
        except ConnectionError as e:
            console.print(f"\n[red]Error: {e}")


async def main():
    console.print("[bold cyan]Donkit Chat CLI (async)[/bold cyan]")
    api_key = getpass.getpass("Enter API Token: ")

    while True:
        try:
            question = input("\n[You] > ").strip()
            if not question:
                continue
            if question.lower() in {"exit", "quit"}:
                console.print("[yellow]Bye![/yellow]")
                break
            await ask_question(question, api_key)
        except KeyboardInterrupt:
            console.print("\n[yellow]Bye![/yellow]")
            break


if __name__ == "__main__":
    asyncio.run(main())

