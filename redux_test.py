from redux import createStore, Store
from typing import TypedDict, Callable, TypeVar, Generic
import logging, unittest

class TestRedux(unittest.TestCase):
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)
    def setUp(self):
        class Counter(TypedDict):
            count: int
        class Info(TypedDict):
            name: str
            description: str
        class State(TypedDict):
            counter: Counter
            info: Info
        
        initState: State = {"counter": {"count": 0}, "info": {"name": "", "description": ""}}
        self.store = createStore(initState)

    def test_createStore(self):
        self.assertEqual(self.store.getState(), {"counter": {"count": 0}, "info": {"name": "", "description": ""}})

    def test_subscribe(self):
        def subscribeInfo():
            state = self.store.getState()
            self.logger.info(
                "info: %s: %s", state["info"]["name"], state["info"]["description"]
            )

        def subscribeCounter():
            state = self.store.getState()
            self.logger.info("counter: %d", state["counter"]["count"])

        self.store.subscribe(subscribeInfo)
        self.store.subscribe(subscribeCounter)

    def test_changeState(self):
        def subscribeInfo():
            state = self.store.getState()
            self.logger.info(
                "info: %s: %s", state["info"]["name"], state["info"]["description"]
            )

        def subscribeCounter():
            state = self.store.getState()
            self.logger.info("counter: %d", state["counter"]["count"])

        self.store.subscribe(subscribeInfo)
        self.store.subscribe(subscribeCounter)
        state = self.store.getState().copy()
        state["info"]["name"] = "redux"
        state["info"]["description"] = "a redux implementation in python"
        self.store.changeState(state)
        self.assertEqual(self.store.getState(), {'counter': {'count': 0}, 'info': {'name': 'redux', 'description': 'a redux implementation in python'}})

def test2():
    def subscribeInfo():
        state = store.getState()
        logging.debug(
            "info: {}: {}".format(state["info"]["name"], state["info"]["description"])
        )

    def subscribeCounter():
        state = store.getState()
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
    store = createStore(reducer, rewriteCreateStoreFunc)
    unsub = store.subscribe(subscribeInfo)
    store.subscribe(subscribeCounter)
    store.dispatch(Action("setName", "redux"))
    store.dispatch(Action("setDescription", "a redux implementation in python"))
    store.dispatch(Action("increment"))

    def increment():
        return Action("increment")

    def setName(name):
        return Action("setName", name)

    actions = cast(
        dict[str, Callable],
        bindActionCreators(
            {"increment": increment, "setName": setName}, store.dispatch
        ),
    )
    actions["increment"]()
    actions["setName"]("redux")
