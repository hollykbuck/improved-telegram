"""
A redux implementation in python. 
"""

import sys, os, json, signal, logging
from typing import TypedDict, Callable, TypeVar, Generic, cast, Optional

T = TypeVar("T")


class Action(Generic[T]):
    type: str

    def __init__(self, type: str, payload: T = None) -> None:
        self.type = type
        self.payload = payload

U = TypeVar("U")

class Store(Generic[T]):
    def __init__(
        self,
        initial_state: T,
        reducer: Callable[[T, Action], T],
    ):
        self._state = initial_state
        self._listeners = []
        self._reducer = reducer

    def subscribe(self, listener: Callable[[], None]):
        self._listeners.append(listener)

    def dispatch(self, action: Action[U]):
        self._state = self._reducer(self._state, action)
        for listener in self._listeners:
            listener()

    def getState(self) -> T:
        return self._state


def createStore(initialState: T, reducer: Callable[[T, Action], T]) -> Store[T]:
    return Store(initialState, reducer)


def combineReducers(
    reducers: dict[str, Callable[[T, Action], T]]
) -> Callable[[T, Action], T]:
    def combinedReducer(state: T, action: Action) -> T:
        nextState = state.copy()  # type: ignore
        for key, reducer in reducers.items():
            nextState[key] = reducer(state[key], action)  # type: ignore
        return nextState  # type: ignore

    return combinedReducer


def test1():
    return


def test2():
    initialState = {"counter": {"count": 0}, "info": {"name": "", "description": ""}}

    def subscribeInfo():
        state = store.getState()
        print("info: %s: %s" % (state["info"]["name"], state["info"]["description"]))

    def subscribeCounter():
        state = store.getState()
        print("counter: %d" % state["counter"]["count"])

    def counterReducer(state, action: Action):
        state = state.copy()
        if action.type == "increment":
            state["count"] += 1
        elif action.type == "decrement":
            state["count"] -= 1
        return state

    def infoReducer(state, action: Action):
        state = state.copy()
        if action.type == "setName":
            state["name"] = action.payload
        elif action.type == "setDescription":
            state["description"] = action.payload
        return state

    reducer = combineReducers({"counter": counterReducer, "info": infoReducer})
    store = createStore(initialState, reducer)
    store.subscribe(subscribeInfo)
    store.subscribe(subscribeCounter)
    store.dispatch(Action("setName", "redux"))
    store.dispatch(Action("setDescription", "a redux implementation in python"))
    store.dispatch(Action("increment"))


if __name__ == "__main__":
    # check first arg
    if len(sys.argv) < 2:
        print("Usage: python redux.py <testName>")
        sys.exit(1)
    match sys.argv[1]:
        case "test1":
            test1()
        case "test2":
            test2()
        case _:
            print("Unknown test name")
