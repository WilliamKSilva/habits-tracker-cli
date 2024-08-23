import click 
import os
from datetime import datetime

def highlighted_text(text, color, fg: bool):
    if fg: 
        return click.style(text, fg=color)
    return click.style(text, bg=color)

def move_text(text: str, pos: int):
    return text.rjust(pos)

def read_file(path: str): 
    try: 
        return open(path).read()
    except OSError:
        print(f"Error trying to open {path} file")
        exit(-1)

def cli():
    habits = [
        {
            "name": "smoking",
            "date": "2024-08-16"
        },
        {
            "name": "drinking alchool",
            "date": "2024-08-16"
        }
    ]

    username = highlighted_text(f"Hello {os.getlogin()}", 'magenta', True)
    greeting_text = move_text(username, 0)
    ascii_text = read_file("ascii.txt")
    click.echo(ascii_text)
    click.echo(greeting_text)
    click.echo("\n")
    click.echo("You are:")

    for habit in habits:
        today = datetime.now()
        habit_date = datetime.fromisoformat(habit["date"])
        difference = today - habit_date
        name = habit["name"]
        plural = "days"
        singular = "day"
        days = highlighted_text(f"{difference.days} {plural if difference.days > 1 else singular}", "green", True)
        click.echo(move_text(f"{days} without {name}", 0))
cli()

