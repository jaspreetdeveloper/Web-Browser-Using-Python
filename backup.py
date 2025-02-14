from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtGui import *
import sys
import os

class Browser(QMainWindow):
    def __init__(self):
        super(Browser, self).__init__()
        self.browser = QWebEngineView()
        self.home_page = self.load_home_page()  # Load your custom home page
        self.browser.setUrl(QUrl(self.home_page))  # Set custom or default home page
        self.setCentralWidget(self.browser)
        self.showMaximized()

        # Dark mode flag
        self.dark_mode = False

        # Window title and icon
        self.setWindowTitle("Unity Browser")
        self.setWindowIcon(QIcon("icons/browser.png"))

        # Navigation bar
        navbar = QToolBar()
        self.addToolBar(navbar)

        # Back button with custom image
        back_btn = QAction(QIcon("icons/back.png"), "Back", self)
        back_btn.triggered.connect(self.browser.back)
        navbar.addAction(back_btn)

        # Forward button with custom image
        forward_btn = QAction(QIcon("icons/forward.png"), "Forward", self)
        forward_btn.triggered.connect(self.browser.forward)
        navbar.addAction(forward_btn)

        # Reload button with custom image
        reload_btn = QAction(QIcon("icons/reload.png"), "Reload", self)
        reload_btn.triggered.connect(self.browser.reload)
        navbar.addAction(reload_btn)

        # Home button with custom image
        home_btn = QAction(QIcon("icons/home.png"), "Home", self)
        home_btn.triggered.connect(self.navigate_home)
        navbar.addAction(home_btn)

        # URL bar
        self.url_bar = QLineEdit()
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        navbar.addWidget(self.url_bar)

        # Bookmark button with custom image
        bookmark_btn = QAction(QIcon("icons/bookmark.png"), "Bookmark", self)
        bookmark_btn.triggered.connect(self.add_bookmark)
        navbar.addAction(bookmark_btn)

        # Dark mode toggle button with custom image
        dark_mode_btn = QAction(QIcon("icons/dark.png"), "Toggle Dark Mode", self)
        dark_mode_btn.triggered.connect(self.toggle_dark_mode)
        navbar.addAction(dark_mode_btn)

        # Set Home Page button with custom image
        home_set_btn = QAction(QIcon("icons/sethomepage.png"), "Set Home Page", self)
        home_set_btn.triggered.connect(self.set_home_page)
        navbar.addAction(home_set_btn)

        # Bookmarks menu
        bookmark_menu = QMenu("Bookmarks", self)
        self.menuBar().addMenu(bookmark_menu)
        self.bookmarks = bookmark_menu

        # History menu
        history_menu = QMenu("History", self)
        self.menuBar().addMenu(history_menu)
        self.history = history_menu

        # Progress bar for loading pages
        self.progress = QProgressBar()
        self.progress.setMaximumHeight(10)
        self.progress.setVisible(False)
        navbar.addWidget(self.progress)

        # Connect the progress bar with page loading status
        self.browser.loadProgress.connect(self.update_progress)
        self.browser.loadFinished.connect(self.hide_progress)

        # Update URL bar when URL changes
        self.browser.urlChanged.connect(self.update_url)

        # Enable download functionality
        self.browser.page().profile().downloadRequested.connect(self.download_file)

        # Load bookmarks and history from file
        self.load_bookmarks()
        self.load_history()

    # Home page navigation
    def navigate_home(self):
        self.browser.setUrl(QUrl(self.home_page))

    # Navigate to URL
    def navigate_to_url(self):
        url = self.url_bar.text()
        if not url.startswith("http"):
            url = f"https://www.google.com/search?q={url}"
        self.browser.setUrl(QUrl(url))

    # Update URL bar
    def update_url(self, q):
        self.url_bar.setText(q.toString())
        self.save_history(q.toString())

    # Add bookmark
    def add_bookmark(self):
        url = self.browser.url().toString()
        name, ok = QInputDialog.getText(self, 'Bookmark Name', 'Enter name for this bookmark:')
        if ok:
            bookmark_action = QAction(name, self)
            bookmark_action.triggered.connect(lambda: self.browser.setUrl(QUrl(url)))
            self.bookmarks.addAction(bookmark_action)
            with open("bookmarks.txt", "a") as file:
                file.write(f"{name},{url}\n")

    # Load bookmarks from file
    def load_bookmarks(self):
        if os.path.exists("bookmarks.txt"):
            with open("bookmarks.txt", "r") as file:
                for line in file.readlines():
                    name, url = line.strip().split(",")
                    bookmark_action = QAction(name, self)
                    bookmark_action.triggered.connect(lambda url=url: self.browser.setUrl(QUrl(url)))
                    self.bookmarks.addAction(bookmark_action)

    # Toggle dark mode
    def toggle_dark_mode(self):
        if not self.dark_mode:
            self.setStyleSheet("background-color: #2E2E2E; color: #FFFFFF;")
        else:
            self.setStyleSheet("")
        self.dark_mode = not self.dark_mode

    # Download file
    def download_file(self, download_item):
        save_path, _ = QFileDialog.getSaveFileName(self, "Save File", download_item.url().fileName())
        if save_path:
            download_item.setPath(save_path)
            download_item.accept()

    # Set custom home page
    def set_home_page(self):
        home_url, ok = QInputDialog.getText(self, 'Set Home Page', 'Enter the URL for the home page:')
        if ok:
            with open("home_page.txt", "w") as file:
                file.write(home_url)
            self.home_page = home_url

    # Load custom or default home page
    def load_home_page(self):
        return "https://unitybrowser.my.canva.site/"  # Your website URL

    # Save history
    def save_history(self, url):
        with open("history.txt", "a") as file:
            file.write(url + "\n")
        history_action = QAction(url, self)
        history_action.triggered.connect(lambda: self.browser.setUrl(QUrl(url)))
        self.history.addAction(history_action)

    # Load history
    def load_history(self):
        if os.path.exists("history.txt"):
            with open("history.txt", "r") as file:
                for url in file.readlines():
                    url = url.strip()
                    history_action = QAction(url, self)
                    history_action.triggered.connect(lambda url=url: self.browser.setUrl(QUrl(url)))
                    self.history.addAction(history_action)

    # Update progress bar when loading a page
    def update_progress(self, progress):
        self.progress.setValue(progress)
        self.progress.setVisible(True)

    # Hide progress bar once page has finished loading
    def hide_progress(self):
        self.progress.setVisible(False)

# Splash screen setup
def show_splash_screen():
    splash_pix = QPixmap("icons/splash.png")
    splash = QSplashScreen(splash_pix, Qt.WindowStaysOnTopHint)
    splash.setMask(splash_pix.mask())
    splash.show()
    QTimer.singleShot(2000, splash.close)  # Display splash for 2 seconds

# Main application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    QApplication.setApplicationName("Unity Browser")

    # Show splash screen
    show_splash_screen()

    # Create and display the browser window
    window = Browser()
    app.exec_()
