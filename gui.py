# gui.py
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
    QComboBox,
    QLineEdit,
    QHBoxLayout,
    QTextEdit,
    QTableWidgetSelectionRange,
)
from PyQt5.QtCore import Qt, pyqtSignal

class SiteTableGUI(QWidget):
    # Signal to emit the selected sites data
    sites_processed = pyqtSignal(list)
    # Signal to emit user input for a site
    user_input_received = pyqtSignal(str, str, str)
    # Signal to emit turn in sites request
    turn_in_sites_signal = pyqtSignal()

    def __init__(self, table_data, processed_sites_dict):
        super().__init__()
        self.setWindowTitle("Parsed Sites")
        self.resize(800, 600)
        self.table_data = table_data
        self.selected_sites = []
        self.processed_sites = []  # To store processed sites
        self.processed_sites_dict = processed_sites_dict  # Add this line

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_table()
        self.create_buttons()
        self.create_progress_display()

    def create_table(self):
        self.table = QTableWidget()
        self.table.setColumnCount(6)  # Updated column count
        headers = ["Select", "Owner", "Site ID", "Result", "Fail Reason", "Action"]
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

            # Populate Owner column (assuming Owner is at index 1)
            owner_item = QTableWidgetItem(row_data[1] if len(row_data) > 1 else "")
            owner_item.setFlags(owner_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row_idx, 1, owner_item)

            # Populate Site ID column (assuming Site ID is at index 2)
            site_id = row_data[2] if len(row_data) > 2 else ""
            site_id_item = QTableWidgetItem(site_id)
            site_id_item.setFlags(site_id_item.flags() ^ Qt.ItemIsEditable)
            self.table.setItem(row_idx, 2, site_id_item)

            # Check if site_id is in processed_sites_dict
            if site_id in self.processed_sites_dict:
                # Site has been processed before
                result_data = self.processed_sites_dict[site_id]
                result = result_data[1]  # result.lower()
                fail_reason = result_data[3]
                # Add Result dropdown (disabled)
                result_combo = QComboBox()
                result_combo.addItems(["", "Pass", "Fail", "Skip"])
                result_combo.setCurrentText(result.capitalize())
                result_combo.setEnabled(False)
                self.table.setCellWidget(row_idx, 3, result_combo)
                # Add Fail Reason input (disabled)
                fail_reason_input = QLineEdit()
                fail_reason_input.setText(fail_reason)
                fail_reason_input.setEnabled(False)
                self.table.setCellWidget(row_idx, 4, fail_reason_input)
                # Add placeholder to Action column
                action_item = QTableWidgetItem("Processed")
                action_item.setFlags(action_item.flags() ^ Qt.ItemIsEditable)
                self.table.setItem(row_idx, 5, action_item)
                # Add to processed_sites
                self.processed_sites.append((site_id, result.lower(), "", fail_reason))
                # Disable the checkbox
                checkbox_widget = self.table.cellWidget(row_idx, 0)
                checkbox = checkbox_widget.findChild(QCheckBox)
                checkbox.setEnabled(False)
            else:
                # Site has not been processed
                # Add Result dropdown (initially disabled)
                result_combo = QComboBox()
                result_combo.addItems(["", "Pass", "Fail", "Skip"])
                result_combo.setEnabled(False)
                self.table.setCellWidget(row_idx, 3, result_combo)
                # Add Fail Reason input (initially disabled)
                fail_reason_input = QLineEdit()
                fail_reason_input.setEnabled(False)
                self.table.setCellWidget(row_idx, 4, fail_reason_input)
                # Add to Action column
                action_item = QTableWidgetItem("")
                self.table.setItem(row_idx, 5, action_item)
                # Connect the result combo box to enable/disable the fail reason input
                def on_result_changed(text, fr_input=fail_reason_input):
                    fr_input.setEnabled(text.lower() == "fail")
                result_combo.currentTextChanged.connect(on_result_changed)

        self.layout.addWidget(self.table)

    def create_buttons(self):
        self.button_layout = QHBoxLayout()

        self.process_button = QPushButton("Process Selected Sites")
        self.process_button.clicked.connect(self.process_selected_sites)
        self.button_layout.addWidget(self.process_button)

        # Add the new Turn In button
        self.turn_in_button = QPushButton("Turn in Processed Sites")
        self.turn_in_button.clicked.connect(self.turn_in_processed_sites)
        self.turn_in_button.setEnabled(bool(self.processed_sites))  # Enable if there are processed sites
        self.button_layout.addWidget(self.turn_in_button)

        self.layout.addLayout(self.button_layout)

    def create_progress_display(self):
        self.progress_display = QTextEdit()
        self.progress_display.setReadOnly(True)
        self.layout.addWidget(self.progress_display)

    def update_progress(self, message):
        self.progress_display.append(message)

    def process_selected_sites(self):
        # Collect selected site IDs
        self.selected_sites = []
        for row in range(self.table.rowCount()):
            checkbox_widget = self.table.cellWidget(row, 0)
            checkbox = checkbox_widget.findChild(QCheckBox)
            if checkbox.isChecked() and checkbox.isEnabled():
                site_id = self.table.item(row, 2).text()
                self.selected_sites.append({'site_id': site_id})
        if not self.selected_sites:
            QMessageBox.warning(self, "No Selection", "No sites selected.")
            return
        # Emit the signal with the data
        self.sites_processed.emit(self.selected_sites)
        # Disable the process button to prevent re-processing
        self.process_button.setEnabled(False)

    def on_site_processed(self, site_id):
        # Find the row corresponding to the site_id
        for row in range(self.table.rowCount()):
            if self.table.item(row, 2).text() == site_id:
                # Enable the Result dropdown and Fail Reason input
                result_combo = self.table.cellWidget(row, 3)
                result_combo.setEnabled(True)
                fail_reason_input = self.table.cellWidget(row, 4)
                # Add a Confirm button
                confirm_button = QPushButton("Confirm")
                self.table.setCellWidget(row, 5, confirm_button)
                # Connect the Confirm button
                confirm_button.clicked.connect(lambda _, r=row: self.confirm_result(r))
                # Optionally, highlight the row
                self.table.selectRow(row)
                break

    def confirm_result(self, row):
        site_id = self.table.item(row, 2).text()
        result_combo = self.table.cellWidget(row, 3)
        result = result_combo.currentText()
        fail_reason_input = self.table.cellWidget(row, 4)
        fail_reason = fail_reason_input.text()
        if not result:
            QMessageBox.warning(self, "Missing Result", f"Please select a result for site {site_id}")
            return
        if result.lower() == "fail" and not fail_reason:
            QMessageBox.warning(self, "Missing Fail Reason", f"Please provide a fail reason for site {site_id}")
            return
        # Disable the inputs
        result_combo.setEnabled(False)
        fail_reason_input.setEnabled(False)
        confirm_button = self.table.cellWidget(row, 5)
        confirm_button.setEnabled(False)
        # Emit the user input signal
        self.user_input_received.emit(site_id, result, fail_reason)
        # Add to processed_sites
        self.processed_sites.append((site_id, result.lower(), "", fail_reason))
        # Enable the Turn In button as there is at least one processed site
        self.turn_in_button.setEnabled(True)
        # Optionally, unselect the row
        self.table.setRangeSelected(QTableWidgetSelectionRange(row, 0, row, self.table.columnCount()-1), False)
        # Update Action column
        action_item = QTableWidgetItem("Processed")
        action_item.setFlags(action_item.flags() ^ Qt.ItemIsEditable)
        self.table.setItem(row, 5, action_item)
        # Disable the checkbox
        checkbox_widget = self.table.cellWidget(row, 0)
        checkbox = checkbox_widget.findChild(QCheckBox)
        checkbox.setEnabled(False)

    def turn_in_processed_sites(self):
        if not self.processed_sites:
            QMessageBox.information(self, "No Processed Sites", "There are no processed sites to turn in.")
            return
        # Emit the turn in signal without data
        self.turn_in_sites_signal.emit()
        # Optionally, disable the turn in button to prevent re-turning
        self.turn_in_button.setEnabled(False)
