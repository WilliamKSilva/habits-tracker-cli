import click 
import os
import json
from random import randrange
from typing import IO, Any, List
from datetime import datetime

from cli_json import Habit, HabitsJson, QuotesJSON, Reason, LastQuote

def click_error(message: str):
    print(message)
    print("Aborted!")

def open_file(path: str, mode: str): 
    try: 
        return open(path, mode)
    except FileNotFoundError:
        return None
    except OSError as error:
        msg = f"Error trying to access file: {error}"
        click_error(msg)
        exit(1)

def create_file(path: str) -> IO[Any]:
    try:
        return open(path, "a")
    except OSError:
        msg = f"Error trying to create file {path}"
        click_error(msg)
        exit(1)

def write_to_file(data, f: IO[Any]):
    f.seek(0)
    f.write(data)
    f.truncate()

def add_habit(habit: Habit | None, habits_json: HabitsJson | None):
    if (habits_json == None):
        # User don't have any habits and did not passed the required first one
        if (habit == None):
            msg = f"You need to pass an initial habit to start tracking"
            click_error(msg)
            exit(1)

        new_habits_json: HabitsJson = {
            "habits": [habit]
        }

        f = create_file("habits.json")
        write_to_file(json.dumps(new_habits_json), f)
        f.close()
        return new_habits_json 

    if (habit == None):
        return habits_json

    f = open_file("habits.json", "r+")
    if (f == None):
        msg = f"Error trying to load habits file"
        click_error(msg)
        exit(1)

    habits_json["habits"].append(habit)
    write_to_file(json.dumps(habits_json), f)
    f.close()
    return habits_json

def load_habits_json() -> HabitsJson | None:
    f = open_file("habits.json", "r+")
    habits_json: HabitsJson = {
        "habits": []
    }

    if (f == None):
        return None

    json_loaded = json.load(f)
    habits_json["habits"] = json_loaded["habits"] 
    f.close()
    return habits_json

class State:
    habits_json: HabitsJson
    quotes_json: QuotesJSON

    def __init__(self, habit: Habit | None):
        # Try to load existing habits
        habits_json = load_habits_json()
        # Add habit if was passed and create the habits file if don't exist yet
        habits_json = add_habit(habit, habits_json)

        # If habits file still don't exist and wasn't loaded, something went wrong 
        if (habits_json == None):
            msg = f"Error trying to load habits_json data"
            click_error(msg)
            exit(1)

        self.habits_json = habits_json

        f = open_file("quotes.json", "r")
        if (f == None):
            print(f"Error trying to load quotes file")
            print("Aborted!")
            exit(1)

        self.quotes_json = json.load(f)
        f.close()

class Renderer:
    @staticmethod
    def render_greeting():
        username = Renderer.colored_text(os.getlogin(), "magenta") 
        greeting = f"Hello {username}"
        f = open_file("ascii.txt", "r")
        if (f == None):
            msg = f"Error trying to load ascii.txt file"
            click_error(msg)
            exit(1)

        ascii = f.read()
        click.echo(ascii)
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
    def render_reasons(habit_name: str, reasons: List[Reason]):
        reason_text = f"\n You decided to stop with {habit_name} because: \n"
        for r in reasons:
            desc = f" {r['description']}\n"
            reason_text += Renderer.colored_text(desc, "magenta") 
            click.echo(reason_text)

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

        f = open_file("quotes.json", "w")
        if (f == None):
            msg = f"Error trying to open quotes.json file"
            click_error(msg)
            exit(1)
        f.seek(0)
        f.write(updated_json)
        f.truncate()
        f.close()

    @staticmethod
    def colored_text(text: str, color: str): 
        return click.style(text, fg=color)

@click.command()
@click.option("--habit", help='The action or name of the habit, like: "drinking alcohol" or "smoking"')
def cli(habit):
    """A CLI app to track your bad habits"""
    habit_to_add: Habit = {
        "date": "",
        "name": "",
        "reasons": []
    }
    state: State | None = None

    if (habit):
        dsc = click.prompt("Type a reason for you to want to this habit")
        reason: Reason = {
            "description": dsc 
        }
        habit_to_add["reasons"].append(reason)
        habit_to_add["name"] = habit

        date = datetime.now()
        habit_to_add["date"] = date.strftime("%Y-%m-%d") 
        state = State(habit_to_add)
    else:
        state = State(None)

    Renderer.render_greeting()

    Renderer.render_habits(state.habits_json["habits"])
    for h in state.habits_json["habits"]:
        Renderer.render_reasons(h["name"], h["reasons"])

    Renderer.render_quote(state.quotes_json)

if __name__ == "__main__":
    cli()
