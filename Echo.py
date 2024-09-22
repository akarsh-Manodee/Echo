import sys
import os
import hashlib
import base64
from cryptography.fernet import Fernet
from PyQt5.QtWidgets import (QApplication, QMainWindow, QTextEdit, QAction, QMessageBox, 
                             QTreeView, QFileSystemModel, QVBoxLayout, QWidget, 
                             QSplitter, QInputDialog, QLineEdit, QPushButton)
from PyQt5.QtCore import QPropertyAnimation, Qt, QDateTime, QEasingCurve
from PyQt5.QtGui import QKeySequence

class JournalApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.journal_dir = os.path.expanduser('~/Echo')
        self.pin_file = os.path.expanduser('~/.echo_pin')  # Hidden file to store the hashed pin
        self.encryption_key = None

        # Pin check
        self.check_or_create_pin()

        # Decrypt journal folder if the correct pin is provided
        self.decrypt_journal_files()

        # Create a text editor for journaling
        self.text_edit = QTextEdit(self)
        self.setCentralWidget(self.text_edit)

        # Setup UI and tree navigation
        self.initUI()

    def check_or_create_pin(self):
        """Check if a pin exists, if not, ask the user to create one"""
        if not os.path.exists(self.pin_file):
            self.create_pin()
        else:
            self.prompt_for_pin()

    def create_pin(self):
        """Prompt the user to create a 4-digit pin"""
        while True:
            pin, ok = QInputDialog.getText(self, 'Create Pin', 'Enter a 4-digit pin:', QLineEdit.Password)
            if ok and len(pin) == 4 and pin.isdigit():
                # Hash and store the pin
                hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
                with open(self.pin_file, 'w') as file:
                    file.write(hashed_pin)
                self.encryption_key = self.generate_key(pin)
                self.show_instructions()
                break
            else:
                QMessageBox.warning(self, 'Invalid Pin', 'Please enter a valid 4-digit pin.')

    def show_instructions(self):
        """Show instructions for using the journal app"""
        instructions = (
            "🎉 Congratulations on setting up your Journal! 🎉\n\n"
            "Here’s what you need to know:\n\n"
            "✍️ Once you save your journal entry, it can't be edited. "
            "Consider your words carefully!\n\n"
            "🔑 You can access your journal using the 4-digit pin you just created. "
            "Remember, security first!\n\n"
            "💾 Shortcuts to make your life easier:\n"
            " - Ctrl + S: Save your journal entry\n"
            " - Ctrl + Q: Quit the app (don't forget to save before you go!)\n\n"
            "🔒 Your journals are encrypted for your privacy. "
            "Only you can unlock them with your pin.\n\n"
            "⚠️ Important Security Note: If you haven't saved your current journal entry and navigate to another journal, "
            "your unsaved work will be lost. It's advised to write and save your journal first. Once you open a previous journal, "
            "the whole app will become read-only, and you cannot write in the current journal if you haven't saved the file. "
            "To write again, you will need to reopen the software.\n\n"
            "📖 For first-time users: You don't have any journals today, so please write your first journal entry and hit Ctrl + S to save it. "
            "Then, use Ctrl + Q to quit the app. After that, you'll be able to navigate to your saved diary entries easily.\n\n"
            "Happy journaling! 📝"
        )

        QMessageBox.information(self, 'Welcome to Your Journal', instructions)

    def prompt_for_pin(self):
        """Prompt the user to enter the pin"""
        for _ in range(3):  # Allow 3 attempts
            pin, ok = QInputDialog.getText(self, 'Enter Pin', 'Enter your 4-digit pin:', QLineEdit.Password)
            if ok:
                hashed_pin = hashlib.sha256(pin.encode()).hexdigest()
                with open(self.pin_file, 'r') as file:
                    stored_pin = file.read()
                if stored_pin == hashed_pin:
                    self.encryption_key = self.generate_key(pin)
                    return
                else:
                    QMessageBox.warning(self, 'Wrong Pin', 'The pin you entered is incorrect.')
        sys.exit()  # Close the app if the user fails to enter the correct pin

    def generate_key(self, pin):
        """Generate a valid Fernet key from the pin."""
        key = hashlib.sha256(pin.encode()).digest()  # Get the SHA-256 hash of the pin
        key = base64.urlsafe_b64encode(key[:32])     # Base64 encode the first 32 bytes
        return Fernet(key)

    def encrypt_journal_files(self):
        """Encrypt all journal files using the pin-based key"""
        if self.encryption_key:
            for root, _, files in os.walk(self.journal_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        data = f.read()
                    encrypted_data = self.encryption_key.encrypt(data)
                    with open(file_path, 'wb') as f:
                        f.write(encrypted_data)

    def decrypt_journal_files(self):
        """Decrypt all journal files using the pin-based key"""
        if self.encryption_key:
            for root, _, files in os.walk(self.journal_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    with open(file_path, 'rb') as f:
                        encrypted_data = f.read()
                    try:
                        data = self.encryption_key.decrypt(encrypted_data)
                        with open(file_path, 'wb') as f:
                            f.write(data)
                    except:
                        pass  # Ignore any decryption errors

    def initUI(self):
        # Full-screen on startup
        self.showFullScreen()

        # Set dark theme
        self.setStyleSheet("""        
            QMainWindow { background-color: #2b2b2b; }
            QTextEdit { background-color: #1e1e1e; color: white; font-size: 16px; padding: 10px; border: none; }
            QTreeView { background-color: #333; color: white; border-right: 1px solid #444; }
            QPushButton { background-color: #555; color: white; border: none; padding: 5px; }
            QPushButton:hover { background-color: #777; }
            QMenuBar { background-color: #2b2b2b; color: white; }
            QMenuBar::item { background: #2b2b2b; }
            QMenuBar::item:selected { background: #444; }
        """)

        # Close only on Ctrl+Q
        exit_action = QAction('Exit', self)
        exit_action.setShortcut(QKeySequence('Ctrl+Q'))
        exit_action.triggered.connect(self.close)

        # Save file with Ctrl+S
        save_action = QAction('Save', self)
        save_action.setShortcut(QKeySequence('Ctrl+S'))
        save_action.triggered.connect(self.save_note)

        # Create menu bar
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction(exit_action)
        file_menu.addAction(save_action)

        self.create_tree_view()
        self.load_today_note()

        # Button to toggle the navigation bar
        toggle_nav_button = QPushButton('Echo', self)
        toggle_nav_button.clicked.connect(self.toggle_navbar)
        self.menuBar().setCornerWidget(toggle_nav_button, Qt.TopLeftCorner)

    def create_tree_view(self):
        # Tree navigation
        self.tree_view = QTreeView(self)
        file_model = QFileSystemModel()
        file_model.setRootPath(self.journal_dir)
        self.tree_view.setModel(file_model)
        self.tree_view.setRootIndex(file_model.index(self.journal_dir))
        self.tree_view.setColumnHidden(1, True)
        self.tree_view.setColumnHidden(2, True)
        self.tree_view.setColumnHidden(3, True)

        # Hide the header (remove "Name" label)
        self.tree_view.header().hide()

        self.tree_view.clicked.connect(self.load_selected_note)

        # Splitter for tree and editor
        self.splitter = QSplitter(self)
        self.splitter.addWidget(self.tree_view)
        self.splitter.addWidget(self.text_edit)
        self.splitter.setSizes([200, 800])

        layout = QVBoxLayout()
        layout.addWidget(self.splitter)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def load_today_note(self):
        # Load today's journal entry
        current_date_dir = os.path.join(self.journal_dir, QDateTime.currentDateTime().toString("yyyy/MMM/dd"))
        if not os.path.exists(current_date_dir):
            os.makedirs(current_date_dir)

        self.current_note_path = os.path.join(current_date_dir, 'journal.txt')
        if os.path.exists(self.current_note_path):
            with open(self.current_note_path, 'r') as file:
                self.text_edit.setText(file.read())
                self.text_edit.setReadOnly(True)
        else:
            self.text_edit.clear()
            self.text_edit.setReadOnly(False)

    def load_selected_note(self, index):
        """Load selected journal note from the tree view"""
        model = self.tree_view.model()
        file_path = model.filePath(index)
        if os.path.isfile(file_path) and file_path.endswith('.txt'):
            with open(file_path, 'r') as file:
                self.text_edit.setText(file.read())
                self.text_edit.setReadOnly(True)
            self.current_note_path = file_path

    def save_note(self):
        if self.current_note_path:
            with open(self.current_note_path, 'w') as file:
                file.write(self.text_edit.toPlainText())
            self.text_edit.setReadOnly(True)
            QMessageBox.information(self, 'Saved', "Journal entry saved and locked.")

    def toggle_navbar(self):
        """Animate the navigation bar to show or hide with a sliding effect."""
        current_width = self.splitter.sizes()[0]
        target_width = 0 if current_width > 0 else 200

        animation = QPropertyAnimation(self.splitter, b'sizes')
        animation.setDuration(500)
        animation.setEasingCurve(QEasingCurve.InOutQuad)
        animation.setStartValue([current_width, self.splitter.sizes()[1]])
        animation.setEndValue([target_width, self.splitter.sizes()[1]])
        animation.start()

    def closeEvent(self, event):
        # Encrypt files before closing the app
        self.encrypt_journal_files()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = JournalApp()
    sys.exit(app.exec_())

