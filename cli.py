import click 
import os
from random import randrange
import json
from datetime import datetime

def highlighted_text(text, color, fg: bool):
    if fg: 
        return click.style(text, fg=color)
    return click.style(text, bg=color)
def move_text(text: str, pos: int):
    return text.rjust(pos)

# TODO: mode type should be OpenTextMode
def open_file(path: str, mode: str, read_content: bool): 
    try: 
        f = open(path, mode)

        if (read_content):
            data = f.read()
            f.close()
            return data

        return f
    except OSError:
        print(f"Error trying to open {path} file")
        exit(-1)

def render_greeting():
    username = highlighted_text(f"Hello {os.getlogin()}", 'magenta', True)
    greeting_text = move_text(username, 0)
    ascii_text = open_file("ascii.txt", "r", read_content=True)
    click.echo(ascii_text)
    click.echo(greeting_text)
    click.echo("\n")

def render_quote():
    # Every day we render a different random quote

    f_read = open_file("quotes.json", "r", read_content=False)
    # read+write mode don't work with json.load 
    quotes_data = json.load(f_read)
    f_read.close()

    last_quote_date = datetime.fromisoformat(quotes_data["last_quote"]["date"])
    last_quote_index = quotes_data["last_quote"]["index"]
    quotes = quotes_data["quotes"]
    quote = quotes[last_quote_index]

    if ((datetime.now() - last_quote_date).days == 0):
        click.echo("\n")
        click.echo(highlighted_text(text=quote["content"], color="blue", fg=True))

        name = highlighted_text(text=quote["name"], color="blue", fg=True)
        click.echo(f'-- {name} --')
        return

    rand_quote_index = randrange(0, len(quotes))
    while (rand_quote_index == last_quote_index):
        rand_quote_index = randrange(0, len(quotes)) == last_quote_index

    f_write = open_file("quotes.json", "w", read_content=False)

    quote = quotes[rand_quote_index]

    click.echo("\n")
    click.echo(highlighted_text(text=quote["content"], color="blue", fg=True))

    name = highlighted_text(text=quote["name"], color="blue", fg=True)
    click.echo(f'-- {name} --')

    # Update last_quote info
    last_quote = {
        "date": datetime.now().date().isoformat(),
        "index": rand_quote_index
    }

    quotes_data["last_quote"] = last_quote

    updated_json = json.dumps(quotes_data)
    f_write.seek(0)
    f_write.write(updated_json)
    f_write.truncate()
    f_write.close()

def cli():
    habits = [
        {
            "name": "smoking",
            "date": "2024-08-16"
        },
        {
            "name": "drinking alcohol",
            "date": "2024-08-16"
        }
    ]

    render_greeting()
    
    click.echo(" You are:")
    for habit in habits:
        today = datetime.now()
        habit_date = datetime.fromisoformat(habit["date"])
        difference = today - habit_date
        name = habit["name"]
        plural = "days"
        singular = "day"
        days = highlighted_text(f" {difference.days} {plural if difference.days > 1 else singular}", "green", True)
        click.echo(move_text(f"{days} without {name}", 0))

    render_quote()
cli()

