import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QCheckBox,
)

from radar_chart import RadarChartWidget

STAT_COLS = ["HP_PCT", "ATTACK_PCT", "DEFENSE_PCT", "SPATK_PCT", "SPDEF_PCT", "SPEED_PCT"]
STAT_LABELS = ["HP", "Attack", "Defense", "Sp. Atk", "Sp. Def", "Speed"]


class OutputPage(QWidget):
    def __init__(self, on_back, matches_path, matches_key_col, other_path, other_key_col, source_label):
        super().__init__()
        self.matches = pd.read_csv(matches_path)
        self.other = pd.read_csv(other_path)
        self.matches_key_col = matches_key_col
        self.other_key_col = other_key_col

        self.header_label = QLabel()
        self.header_label.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.match_label = QLabel()

        self.radar_chart = RadarChartWidget(STAT_LABELS)
        self.radar_chart.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.current_series = []

        self.series_checkboxes = [QCheckBox() for _ in range(3)]
        toggle_row = QHBoxLayout()
        for checkbox in self.series_checkboxes:
            checkbox.setChecked(True)
            checkbox.toggled.connect(self.update_chart)
            toggle_row.addWidget(checkbox)

        self.table = QTableWidget(len(STAT_LABELS), 4)
        self.table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.table.setHorizontalHeaderLabels(["Stat", source_label, "Euclidean Match", "Cosine Match"])
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        for row, label in enumerate(STAT_LABELS):
            self.table.setItem(row, 0, QTableWidgetItem(label))

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(on_back)

        chart_col = QVBoxLayout()
        chart_col.addWidget(self.radar_chart)
        chart_col.addLayout(toggle_row)

        content_row = QHBoxLayout()
        content_row.addLayout(chart_col, 1)
        content_row.addWidget(self.table, 1)

        layout = QVBoxLayout()
        layout.addWidget(self.header_label)
        layout.addWidget(self.match_label)
        layout.addLayout(content_row)
        layout.addWidget(back_btn)
        self.setLayout(layout)

    def show_entity(self, name):
        row = self.matches[self.matches[self.matches_key_col] == name].iloc[0]
        euclidean_name = row["EUCLIDEAN_MATCH"]
        cosine_name = row["COSINE_MATCH"]
        euclidean_row = self.other[self.other[self.other_key_col] == euclidean_name].iloc[0]
        cosine_row = self.other[self.other[self.other_key_col] == cosine_name].iloc[0]

        self.header_label.setText(name)
        self.match_label.setText(
            f"Euclidean match: {euclidean_name} (distance {row['EUCLIDEAN_DIST']:.1f})   |   "
            f"Cosine match: {cosine_name} (similarity {row['COSINE_SIM']:.4f})"
        )

        for r, col in enumerate(STAT_COLS):
            self.table.setItem(r, 1, QTableWidgetItem(f"{row[col]:.1f}"))
            self.table.setItem(r, 2, QTableWidgetItem(f"{euclidean_row[col]:.1f}"))
            self.table.setItem(r, 3, QTableWidgetItem(f"{cosine_row[col]:.1f}"))

        self.current_series = [
            (name, [row[col] for col in STAT_COLS], "#4a90d9"),
            (euclidean_name, [euclidean_row[col] for col in STAT_COLS], "#d94a4a"),
            (cosine_name, [cosine_row[col] for col in STAT_COLS], "#4ad97a"),
        ]
        for checkbox, (series_name, _, _) in zip(self.series_checkboxes, self.current_series):
            checkbox.setText(series_name)
            checkbox.setChecked(True)

        self.update_chart()

    def update_chart(self):
        visible_series = [
            series for checkbox, series in zip(self.series_checkboxes, self.current_series)
            if checkbox.isChecked()
        ]
        self.radar_chart.plot(visible_series)
