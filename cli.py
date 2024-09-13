import click 
import os
import io
from random import randrange
from typing import IO, Any, List, TypedDict
import json
from datetime import datetime

def open_file(path: str, mode: str): 
    try: 
        return open(path, mode)
    except OSError:
        print(f"Error trying to open {path} file")
        print("Aborted!")
        exit(1)

def overwrite_file(data, f: IO[Any]):
    f.seek(0)
    f.write(data)
    f.truncate()

class Habit(TypedDict): 
    name: str 
    date: str

class HabitsJson(TypedDict):
    habits: List[Habit]

class Quote(TypedDict): 
    name: str 
    content: str

class LastQuote(TypedDict):
    index: int
    date: str

class QuotesJSON(TypedDict):
    last_quote: LastQuote
    quotes: List[Quote]

class State:
    habits_json: HabitsJson

    quotes_json: QuotesJSON

    def __init__(self, habit: Habit | None):
        file = open_file("habits.json", "r+")
        # User not registered some habit yet
        if (file == None and habit == None):
            print('You should add a habit first, like: cli.py --habit="drinking"')
            print("Aborted!")
            exit(1)

        if (habit):
            if (file == None):
                file = open_file("habits.json", "x")
                file.close()
                file = open_file("habits.json", "r+")
                self.habits_json["habits"].append(habit)
            else:
                self.habits_json = json.load(file)
                self.habits_json["habits"].append(habit)

            overwrite_file(json.dumps(self.habits_json), file)

            file.close()
        else:
            file = open_file("habits.json", "r")
            self.habits_json = json.load(file)
            file.close()

        file = open_file("quotes.json", "r")
        self.quotes_json = json.load(file)
        file.close()

class Renderer:
    @staticmethod
    def render_greeting():
        username = Renderer.colored_text(os.getlogin(), "magenta") 
        greeting = f"Hello {username}"
        f = open_file("ascii.txt", "r").read()
        click.echo(f)
        click.echo(greeting)
        click.echo("\n")

    @staticmethod
    def render_habits(habits: List[Habit]):
        click.echo(" You are:")
        for habit in habits:
            today = datetime.now()
            habit_date = datetime.fromisoformat(habit["date"])
            difference = today - habit_date
            name = habit["name"]
            plural = "days"
            singular = "day"
            days = f" {difference.days} {singular if (difference.days == 1) else plural}"
            habit_text = Renderer.colored_text(f"{days} without {name}", "green")
            click.echo(habit_text)

    @staticmethod
    def render_quote(quotes_json: QuotesJSON):
        # Every day we render a different random quote
        last_quote_date = datetime.fromisoformat(quotes_json["last_quote"]["date"])
        last_quote_index = quotes_json["last_quote"]["index"]
        quotes = quotes_json["quotes"]
        quote = quotes[last_quote_index]

        if ((datetime.now() - last_quote_date).days == 0):
            click.echo("\n")
            quote_content_text = Renderer.colored_text(quote["content"], "blue")
            click.echo(quote_content_text)

            quote_name_text = Renderer.colored_text(quote["name"], "blue")
            click.echo(f'-- {quote_name_text} --')
            return

        rand_quote_index = randrange(0, len(quotes))
        while (rand_quote_index == last_quote_index):
            rand_quote_index = randrange(0, len(quotes)) == last_quote_index

        quote = quotes[rand_quote_index]

        click.echo("\n")
        quote_content_text = Renderer.colored_text(quote["content"], "blue")
        click.echo(quote_content_text)

        quote_name_text = Renderer.colored_text(quote["name"], "blue")
        click.echo(f'-- {quote_name_text} --')

        # Update last_quote info
        last_quote: LastQuote = {
            "date": datetime.now().date().isoformat(),
            "index": rand_quote_index
        }

        quotes_json["last_quote"] = last_quote
        updated_json = json.dumps(quotes_json)

        file = open_file("quotes.json", "w")
        file.seek(0)
        file.write(updated_json)
        file.truncate()
        file.close()

    @staticmethod
    def colored_text(text: str, color: str): 
        return click.style(text, fg=color)

@click.command()
@click.option("--habit", help='The action or name of the habit, like: "drinking alcohol" or "smoking"')
def cli(habit):
    """A CLI app to track your bad habits"""

    habit_to_add: Habit = {
        "date": "",
        "name": ""
    }
    if (habit):
        habit_to_add["name"] = habit

        date = datetime.now()
        habit_to_add["date"] = date.strftime("%Y-%m-%d") 

    state = State(habit_to_add)

    Renderer.render_greeting()

    Renderer.render_habits(state.habits_json["habits"])

    Renderer.render_quote(state.quotes_json)

if __name__ == "__main__":
    cli()
