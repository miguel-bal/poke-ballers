import sys

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QStackedWidget,
)

from nba_entry import NbaEntryPage
from output_page import OutputPage


class HomePage(QWidget):
    def __init__(self, on_nba_to_pokemon):
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
        pokemon_to_nba_btn.clicked.connect(self.placeholder)
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

        layout = QVBoxLayout()
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addLayout(mode_row)
        layout.addLayout(info_row)
        layout.addLayout(exit_row)
        self.setLayout(layout)

    def placeholder(self):
        QMessageBox.information(self, "Not built yet", "This screen isn't implemented yet.")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Poké-Ballers")
        self.resize(500, 400)

        self.stack = QStackedWidget()
        self.home_page = HomePage(self.show_nba_entry)
        self.nba_entry_page = NbaEntryPage(self.show_home, self.show_output)
        self.output_page = OutputPage(self.show_nba_entry)
        self.stack.addWidget(self.home_page)
        self.stack.addWidget(self.nba_entry_page)
        self.stack.addWidget(self.output_page)

        self.setCentralWidget(self.stack)

    def show_home(self):
        self.stack.setCurrentWidget(self.home_page)

    def show_nba_entry(self):
        self.stack.setCurrentWidget(self.nba_entry_page)

    def show_output(self, player_name):
        self.output_page.show_player(player_name)
        self.stack.setCurrentWidget(self.output_page)


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
