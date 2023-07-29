"""
A redux implementation in python. 
"""

import sys, os, json, signal, logging
from typing import (
    TypedDict,
    Callable,
    TypeVar,
    Generic,
    cast,
    Optional,
    Protocol,
    Any,
    runtime_checkable,
    overload,
)
from functools import reduce

T = TypeVar("T")

sentinel = {}


def compose(*funcs):
    if not funcs:
        return lambda arg: arg
    if len(funcs) == 1:
        return funcs[0]
    return reduce(lambda f, g: lambda *args, **kwargs: f(g(*args, **kwargs)), funcs)


class Action(Generic[T]):
    type: str

    def __init__(self, type: str, payload: T = None) -> None:
        self.type = type
        self.payload = payload

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)


class SupportsGetState(Protocol):
    def getState(self):
        ...


class Store(SupportsGetState):
    def __init__(self, reducer: Callable[[Any, Action], Any]):
        self._state = {}  # type: ignore
        self._listeners = []
        self._reducer = reducer

        def dispatch(action):
            self._state = self._reducer(self._state, action)
            for listener in self._listeners:
                listener()

        self.dispatch = dispatch
        self.dispatch(Action(sentinel))  # type: ignore

    def subscribe(self, listener: Callable[[], None]):
        self._listeners.append(listener)

        def unsubscribe():
            self._listeners.remove(listener)

        return unsubscribe

    def getState(self):
        return self._state

    def replaceReducer(self, reducer: Callable[[Any, Action], Any]):
        self._reducer = reducer
        self.dispatch(Action(sentinel))  # type: ignore


def createStore(
    reducer: Callable[[T, Action], T],
    initState,
    rewriteCreateStoreFunc: Optional[Callable] = None,
) -> Store:
    if isinstance(initState, Callable):
        rewriteCreateStoreFunc = cast(Callable, initState)
        initState = None
    if rewriteCreateStoreFunc:
        newCreateStore = rewriteCreateStoreFunc(createStore)
        return newCreateStore(reducer, initState)
    return Store(reducer)


def combineReducers(
    reducers: dict[str, Callable[[T, Action], T]]
) -> Callable[[T, Action], T]:
    def combinedReducer(state: T, action: Action) -> T:
        nextState = state.copy()  # type: ignore
        for key, reducer in reducers.items():
            nextState[key] = reducer(state[key] if key in state else None, action)  # type: ignore
        return nextState  # type: ignore

    return combinedReducer


class SimpleStore(SupportsGetState):
    def __init__(self, getState: Callable[[], Any]) -> None:
        self.getState = getState


def applyMiddleware(*middlewares):
    def rewriteCreateStoreFunc(oldCreateStore):
        def newCreateStore(reducer, initState):
            store = oldCreateStore(reducer, initState)
            simpleStore = SimpleStore(store.getState)
            chain = [middleware(simpleStore) for middleware in middlewares]
            dispatch = store.dispatch
            for middleware in reversed(chain):
                dispatch = middleware(dispatch)
            store.dispatch = dispatch
            return store

        return newCreateStore

    return rewriteCreateStoreFunc


def bindActionCreator(actionCreator, dispatch):
    return lambda *args, **kwargs: dispatch(actionCreator(*args, **kwargs))


def bindActionCreators(actionCreators, dispatch):
    if isinstance(actionCreators, Callable):
        return bindActionCreator(actionCreators, dispatch)
    if isinstance(actionCreators, dict):
        boundActionCreators = {}
        for key, actionCreator in actionCreators.items():
            if isinstance(actionCreator, Callable):
                boundActionCreators[key] = bindActionCreator(actionCreator, dispatch)
        return boundActionCreators
    raise Exception(
        "bindActionCreators expected a function or a object with actionCreators"
    )