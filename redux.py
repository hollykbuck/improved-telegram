"""
A redux implementation in python. 
"""

import sys, os, json, signal
from typing import TypedDict, Callable

class State(TypedDict):
    count: int

state: State = {
    "count": 1
}

listeners = []

def subscribe(listener: "Callable"):
    listeners.append(listener)

def changeCount(count: int):
    state["count"] = count
    for listener in listeners:
        listener()

if __name__ == '__main__':
    subscribe(lambda: print("count changed to", state["count"]))
    changeCount(2)
    changeCount(3)
    changeCount(4)