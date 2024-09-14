from typing import List, TypedDict


class Reason(TypedDict):
    description: str

class Habit(TypedDict): 
    name: str 
    date: str
    reasons: List[Reason]

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
