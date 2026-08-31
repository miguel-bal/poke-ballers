import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QButtonGroup, QPushButton, QLabel,
)

from common import SEGMENTED_BUTTON_STYLE, strip_accents

CAREER_STATS_PATH = "data/nba_career_stats.csv"


class NbaEntryPage(QWidget):
    def __init__(self, on_back, on_select):
        super().__init__()
        self.on_back = on_back
        self.on_select = on_select
        self.players = pd.read_csv(CAREER_STATS_PATH)
        self.players["SEARCH_NAME"] = self.players["PLAYER_NAME"].apply(
            lambda name: strip_accents(name).lower()
        )
        self.selected_decade = None

        title = QLabel("Find a Pokemon match for an NBA player")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type a player name...")
        self.search_box.textChanged.connect(self.refresh_list)

        era_row = QHBoxLayout()
        era_row.setSpacing(0)
        self.era_group = QButtonGroup(self)
        self.era_group.setExclusive(True)

        all_eras_btn = QPushButton("All eras")
        all_eras_btn.setCheckable(True)
        all_eras_btn.setChecked(True)
        all_eras_btn.setStyleSheet(SEGMENTED_BUTTON_STYLE)
        all_eras_btn.toggled.connect(lambda checked: checked and self.set_decade(None))
        self.era_group.addButton(all_eras_btn)
        era_row.addWidget(all_eras_btn)

        for decade, label in sorted(self.players[["PRIMARY_DECADE", "ERA_LABEL"]].drop_duplicates().values.tolist()):
            btn = QPushButton(f"{decade}s - {label}")
            btn.setCheckable(True)
            btn.setStyleSheet(SEGMENTED_BUTTON_STYLE)
            btn.toggled.connect(lambda checked, d=decade: checked and self.set_decade(d))
            self.era_group.addButton(btn)
            era_row.addWidget(btn)

        self.result_list = QListWidget()
        self.result_list.itemDoubleClicked.connect(self.select_player)

        select_btn = QPushButton("Select")
        select_btn.clicked.connect(self.select_current)

        back_btn = QPushButton("Back")
        back_btn.clicked.connect(self.on_back)

        button_row = QHBoxLayout()
        button_row.addWidget(select_btn)
        button_row.addWidget(back_btn)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(self.search_box)
        layout.addLayout(era_row)
        layout.addWidget(self.result_list)
        layout.addLayout(button_row)
        self.setLayout(layout)

        self.refresh_list()

    def set_decade(self, decade):
        self.selected_decade = decade
        self.refresh_list()

    def refresh_list(self):
        text = strip_accents(self.search_box.text().strip()).lower()
        df = self.players
        if self.selected_decade is not None:
            df = df[df["PRIMARY_DECADE"] == self.selected_decade]
        if text:
            df = df[df["SEARCH_NAME"].str.contains(text)]

        self.result_list.clear()
        self.result_list.addItems(sorted(df["PLAYER_NAME"].tolist())[:100])

    def select_current(self):
        item = self.result_list.currentItem()
        if item:
            self.select_player(item)

    def select_player(self, item):
        self.on_select(item.text())
