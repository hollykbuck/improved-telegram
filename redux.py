"""
A redux implementation in python. 
"""

import sys, os, json, signal, logging
from typing import TypedDict, Callable, TypeVar, Generic, cast, Optional

T = TypeVar("T")

sentinel = {}


class Action(Generic[T]):
    type: str

    def __init__(self, type: str, payload: T = None) -> None:
        self.type = type
        self.payload = payload

    def __repr__(self) -> str:
        return json.dumps(self.__dict__)


U = TypeVar("U")


class Store(Generic[T]):
    def __init__(
        self,
        reducer: Callable[[T, Action], T],
    ):
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

    # def dispatch(self, action: Action[U]):
    #     self._state = self._reducer(self._state, action)
    #     for listener in self._listeners:
    #         listener()

    def getState(self) -> T:
        return self._state


def createStore(
    reducer: Callable[[T, Action], T],
    initState,
    rewriteCreateStoreFunc: Optional[Callable] = None,
) -> Store[T]:
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


def applyMiddleware(*middlewares):
    def rewriteCreateStoreFunc(oldCreateStore):
        def newCreateStore(reducer, initState):
            store = oldCreateStore(reducer, initState)
            chain = [middleware(store) for middleware in middlewares]
            dispatch = store.dispatch
            for middleware in reversed(chain):
                dispatch = middleware(dispatch)
            store.dispatch = dispatch
            return store

        return newCreateStore

    return rewriteCreateStoreFunc


def test1():
    return


def test2():
    def subscribeInfo():
        state = store.getState()
        # print("info: %s: %s" % (state["info"]["name"], state["info"]["description"]))
        logging.debug(
            "info: {}: {}".format(state["info"]["name"], state["info"]["description"])
        )

    def subscribeCounter():
        state = store.getState()
        # print("counter: %d" % state["counter"]["count"])
        logging.debug("counter: {}".format(state["counter"]["count"]))

    def counterReducer(state, action: Action):
        if not state:
            state = {"count": 0}
        else:
            state = state.copy()
        if action.type == "increment":
            state["count"] += 1
        elif action.type == "decrement":
            state["count"] -= 1
        return state

    def infoReducer(state, action: Action):
        if not state:
            state = {"name": "", "description": ""}
        else:
            state = state.copy()
        if action.type == "setName":
            state["name"] = action.payload
        elif action.type == "setDescription":
            state["description"] = action.payload
        return state

    def loggerMiddleware(store):
        def nextDispatch(next):
            def newDispatch(action):
                print("this state: {}".format(store.getState()))
                print("action: {}".format(action))
                next(action)
                print("next state: {}".format(store.getState()))

            return newDispatch

        return nextDispatch

    def exceptionMiddleware(store):
        def nextDispatch(next):
            def newDispatch(action):
                try:
                    next(action)
                except Exception as e:
                    print("error: {}".format(e))

            return newDispatch

        return nextDispatch

    reducer = combineReducers({"counter": counterReducer, "info": infoReducer})
    rewriteCreateStoreFunc = applyMiddleware(exceptionMiddleware, loggerMiddleware)
    store = createStore(reducer, None, rewriteCreateStoreFunc)
    store.subscribe(subscribeInfo)
    store.subscribe(subscribeCounter)
    store.dispatch(Action("setName", "redux"))
    store.dispatch(Action("setDescription", "a redux implementation in python"))
    store.dispatch(Action("increment"))


if __name__ == "__main__":
    # check first arg
    logging.basicConfig(level=logging.DEBUG)
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
