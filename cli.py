import click 
import os
import json
from random import randrange
from typing import IO, Any, List
from datetime import datetime

from cli_json import Habit, HabitsJson, QuotesJSON, Reason, LastQuote

def open_file(path: str, mode: str): 
    try: 
        return open(path, mode)
    except FileNotFoundError:
        return None
    except OSError as error:
        print(f"Error trying to access file: {error}")
        print("Aborted!")
        exit(1)

def create_file(path: str):
    try:
        return open(path, "a")
    except OSError:
        print(f"Error trying to create file {path}")
        print("Aborted!")
        exit(1)

def write_to_file(data, f: IO[Any]):
    f.seek(0)
    f.write(data)
    f.truncate()

def add_habit(habit: Habit | None, habits_json: HabitsJson | None):
    if (habits_json == None):
        # User don't have any habits and did not passed the required first one
        if (habit == None):
            print(f"You need to pass an initial habit to start tracking")
            print("Aborted!")
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
        print(f"Error trying to load habits file")
        print("Aborted!")
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

    habits_json["habits"] = json.load(f)
    f.close()
    return habits_json

class State:
    habits_json: HabitsJson
    quotes_json: QuotesJSON

    def __init__(self, habit: Habit | None):
        habits_json = load_habits_json()
        habits_json = add_habit(habit, habits_json)

        if (habits_json == None):
            print(f"Error trying to load habits_json data")
            print("Aborted!")
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
            print(f"Error trying to load ascii.txt file")
            print("Aborted!")
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
        "name": "",
        "reasons": []
    }
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

    Renderer.render_greeting()

    Renderer.render_habits(state.habits_json["habits"])

    Renderer.render_quote(state.quotes_json)

if __name__ == "__main__":
    cli()
