import sys
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QCheckBox,
    QPushButton,
    QMessageBox,
)
from PyQt5.QtCore import Qt

class SiteTableGUI(QWidget):
    def __init__(self, table_data):
        super().__init__()
        self.setWindowTitle("Parsed Sites")
        self.resize(600, 400)
        self.table_data = table_data
        self.selected_sites = []

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_table()
        self.create_buttons()

    def create_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(3)  # Only 3 columns: Select, Owner, Site ID
        headers = ["Select", "Owner", "Site ID"]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        self.table.setRowCount(len(self.table_data))

        for row_idx, row_data in enumerate(self.table_data):
            # Add checkbox
            checkbox = QCheckBox()
            checkbox_widget = QWidget()
            checkbox_layout = QVBoxLayout()
            checkbox_layout.addWidget(checkbox)
            checkbox_layout.setAlignment(Qt.AlignCenter)
            checkbox_layout.setContentsMargins(0, 0, 0, 0)
            checkbox_widget.setLayout(checkbox_layout)
            self.table.setCellWidget(row_idx, 0, checkbox_widget)

            # Populate other columns (assuming Owner is at index 1 and Site ID is at index 2)
            owner_item = QTableWidgetItem(row_data[1] if len(row_data) > 1 else "")
            owner_item.setFlags(owner_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row_idx, 1, owner_item)

            site_id_item = QTableWidgetItem(row_data[2] if len(row_data) > 2 else "")
            site_id_item.setFlags(site_id_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row_idx, 2, site_id_item)

        self.layout.addWidget(self.table)

    def create_buttons(self):
        self.button_layout = QVBoxLayout()

        self.select_button = QPushButton("Process Selected Sites")
        self.select_button.clicked.connect(self.process_selected_sites)
        self.layout.addWidget(self.select_button)

    def process_selected_sites(self):
        self.selected_sites = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox.isChecked():
                site_id = self.table.item(row, 2).text()  # Get the Site ID from the 2nd column
                self.selected_sites.append(site_id)

        if not self.selected_sites:
            QMessageBox.warning(self, "No Selection", "No sites selected.")
            return

        QMessageBox.information(
            self,
            "Selected Sites",
            f"The following sites have been selected:\n{', '.join(self.selected_sites)}",
        )
        self.close()

def main():
    app = QApplication(sys.argv)
    parsed_table_path = "parsed_table.txt"
    table_data = read_parsed_table(parsed_table_path)

    if not table_data:
        QMessageBox.critical(None, "Error", "No data found in parsed_table.txt.")
        sys.exit()

    gui = SiteTableGUI(table_data)
    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
