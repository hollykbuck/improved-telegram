ui_mainwindow.py: mainwindow.ui
	pyside6-uic $? -o $@

clean:
	rm -f ui_mainwindow.py

all: ui_mainwindow.py

.PHONY: clean all