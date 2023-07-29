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