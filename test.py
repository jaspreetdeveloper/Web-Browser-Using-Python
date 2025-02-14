from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
import sys
import os

class Browser(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Unity Browser")
        self.setWindowIcon(QIcon("icons/browser.png"))
        self.showMaximized()

        # Dark mode flag
        self.dark_mode = False

        # Central widget and layout setup
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        # WebEngineView setup
        self.browser = QWebEngineView()
        self.home_page = self.load_home_page()
        self.browser.setUrl(QUrl(self.home_page))
        self.layout.addWidget(self.browser)

        # Navigation bar setup
        self.create_navigation_bar()

        # Progress bar
        self.progress = QProgressBar()
        self.progress.setMaximumHeight(10)
        self.progress.setVisible(False)
        self.layout.addWidget(self.progress)

        # Browser signals
        self.browser.loadProgress.connect(self.update_progress)
        self.browser.loadFinished.connect(self.hide_progress)
        self.browser.urlChanged.connect(self.update_url)

        # Load bookmarks, history, and favorites
        self.load_bookmarks()
        self.load_history()

    def create_navigation_bar(self):
        navbar = QToolBar()
        self.addToolBar(navbar)

        # Helper function to create navigation buttons
        def add_nav_button(icon, tooltip, callback):
            button = QAction(QIcon(icon), tooltip, self)
            button.triggered.connect(callback)
            navbar.addAction(button)

        # Add navigation buttons
        add_nav_button("icons/back.png", "Back", self.browser.back)
        add_nav_button("icons/forward.png", "Forward", self.browser.forward)
        add_nav_button("icons/reload.png", "Reload", self.browser.reload)
        add_nav_button("icons/home.png", "Home", self.navigate_home)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Dark mode toggle
        dark_mode_btn = QAction(QIcon("icons/dark.png"), "Toggle Dark Mode", self)
        dark_mode_btn.triggered.connect(self.toggle_theme)
        navbar.addAction(dark_mode_btn)

        # Set home page button
        home_set_btn = QAction(QIcon("icons/sethomepage.png"), "Set Home Page", self)
        home_set_btn.triggered.connect(self.set_home_page)
        navbar.addAction(home_set_btn)

        # Add bookmark button
        bookmark_btn = QAction(QIcon("icons/bookmark.png"), "Add Bookmark", self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        navbar.addAction(bookmark_btn)

        # Menus for bookmarks and history
        self.bookmark_menu = QMenu("Bookmarks", self)
        self.menuBar().addMenu(self.bookmark_menu)

        self.history_menu = QMenu("History", self)
        self.menuBar().addMenu(self.history_menu)

    def navigate_home(self):
        self.browser.setUrl(QUrl(self.home_page))

    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = f"https://www.google.com/search?q={url}"
        self.browser.setUrl(QUrl(url))

    def update_url(self, q):
        self.url_bar.setText(q.toString())
        self.save_history(q.toString())

    def toggle_theme(self):
        if not self.dark_mode:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2E2E2E;
                    color: white;
                }
                QToolBar {
                    background-color: #444444;
                }
                QLineEdit {
                    background-color: #555555;
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QMainWindow {
                    background-color: white;
                    color: black;
                }
                QToolBar {
                    background-color: #f0f0f0;
                }
                QLineEdit {
                    background-color: white;
                    color: black;
                }
            """)
        self.dark_mode = not self.dark_mode

    def add_bookmark(self):
        url = self.browser.url().toString()
        name, ok = QInputDialog.getText(self, 'Bookmark Name', 'Enter name for this bookmark:')
        if ok:
            bookmark_action = QAction(name, self)
            bookmark_action.triggered.connect(lambda: self.browser.setUrl(QUrl(url)))
            self.bookmark_menu.addAction(bookmark_action)
            with open("bookmarks.txt", "a") as file:
                file.write(f"{name},{url}\n")

    def load_bookmarks(self):
        if os.path.exists("bookmarks.txt"):
            with open("bookmarks.txt", "r") as file:
                for line in file.readlines():
                    name, url = line.strip().split(",")
                    bookmark_action = QAction(name, self)
                    bookmark_action.triggered.connect(lambda url=url: self.browser.setUrl(QUrl(url)))
                    self.bookmark_menu.addAction(bookmark_action)

    def save_history(self, url):
        with open("history.txt", "a") as file:
            file.write(url + "\n")
        history_action = QAction(url, self)
        history_action.triggered.connect(lambda: self.browser.setUrl(QUrl(url)))
        self.history_menu.addAction(history_action)

    def load_history(self):
        if os.path.exists("history.txt"):
            with open("history.txt", "r") as file:
                for url in file.readlines():
                    url = url.strip()
                    history_action = QAction(url, self)
                    history_action.triggered.connect(lambda url=url: self.browser.setUrl(QUrl(url)))
                    self.history_menu.addAction(history_action)

    def update_progress(self, progress):
        self.progress.setValue(progress)
        self.progress.setVisible(True)

    def hide_progress(self):
        self.progress.setVisible(False)

    def set_home_page(self):
        home_url, ok = QInputDialog.getText(self, 'Set Home Page', 'Enter the URL for the home page:')
        if ok:
            with open("home_page.txt", "w") as file:
                file.write(home_url)
            self.home_page = home_url

    def load_home_page(self):
        if os.path.exists("home_page.txt"):
            with open("home_page.txt", "r") as file:
                return file.read().strip()
        return "https://unitybrowser.my.canva.site/"  # Default home page

# Splash screen
def show_splash_screen():
    splash_pix = QPixmap("icons/splash.png")
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    QTimer.singleShot(2000, splash.close)

# Main application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Unity Browser")
    show_splash_screen()
    window = Browser()
    app.exec_()
