from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
import pyqtgraph as pg
from datetime import datetime
import json
import sys
import os

from utils import *

basedir = os.path.dirname(__file__)

# JSON file things
SYMBOLS_FILE = os.path.join(basedir, "Resources/symbols.json")

COLS = ["Open",
        "High",
        "Low",
        "Close",
        "Volume",
        "Dividends",
        "Stock Splits"]

# Styles for plots
COLOR = ["#f00",
         "#0f0",
         "#00f",
         "#088",
         "#808",
         "#880",
         "#000"]

# Fonts
boldFont = QFont()
boldFont.setBold(True)

class AddWindow(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Another Window % d" % randint(0, 100))
        layout.addWidget(self.label)
        self.setLayout(layout)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Attributes
        #    self.data : Active data

        # Get symbols
        with open(SYMBOLS_FILE) as file:
            self.symbols = json.load(file)

        # Set up the window
        self.setupWindow()

        # Graph stuff
        self.layout_graph = QVBoxLayout()

        # Create graph widget
        self.graphWidget = pg.PlotWidget()
        # Set axis type
        date_axis = pg.DateAxisItem(orientation="bottom")
        self.graphWidget.setAxisItems({"bottom": date_axis})
        self.setupGraph()

        self.proxy = pg.SignalProxy(self.graphWidget.scene().sigMouseMoved, rateLimit=60, slot=self.mouseMoved)

        self.layout_graph.addWidget(self.graphWidget)

        # For cursor position display
        self.cursorWidget = QLabel(f"({0}, {0})")

        self.layout_graph.addWidget(self.cursorWidget)

        # Container for graph
        self.container_graph = QWidget()
        self.container_graph.setLayout(self.layout_graph)

        # Side bar stuff
        self.layout_side = QVBoxLayout()

        # Symbol selection (list widget)
        self.select_layout = QVBoxLayout()

        self.select_label = QLabel("Select stock to view")
        self.select_label.setFont(boldFont)
        self.select_layout.addWidget(self.select_label)

        self.list_symbol = QListWidget()
        item = QListWidgetItem("None")
        self.list_symbol.addItem(item)
        for key, index in self.symbols.items():
            self.list_symbol.addItem(f"{key} : {index}")
        self.list_symbol.setCurrentItem(item)
        self.select_layout.addWidget(self.list_symbol)

        self.layout_side.addLayout(self.select_layout)

        # Add/remove push button
        self.add_layout = QHBoxLayout()

        self.add_button = QPushButton("Add")
        self.remove_button = QPushButton("Remove")

        self.add_button.clicked.connect(self.add_button_clicked)
        self.remove_button.clicked.connect(self.remove_button_clicked)

        self.add_layout.addWidget(self.add_button)
        self.add_layout.addWidget(self.remove_button)

        self.layout_side.addLayout(self.add_layout)

        # Pop up add window
        self.add_container = QWidget()
        self.add_layout = QVBoxLayout()

        self.add_label = QLabel("Enter name and symbol of stock.")
        self.add_layout.addWidget(self.add_label)
        self.add_layout_sub = QFormLayout()
        self.add_textbox_name = QLineEdit()
        self.add_layout_sub.addRow("Name: ", self.add_textbox_name)
        self.add_textbox_index = QLineEdit()
        self.add_layout_sub.addRow("Symbol: ", self.add_textbox_index)

        self.add_layout.addLayout(self.add_layout_sub)

        self.add_confirm = QPushButton("Confirm add")
        self.add_confirm.clicked.connect(self.add_confirm_clicked)
        self.add_layout.addWidget(self.add_confirm)

        self.add_cancel = QPushButton("Cancel")
        self.add_cancel.clicked.connect(self.add_container.hide)
        self.add_layout.addWidget(self.add_cancel)

        self.add_container.setLayout(self.add_layout)

        # Pop up remove window
        self.remove_container = QWidget()
        self.remove_layout = QVBoxLayout()

        self.remove_label = QLabel()
        self.remove_layout.addWidget(self.remove_label)

        self.remove_confirm = QPushButton("Confirm remove")
        self.remove_confirm.clicked.connect(self.remove_confirm_clicked)
        self.remove_layout.addWidget(self.remove_confirm)

        self.remove_cancel = QPushButton("Cancel")
        self.remove_cancel.clicked.connect(self.remove_container.hide)
        self.remove_layout.addWidget(self.remove_cancel)

        self.remove_confirm.hide()
        self.remove_container.setLayout(self.remove_layout)

        # Natural log checkbox
        self.check_ln = QCheckBox("Use natural log of data")
        self.check_ln.setChecked(True)

        self.layout_side.addWidget(self.check_ln)

        # Data display checkboxes
        self.options_layout = QVBoxLayout()

        self.options_label = QLabel("Select data to display")
        self.options_label.setFont(boldFont)
        self.options_layout.addWidget(self.options_label)

        self.options_layout_sub = QGridLayout()
        self.check_options = QWidget()
        for i, col in enumerate(COLS):
            checkbox = QCheckBox(col)
            checkbox.setParent(self.check_options)
            if col == "Close":
                checkbox.setChecked(True)
            self.options_layout_sub.addWidget(checkbox, i//2, i%2)
        self.checklist = self.check_options.findChildren(QCheckBox)
        self.options_layout.addLayout(self.options_layout_sub)

        self.layout_side.addLayout(self.options_layout)

        # Bounds calculation widget
        # Checkbox to display suboptions for linear fitting
        self.bound_layout1 = QHBoxLayout()
        self.bound_label1 = QLabel("Perform linear fit")
        self.bound_label1.setFont(boldFont)
        self.bound_layout1.addWidget(self.bound_label1)

        self.check_bound = QCheckBox()
        self.check_bound.clicked.connect(self.check_bound_clicked)
        self.bound_layout1.addWidget(self.check_bound)
        self.layout_side.addLayout(self.bound_layout1)

        # Select range of dates for linear fitting
        self.bound_layout2 = QVBoxLayout()
        self.bound_layout2.addWidget(QLabel("Range of dates to use for calculating bounds \n(using Close data)"))

        self.bound_layout2_date = QHBoxLayout()
        current_date = QDate.currentDate()
        self.bound_upperbound = QDateEdit()
        self.bound_upperbound.setDate(current_date)
        self.bound_lowerbound = QDateEdit()
        self.bound_lowerbound.setDate(current_date.addYears(-10))

        self.bound_layout2_date.addWidget(QLabel("From: "))
        self.bound_layout2_date.addWidget(self.bound_lowerbound)
        self.bound_layout2_date.addWidget(QLabel("To: "))
        self.bound_layout2_date.addWidget(self.bound_upperbound)
        self.bound_layout2.addLayout(self.bound_layout2_date)

        # Container to allow hiding and showing widgets
        self.bound_container = QWidget()
        self.bound_container.setLayout(self.bound_layout2)
        self.bound_container.hide()

        self.layout_side.addWidget(self.bound_container)

        # Confirm selection (button)
        self.button_refresh = QPushButton("Refresh")
        self.button_refresh.clicked.connect(self.select_confirm)

        self.layout_side.addWidget(self.button_refresh)

        # Container for side bar
        self.container_side = QWidget()
        self.container_side.setLayout(self.layout_side)

        # Main layout
        self.layout = QHBoxLayout()
        self.layout.addWidget(self.container_graph, 7)
        self.layout.addWidget(self.container_side, 3)

        self.container = QWidget()
        self.container.setLayout(self.layout)

        self.setCentralWidget(self.container)

    def setupWindow(self):
        self.setWindowTitle("StockApp")

        self.setWindowFlag(Qt.WindowType.CustomizeWindowHint)
        self.setWindowFlag(Qt.WindowType.WindowFullscreenButtonHint, False)

    def setupGraph(self):
        # Set background color
        self.graphWidget.setBackground("w")
        # Add Legends
        self.graphWidget.addLegend()
        # Add grid
        self.graphWidget.showGrid(x=True, y=True)

        self.create_crosshair()

    def create_crosshair(self):
        # Add crosshair lines.
        self.crosshair_v = pg.InfiniteLine(angle=90, movable=False)
        self.crosshair_h = pg.InfiniteLine(angle=0, movable=False)
        self.graphWidget.addItem(self.crosshair_v)
        self.graphWidget.addItem(self.crosshair_h)

    # Event handler in plot for tracking cursor position
    def mouseMoved(self, e):
        pos = e[0]
        if self.graphWidget.sceneBoundingRect().contains(pos):
            mousePoint = self.graphWidget.getPlotItem().vb.mapSceneToView(pos)
            self.graphx = mousePoint.x()
            self.graphy = mousePoint.y()
            self.crosshair_v.setPos(self.graphx)
            self.crosshair_h.setPos(self.graphy)

            self.cursorWidget.setText(f"({datetime.fromtimestamp(self.graphx).date()}, {round(self.graphy, 4)})")

    def add_button_clicked(self):
        self.add_container.show()

    def add_confirm_clicked(self):
        try:
            name = self.add_textbox_name.text()
            index = self.add_textbox_index.text()
            assert name != ""
            assert index != ""
            assert " : " not in name
            assert " : " not in index
        except:
            print("Invalid input")
            self.add_container.hide()
            return

        new_index = {name: index}

        if name in list(self.symbols.keys()):
            self.add_label.setText("Name already exists, try something else.")
            return

        self.symbols.update(new_index)

        with open(SYMBOLS_FILE, "w") as file:
            json.dump(self.symbols, file)

        self.list_symbol.addItem(f"{name} : {index}")

        self.add_container.hide()

    def remove_button_clicked(self):
        self.remove_container.show()

        item = self.list_symbol.currentItem().text()
        if item == "None":
            self.remove_label.setText("Cannot remove item")
            return
        self.remove_label.setText(f"Remove {item}?")
        self.remove_confirm.show()

    def remove_confirm_clicked(self):
        item = self.list_symbol.currentItem()
        name = item.text().split(" : ")[0]

        self.symbols.pop(name)

        with open(SYMBOLS_FILE, "w") as file:
            json.dump(self.symbols, file)

        self.list_symbol.takeItem(self.list_symbol.row(item))

        self.remove_container.hide()
        self.remove_confirm.hide()

    def check_bound_clicked(self):
        if self.check_bound.isChecked():
            self.bound_container.show()
        else:
            self.bound_container.hide()

    # Event handler for symbol selection combo box
    def select_confirm(self):
        item = self.list_symbol.currentItem()
        if item is None:
            pass
        s = item.text().split(" : ")[0]

        if s == "None":
            self.graphWidget.clear()
        elif s in self.symbols.keys():
            self.graphWidget.clear()

            # Get stock data
            self.data = Data(self.symbols[s])

            # Natural log data if check_ln is checked
            if self.check_ln.isChecked():
                self.data.ln()

            # Plot for options
            for i, checkbox in enumerate(self.checklist):
                if checkbox.isChecked():
                    x, y = self.data.get_data(COLS[i])
                    pen = pg.mkPen(color=COLOR[i], alpha=0.5, width=2)
                    self.graphWidget.plot(x, y, pen=pen, name=COLS[i])

            # Calculate for bounds
            if self.check_bound.isChecked():
                xpred, ypred, upperbound, lowerbound = self.data.get_confidence("Close", 0.95,
                                                                                self.bound_lowerbound.dateTime(),
                                                                                self.bound_upperbound.dateTime())

                # Plot linear fit
                pen = pg.mkPen(color="#000", width=2)
                self.graphWidget.plot(xpred, ypred, pen=pen, name="Linear Fit")

                # Plot 95% bound
                pen = pg.mkPen(color="#0aa", width=2)
                self.graphWidget.plot(xpred, upperbound, pen=pen, name="Upper and Lower Bounds 95%")
                self.graphWidget.plot(xpred, lowerbound, pen=pen)

                xpred, ypred, upperbound, lowerbound = self.data.get_confidence("Close", 0.75,
                                                                                self.bound_lowerbound.dateTime(),
                                                                                self.bound_upperbound.dateTime())

                # Plot 75% bound
                pen = pg.mkPen(color="#aa0", width=2)
                self.graphWidget.plot(xpred, upperbound, pen=pen, name="Upper and Lower Bounds 75%")
                self.graphWidget.plot(xpred, lowerbound, pen=pen)

            self.create_crosshair()

            # Set range
            range = self.graphWidget.visibleRange()
            right = QDateTime.currentDateTime().toPyDateTime().timestamp()
            left = QDateTime.currentDateTime().addYears(-10).toPyDateTime().timestamp()
            range.setRight(right)
            range.setLeft(left)
            temp = self.data.df.drop(self.data.df[self.data.df["Timestamp"] < left].index)["Close"]
            range.setTop(min(temp))
            range.setBottom(max(temp))
            self.graphWidget.setRange(range)

            # Set axis Labels
            styles = {'color': 'r', 'font-size': '14px'}
            if self.check_ln.isChecked():
                self.graphWidget.setLabel('left', 'Stock (ln)', **styles)
            else:
                self.graphWidget.setLabel('left', 'Stock', **styles)
            self.graphWidget.setLabel('bottom', 'Date', **styles)

        else:
            print("Invalid selection")


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()