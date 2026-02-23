"""Warm up the Ollama model by sending a simple message."""

import click

from llm import OllamaAPI


@click.command()
def warmup() -> None:
    api = OllamaAPI()
    click.echo(f"Loading model {api.model}...")
    api.chat(
        model=api.model,
        messages=[{"role": "user", "content": "Hi"}],
        keep_alive="60m",
    )
    click.echo(f"Model {api.model} ready.")


if __name__ == "__main__":
    warmup()
