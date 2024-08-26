import click 
import os
import io
from random import randrange
from typing import List, TypedDict
import json
import errno
from datetime import datetime

def open_file(path: str, mode: str): 
    try: 
        return open(path, mode)
    except OSError as error:
        if error.errno == errno.ENOENT:
            return None

        print(f"Error trying to open {path} file")
        print("Aborted!")
        exit(1)

def overwrite_file(data, f: io.TextIOWrapper):
    f.seek(0)
    f.write(data)
    f.truncate()

class Habit(TypedDict): 
    name: str 
    date: str

    def __init__(self, name: str, date: str):
        self.name = name
        self.date = date

class HabitsJson(TypedDict):
    habits: List[Habit]
    
class Quote:
    def __init__(self, name: str, content: str):
        self.name = name
        self.content = content 

class QuotesData:
    def __init__(self, quotes: List[Quote]):
        self.quotes = quotes
        self.last_quote = {
            "index": 0,
            "date": datetime.now().date
        }

class State:
    # current open file
    file: io.TextIOWrapper

    habits_json: HabitsJson = {
        "habits": []
    }

    quotes: QuotesData
    quotes_json: any

    def __init__(self, habit: Habit | None):
        self.file = open_file("habits.json", "r+")

        # User not registered some habit yet
        if (self.file == None and habit == None):
            print('You should add a habit first, like: cli.py --habit="drinking"')
            print("Aborted!")
            exit(1)

        if (habit):
            if (self.file == None):
                self.file = open_file("habits.json", "x")
                self.file.close()
                self.file = open_file("habits.json", "r+")
                self.habits_json["habits"].append(habit)
            else:
                self.habits_json = json.load(self.file)
                self.habits_json["habits"].append(habit)

            overwrite_file(json.dumps(self.habits_json), self.file)

            self.file.close()
        else:
            self.file = open_file("habits.json", "r")
            self.habits_json = json.load(self.file)
            self.file.close()

        self.file = open_file("quotes.json", "r")
        self.quotes_json = json.load(self.file)
        self.file.close()

def highlighted_text(text, color, fg: bool):
    if fg: 
        return click.style(text, fg=color)
    return click.style(text, bg=color)
def move_text(text: str, pos: int):
    return text.rjust(pos)

def render_greeting():
    username = f"Hello {os.getlogin()}"
    ascii_text = open_file("ascii.txt", "r")
    click.echo(ascii_text)
    click.echo(username)
    click.echo("\n")

def render_quote():
    # Every day we render a different random quote
    f_read = open_file("quotes.json", "r")
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

    f_write = open_file("quotes.json", "w")

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

@click.command()
@click.option("--habit", help='The action or name of the habit, like: "drinking alcohol" or "smoking"')
def cli(habit):
    """A CLI app to track your bad habits"""

    habit_to_add = Habit()
    if (habit):
        habit_to_add["name"] = habit

        date = datetime.now()
        habit_to_add["date"] = date.strftime("%Y-%m-%d") 
    else:
        habit_to_add = None

    state = State(habit_to_add)

    # habits = [
    #     {
    #         "name": "smoking",
    #         "date": "2024-08-16"
    #     },
    #     {
    #         "name": "drinking alcohol",
    #         "date": "2024-08-16"
    #     }
    # ]

    # render_greeting()
    
    # click.echo(" You are:")
    # for habit in habits:
    #     today = datetime.now()
    #     habit_date = datetime.fromisoformat(habit["date"])
    #     difference = today - habit_date
    #     name = habit["name"]
    #     plural = "days"
    #     singular = "day"
    #     days = highlighted_text(f" {difference.days} {plural if difference.days > 1 else singular}", "green", True)
    #     click.echo(move_text(f"{days} without {name}", 0))

    # render_quote()

if __name__ == "__main__":
    cli()
