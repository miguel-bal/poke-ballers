import pandas as pd
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QListWidget,
    QButtonGroup, QPushButton, QLabel,
)

from common import SEGMENTED_BUTTON_STYLE, strip_accents

POKEMON_STATS_PATH = "data/pokemon_normalized.csv"


class PokemonEntryPage(QWidget):
    def __init__(self, on_back, on_select):
        super().__init__()
        self.on_back = on_back
        self.on_select = on_select
        self.pokemon = pd.read_csv(POKEMON_STATS_PATH)
        self.pokemon["SEARCH_NAME"] = self.pokemon["DisplayName"].apply(
            lambda name: strip_accents(name).lower()
        )
        self.selected_generation = None

        title = QLabel("Find an NBA player match for a Pokemon")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("Type a Pokemon name...")
        self.search_box.textChanged.connect(self.refresh_list)

        gen_row = QHBoxLayout()
        gen_row.setSpacing(0)
        self.gen_group = QButtonGroup(self)
        self.gen_group.setExclusive(True)

        all_gens_btn = QPushButton("All gens")
        all_gens_btn.setCheckable(True)
        all_gens_btn.setChecked(True)
        all_gens_btn.setStyleSheet(SEGMENTED_BUTTON_STYLE)
        all_gens_btn.toggled.connect(lambda checked: checked and self.set_generation(None))
        self.gen_group.addButton(all_gens_btn)
        gen_row.addWidget(all_gens_btn)

        for gen in sorted(self.pokemon["Generation"].unique()):
            btn = QPushButton(f"Gen {gen}")
            btn.setCheckable(True)
            btn.setStyleSheet(SEGMENTED_BUTTON_STYLE)
            btn.toggled.connect(lambda checked, g=gen: checked and self.set_generation(g))
            self.gen_group.addButton(btn)
            gen_row.addWidget(btn)

        self.result_list = QListWidget()
        self.result_list.itemDoubleClicked.connect(self.select_pokemon)

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
        layout.addLayout(gen_row)
        layout.addWidget(self.result_list)
        layout.addLayout(button_row)
        self.setLayout(layout)

        self.refresh_list()

    def set_generation(self, generation):
        self.selected_generation = generation
        self.refresh_list()

    def refresh_list(self):
        text = strip_accents(self.search_box.text().strip()).lower()
        df = self.pokemon
        if self.selected_generation is not None:
            df = df[df["Generation"] == self.selected_generation]
        if text:
            df = df[df["SEARCH_NAME"].str.contains(text)]

        self.result_list.clear()
        self.result_list.addItems(sorted(df["DisplayName"].tolist())[:100])

    def select_current(self):
        item = self.result_list.currentItem()
        if item:
            self.select_pokemon(item)

    def select_pokemon(self, item):
        self.on_select(item.text())
