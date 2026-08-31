import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QStackedWidget, QSizePolicy,
)

from nba_entry import NbaEntryPage
from pokemon_entry import PokemonEntryPage
from output_page import OutputPage


class HomePage(QWidget):
    def __init__(self, on_nba_to_pokemon, on_pokemon_to_nba):
        super().__init__()

        title = QLabel("Poké-Ballers")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 40px; font-weight: bold; padding: 20px 0 0 0;")

        subtitle = QLabel("Find your NBA player's Pokémon stat counterpart")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("font-size: 13px; color: #999; padding: 0 0 20px 0;")

        mode_row = QHBoxLayout()
        nba_to_pokemon_btn = QPushButton("NBA Player → Pokemon")
        pokemon_to_nba_btn = QPushButton("Pokemon → NBA Player")
        nba_to_pokemon_btn.clicked.connect(on_nba_to_pokemon)
        pokemon_to_nba_btn.clicked.connect(on_pokemon_to_nba)
        mode_row.addWidget(nba_to_pokemon_btn)
        mode_row.addWidget(pokemon_to_nba_btn)

        info_row = QHBoxLayout()
        info_btn = QPushButton("Instructions / About")
        info_btn.clicked.connect(self.placeholder)
        info_row.addWidget(info_btn)

        exit_row = QHBoxLayout()
        exit_btn = QPushButton("Exit")
        exit_btn.clicked.connect(QApplication.quit)
        exit_row.addWidget(exit_btn)

        for btn in [nba_to_pokemon_btn, pokemon_to_nba_btn, info_btn, exit_btn]:
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(mode_row, 1)
        layout.addLayout(info_row, 1)
        layout.addLayout(exit_row, 1)
        self.setLayout(layout)

    def placeholder(self):
        QMessageBox.information(self, "Not built yet", "This screen isn't implemented yet.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Poké-Ballers")
        self.resize(500, 400)

        self.stack = QStackedWidget()
        self.home_page = HomePage(self.show_nba_entry, self.show_pokemon_entry)
        self.nba_entry_page = NbaEntryPage(self.show_home, self.show_nba_to_pokemon_output)
        self.pokemon_entry_page = PokemonEntryPage(self.show_home, self.show_pokemon_to_nba_output)
        self.nba_to_pokemon_output = OutputPage(
            self.show_nba_entry,
            matches_path="data/matches.csv", matches_key_col="PLAYER_NAME",
            other_path="data/pokemon_normalized.csv", other_key_col="DisplayName",
            source_label="Player",
        )
        self.pokemon_to_nba_output = OutputPage(
            self.show_pokemon_entry,
            matches_path="data/pokemon_matches.csv", matches_key_col="DisplayName",
            other_path="data/nba_career_stats.csv", other_key_col="PLAYER_NAME",
            source_label="Pokemon",
        )
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.nba_entry_page)
        self.stack.addWidget(self.pokemon_entry_page)
        self.stack.addWidget(self.nba_to_pokemon_output)
        self.stack.addWidget(self.pokemon_to_nba_output)

        self.setCentralWidget(self.stack)

    def show_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def show_nba_entry(self):
        self.stack.setCurrentWidget(self.nba_entry_page)

    def show_pokemon_entry(self):
        self.stack.setCurrentWidget(self.pokemon_entry_page)

    def show_nba_to_pokemon_output(self, player_name):
        self.nba_to_pokemon_output.show_entity(player_name)
        self.stack.setCurrentWidget(self.nba_to_pokemon_output)

    def show_pokemon_to_nba_output(self, pokemon_name):
        self.pokemon_to_nba_output.show_entity(pokemon_name)
        self.stack.setCurrentWidget(self.pokemon_to_nba_output)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
