"""
qt-redux
"""

import logging, sys, os
from typing import Callable, Dict, List, Optional, Tuple, Union
from PySide6.QtCore import QObject, QAbstractListModel, Qt, Signal, Slot, QEvent
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QAbstractItemView,
    QListView,
)
from PySide6.QtGui import QStandardItemModel, QStandardItem, Qt, QImage
from ui_mainwindow import Ui_MainWindow

tick = QImage(
    os.path.join(
        "resource", "fontawesome-free-6.4.0-desktop", "svgs", "solid", "check.svg"
    )
)
# resize
tick = tick.scaled(
    16,
    16,
    Qt.AspectRatioMode.KeepAspectRatio,
    Qt.TransformationMode.SmoothTransformation,
)

class FilterBtn(QObject):
    def __init__(self, parent: QObject | None = ...) -> None:
        super().__init__(parent)
    
    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        match event.type():
            case QEvent.Type.Enter:
                print("hover enter")
                
            case QEvent.Type.Leave:
                print("hover leave")
        
        return super().eventFilter(watched, event)

class TodoModel(QAbstractListModel):
    def __init__(self, todos=None):
        super().__init__()
        self.todos = todos or []

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            status, text = self.todos[index.row()]
            return text

        if role == Qt.ItemDataRole.DecorationRole:
            status, _ = self.todos[index.row()]
            if status:
                return tick

    def rowCount(self, index):
        return len(self.todos)


class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.model = TodoModel()
        self.todoView.setModel(self.model)
        self.addButton.clicked.connect(self.add)
        self.deleteButton.clicked.connect(self.delete)
        self.completeButton.clicked.connect(self.complete)
        self.addButton.installEventFilter(FilterBtn(self))
        def enterEvent(event):
            self.addButton.setStyleSheet("""
background-color: #0b5ed7;
border-color: #0a58ca;
border-radius: 6px;
color: white;
font-size: 16px;
padding: 6px 12px;                
                                         """)
        def leaveEvent(event):
            self.addButton.setStyleSheet("""
background-color: #0d6efd;
border-color: #0b5ed7;
border-radius: 6px;
color: white;
font-size: 16px;
padding: 6px 12px;
                                         """)
        self.addButton.enterEvent = enterEvent
        self.addButton.leaveEvent = leaveEvent

    def add(self):
        """
        Add an item to our todo list, getting the text from the QLineEdit .todoEdit
        and then clearing it.
        """
        text = self.todoEdit.text()
        if text:  # Don't add empty strings.
            # Access the list via the model.
            self.model.todos.append((False, text))
            # Trigger refresh.
            self.model.layoutChanged.emit()
            # Empty the input
            self.todoEdit.setText("")

    def delete(self):
        indexes = self.todoView.selectedIndexes()
        if indexes:
            # Indexes is a list of a single item in single-select mode.
            index = indexes[0]
            # Remove the item and refresh.
            del self.model.todos[index.row()]
            self.model.layoutChanged.emit()
            # Clear the selection (as it is no longer valid).
            self.todoView.clearSelection()

    def complete(self):
        indexes = self.todoView.selectedIndexes()
        if indexes:
            index = indexes[0]
            row = index.row()
            status, text = self.model.todos[row]
            self.model.todos[row] = (True, text)
            # .dataChanged takes top-left and bottom right, which are equal
            # for a single selection.
            self.model.dataChanged.emit(index, index)
            # Clear the selection (as it is no longer valid).
            self.todoView.clearSelection()


app = QApplication(sys.argv)
window = MainWindow()
window.show()
app.exec()
