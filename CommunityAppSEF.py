from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
                             QTabWidget, QTreeWidget, QTreeWidgetItem, QComboBox, QTextEdit, QLineEdit, QFileDialog, 
                             QMessageBox, QCalendarWidget, QSplitter, QProgressDialog, QDialog, QListWidget)
from PyQt5.QtGui import QFont, QColor, QPalette, QPixmap
from PyQt5.QtCore import Qt, QDate, QUrl
from PyQt5.QtWebEngineWidgets import QWebEngineView
import sqlite3
from datetime import datetime
import requests
import base64
import folium
from folium.plugins import HeatMap
import io
import os
from PIL import Image
import tempfile
import json
import webbrowser

# Constants for the API
GEMINI_API_KEY = ''
GEMINI_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent'
GEMINI_VISION_API_URL = 'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent'

class CommunitySafetyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Community Safety Collaboration App")
        self.setGeometry(100, 100, 1200, 800)

        self.apply_theme()

        self.conn = sqlite3.connect('community_safety.db')
        self.create_tables()

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.main_layout = QVBoxLayout(self.main_widget)

        self.tabs = QTabWidget()
        self.main_layout.addWidget(self.tabs)

        self.create_dashboard_tab()
        self.create_report_tab()
        self.create_events_tab()
        self.create_resources_tab()
        self.create_feedback_tab()
        self.create_sos_tab()
        self.create_ai_assistant_tab()
        self.create_heatmap_tab()
        self.create_community_forum_tab()

    def apply_theme(self):
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        palette.setColor(QPalette.WindowText, Qt.black)
        palette.setColor(QPalette.Base, Qt.white)
        palette.setColor(QPalette.AlternateBase, QColor(220, 220, 220))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.black)
        palette.setColor(QPalette.Text, Qt.black)
        palette.setColor(QPalette.Button, QColor(200, 200, 200))
        palette.setColor(QPalette.ButtonText, Qt.black)
        palette.setColor(QPalette.BrightText, Qt.red)
        self.setPalette(palette)

        self.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #CCCCCC; }
            QTabWidget::tab-bar { alignment: center; }
            QTabBar::tab {
                background: #E6E6E6;
                border: 1px solid #CCCCCC;
                border-bottom-color: #CCCCCC;
                padding: 10px;
                margin-right: 2px;
            }
            QTabBar::tab:selected {
                background: #D6E9C6;
                border-bottom-color: #D6E9C6;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #CCCCCC;
                padding: 5px;
                border-radius: 5px;
            }
            QPushButton {
                background-color: #66AFE9;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #1F7AC1;
            }
        """)

    def create_tables(self):
        cursor = self.conn.cursor()
        
        # Drop the table if it exists (Optional: Only if you're okay with losing existing data)
        # cursor.execute('DROP TABLE IF EXISTS reports')

        # Recreate the table with the new schema
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY,
                type TEXT,
                description TEXT,
                location TEXT,
                timestamp TEXT,
                status TEXT,
                media_path TEXT,
                assessment TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY,
                title TEXT,
                description TEXT,
                date TEXT,
                location TEXT,
                organizer TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY,
                category TEXT,
                message TEXT,
                timestamp TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sos (
                id INTEGER PRIMARY KEY,
                emergency_type TEXT,
                location TEXT,
                contact TEXT,
                timestamp TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS forum_posts (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT,
                author TEXT,
                timestamp TEXT
            )
        ''')
        
        self.conn.commit()


    def create_dashboard_tab(self):
        dashboard_tab = QWidget()
        dashboard_layout = QVBoxLayout(dashboard_tab)

        weather_label = QLabel("Weather data would be displayed here")
        weather_label.setFont(QFont("Arial", 14))
        dashboard_layout.addWidget(weather_label)

        self.reports_tree = QTreeWidget()
        self.reports_tree.setHeaderLabels(["Type", "Location", "Status"])
        dashboard_layout.addWidget(self.reports_tree)

        self.refresh_reports()

        self.tabs.addTab(dashboard_tab, "Dashboard")

    def create_report_tab(self):
        report_tab = QWidget()
        report_layout = QVBoxLayout(report_tab)

        label = QLabel("Report a Non-Emergency Concern")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        report_layout.addWidget(label)

        self.concern_type = QComboBox()
        self.concern_type.addItems(["Suspicious Activity", "Community Issue", "Infrastructure Problem", "Other"])
        report_layout.addWidget(QLabel("Type of Concern:"))
        report_layout.addWidget(self.concern_type)

        self.description = QTextEdit()
        report_layout.addWidget(QLabel("Description:"))
        report_layout.addWidget(self.description)

        self.location = QLineEdit()
        report_layout.addWidget(QLabel("Location:"))
        report_layout.addWidget(self.location)

        self.media_path_label = QLabel("No file selected")
        upload_button = QPushButton("Upload Image")
        upload_button.clicked.connect(self.upload_media)
        report_layout.addWidget(upload_button)
        report_layout.addWidget(self.media_path_label)

        self.image_preview = QLabel()
        report_layout.addWidget(self.image_preview)

        submit_button = QPushButton("Submit Report")
        submit_button.clicked.connect(self.submit_report)
        report_layout.addWidget(submit_button)

        self.tabs.addTab(report_tab, "Report Concern")

    def create_events_tab(self):
        events_tab = QWidget()
        events_layout = QVBoxLayout(events_tab)

        label = QLabel("Upcoming Community Events")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        events_layout.addWidget(label)

        self.events_tree = QTreeWidget()
        self.events_tree.setHeaderLabels(["Title", "Date", "Location"])
        events_layout.addWidget(self.events_tree)

        add_event_button = QPushButton("Add Event")
        add_event_button.clicked.connect(self.open_add_event_window)
        events_layout.addWidget(add_event_button)

        refresh_events_button = QPushButton("Refresh Events")
        refresh_events_button.clicked.connect(self.refresh_events)
        events_layout.addWidget(refresh_events_button)

        self.tabs.addTab(events_tab, "Community Events")

    def create_resources_tab(self):
        resources_tab = QWidget()
        resources_layout = QVBoxLayout(resources_tab)

        label = QLabel("Community Resources")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        resources_layout.addWidget(label)

        resources = [
            ("Local Police Department", "123-456-7890", "www.localpd.com"),
            ("Community Center", "987-654-3210", "www.communitycenter.org"),
            ("Mental Health Hotline", "555-123-4567", "www.mentalhealth.org"),
            ("Neighborhood Watch Program", "111-222-3333", "www.neighborhoodwatch.com"),
            ("Youth Mentoring Program", "444-555-6666", "www.youthmentor.org")
        ]

        for name, phone, website in resources:
            resource_label = QLabel(f"{name}\nPhone: {phone}\nWebsite: {website}")
            resource_label.setFont(QFont("Arial", 14))
            resources_layout.addWidget(resource_label)

        self.tabs.addTab(resources_tab, "Community Resources")

    def create_feedback_tab(self):
        feedback_tab = QWidget()
        feedback_layout = QVBoxLayout(feedback_tab)

        label = QLabel("Provide Feedback")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        feedback_layout.addWidget(label)

        self.feedback_category = QComboBox()
        self.feedback_category.addItems(["App Improvement", "Community Suggestion", "Law Enforcement Feedback", "Other"])
        feedback_layout.addWidget(QLabel("Category:"))
        feedback_layout.addWidget(self.feedback_category)

        self.feedback_message = QTextEdit()
        feedback_layout.addWidget(QLabel("Message:"))
        feedback_layout.addWidget(self.feedback_message)

        submit_feedback_button = QPushButton("Submit Feedback")
        submit_feedback_button.clicked.connect(self.submit_feedback)
        feedback_layout.addWidget(submit_feedback_button)

        self.tabs.addTab(feedback_tab, "Feedback")

    def create_sos_tab(self):
        sos_tab = QWidget()
        sos_layout = QVBoxLayout(sos_tab)

        label = QLabel("Emergency SOS Activation")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        sos_layout.addWidget(label)

        self.emergency_type = QComboBox()
        self.emergency_type.addItems(["Medical Emergency", "Crime", "Fire", "Natural Disaster", "Other"])
        sos_layout.addWidget(QLabel("Type of Emergency:"))
        sos_layout.addWidget(self.emergency_type)

        self.sos_location = QLineEdit()
        sos_layout.addWidget(QLabel("Location:"))
        sos_layout.addWidget(self.sos_location)

        self.sos_contact = QLineEdit()
        sos_layout.addWidget(QLabel("Contact Number:"))
        sos_layout.addWidget(self.sos_contact)

        activate_sos_button = QPushButton("Activate SOS")
        activate_sos_button.setStyleSheet("background-color: red; color: white;")
        activate_sos_button.clicked.connect(self.activate_sos)
        sos_layout.addWidget(activate_sos_button)

        self.tabs.addTab(sos_tab, "SOS")

    def create_ai_assistant_tab(self):
        ai_tab = QWidget()
        ai_layout = QVBoxLayout(ai_tab)

        label = QLabel("AI Community Safety Assistant")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        ai_layout.addWidget(label)

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        ai_layout.addWidget(self.chat_display)

        input_layout = QHBoxLayout()
        self.user_input = QLineEdit()
        send_button = QPushButton("Send")
        send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.user_input)
        input_layout.addWidget(send_button)
        ai_layout.addLayout(input_layout)

        self.tabs.addTab(ai_tab, "AI Assistant")

    def create_heatmap_tab(self):
        heatmap_tab = QWidget()
        heatmap_layout = QVBoxLayout(heatmap_tab)

        label = QLabel("Incident Heatmap")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        heatmap_layout.addWidget(label)

        self.heatmap_widget = QWebEngineView()
        heatmap_layout.addWidget(self.heatmap_widget)

        generate_heatmap_button = QPushButton("Generate Heatmap")
        generate_heatmap_button.clicked.connect(self.generate_heatmap)
        heatmap_layout.addWidget(generate_heatmap_button)

        self.tabs.addTab(heatmap_tab, "Incident Heatmap")

    def create_community_forum_tab(self):
        forum_tab = QWidget()
        forum_layout = QVBoxLayout(forum_tab)

        label = QLabel("Community Forum")
        label.setFont(QFont("Arial", 20, QFont.Bold))
        forum_layout.addWidget(label)

        self.forum_posts = QListWidget()
        forum_layout.addWidget(self.forum_posts)

        new_post_button = QPushButton("New Post")
        new_post_button.clicked.connect(self.open_new_post_dialog)
        forum_layout.addWidget(new_post_button)

        self.refresh_forum_posts()

        self.tabs.addTab(forum_tab, "Community Forum")

    def send_message(self):
        user_message = self.user_input.text()
        if user_message:
            self.display_message("You: " + user_message)
            self.user_input.clear()
            self.get_ai_response(user_message)

    def display_message(self, message):
        self.chat_display.append(message)

    def get_ai_response(self, user_message):
        try:
            headers = {
                'Content-Type': 'application/json',
            }
            data = {
                'contents': [{'parts': [{'text': user_message}]}],
            }
            params = {
                'key': GEMINI_API_KEY,
            }
            response = requests.post(GEMINI_API_URL, headers=headers, json=data, params=params)
            
            if response.status_code == 200:
                ai_response = response.json()['candidates'][0]['content']['parts'][0]['text']
                self.display_message("AI Assistant: " + ai_response)
            else:
                self.display_message(f"AI Assistant: Error - Status Code {response.status_code}")
        except Exception as e:
            self.display_message(f"AI Assistant: An error occurred: {str(e)}")

    def upload_media(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Upload Image", "", "Image Files (*.png *.jpg *.jpeg)")
        if file_path:
            self.media_path_label.setText(f"File selected: {file_path}")
            self.media_path = file_path
            self.display_image_preview(file_path)

    def display_image_preview(self, file_path):
        pixmap = QPixmap(file_path)
        scaled_pixmap = pixmap.scaled(300, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.image_preview.setPixmap(scaled_pixmap)

    def submit_report(self):
        concern = self.concern_type.currentText()
        desc = self.description.toPlainText().strip()
        loc = self.location.text().strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not concern or not desc or not loc:
            QMessageBox.critical(self, "Error", "Please fill in all fields")
            return

        media_path = getattr(self, 'media_path', None)

        progress_dialog = QProgressDialog("Analyzing report...", None, 0, 100, self)
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.show()

        assessment = self.get_incident_assessment(concern, desc, loc, media_path, progress_dialog)

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO reports (type, description, location, timestamp, status, media_path, assessment) VALUES (?, ?, ?, ?, ?, ?, ?)",
                       (concern, desc, loc, timestamp, "Pending", media_path, assessment))
        self.conn.commit()

        progress_dialog.close()

        QMessageBox.information(self, "Success", "Report submitted successfully\n\nIncident Assessment:\n" + assessment)
        self.clear_report_fields()
        self.refresh_reports()

    def get_incident_assessment(self, concern, desc, loc, media_path, progress_dialog):
        prompt = f"Analyze the following incident report:\nType: {concern}\nDescription: {desc}\nLocation: {loc}\n\nProvide a detailed assessment including:\n1. Severity level\n2. Potential risks\n3. Recommended actions\n4. Additional resources needed (if any)"
        
        progress_dialog.setValue(25)

        if media_path:
            with open(media_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')
            
            headers = {
                'Content-Type': 'application/json',
            }
            data = {
                'contents': [
                    {
                        'parts': [
                            {'text': prompt},
                            {
                                'inline_data': {
                                    'mime_type': 'image/jpeg',
                                    'data': image_data
                                }
                            }
                        ]
                    }
                ],
            }
            params = {
                'key': GEMINI_API_KEY,
            }
            response = requests.post(GEMINI_VISION_API_URL, headers=headers, json=data, params=params)
        else:
            headers = {
                'Content-Type': 'application/json',
            }
            data = {
                'contents': [{'parts': [{'text': prompt}]}],
            }
            params = {
                'key': GEMINI_API_KEY,
            }
            response = requests.post(GEMINI_API_URL, headers=headers, json=data, params=params)

        progress_dialog.setValue(75)

        if response.status_code == 200:
            assessment = response.json()['candidates'][0]['content']['parts'][0]['text']
        else:
            assessment = f"Error in getting assessment: Status Code {response.status_code}"

        progress_dialog.setValue(100)

        return assessment

    def clear_report_fields(self):
        self.concern_type.setCurrentIndex(0)
        self.description.clear()
        self.location.clear()
        self.media_path_label.setText("No file selected")
        self.image_preview.clear()
        if hasattr(self, 'media_path'):
            del self.media_path

    def open_add_event_window(self):
        add_window = QDialog(self)
        add_window.setWindowTitle("Add New Event")
        add_window.setGeometry(100, 100, 400, 600)

        layout = QVBoxLayout(add_window)

        title_entry = QLineEdit()
        layout.addWidget(QLabel("Event Title:"))
        layout.addWidget(title_entry)

        desc_entry = QTextEdit()
        layout.addWidget(QLabel("Description:"))
        layout.addWidget(desc_entry)

        date_calendar = QCalendarWidget()
        layout.addWidget(QLabel("Date:"))
        layout.addWidget(date_calendar)

        location_entry = QLineEdit()
        layout.addWidget(QLabel("Location:"))
        layout.addWidget(location_entry)

        organizer_entry = QLineEdit()
        layout.addWidget(QLabel("Organizer:"))
        layout.addWidget(organizer_entry)

        save_event_button = QPushButton("Save Event")
        layout.addWidget(save_event_button)

        def save_event():
            title = title_entry.text().strip()
            desc = desc_entry.toPlainText().strip()
            date = date_calendar.selectedDate().toString("yyyy-MM-dd")
            location = location_entry.text().strip()
            organizer = organizer_entry.text().strip()

            if not title or not desc or not date or not location or not organizer:
                QMessageBox.critical(add_window, "Error", "Please fill in all fields")
                return

            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO events (title, description, date, location, organizer) VALUES (?, ?, ?, ?, ?)",
                           (title, desc, date, location, organizer))
            self.conn.commit()

            QMessageBox.information(add_window, "Success", "Event added successfully")
            self.refresh_events()
            add_window.accept()

        save_event_button.clicked.connect(save_event)
        add_window.exec_()

    def refresh_events(self):
        self.events_tree.clear()

        cursor = self.conn.cursor()
        cursor.execute("SELECT title, date, location FROM events ORDER BY date")
        for row in cursor.fetchall():
            QTreeWidgetItem(self.events_tree, list(row))

    def submit_feedback(self):
        category = self.feedback_category.currentText()
        message = self.feedback_message.toPlainText().strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not category or not message:
            QMessageBox.critical(self, "Error", "Please fill in all fields")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO feedback (category, message, timestamp) VALUES (?, ?, ?)",
                       (category, message, timestamp))
        self.conn.commit()

        QMessageBox.information(self, "Success", "Feedback submitted successfully")
        self.clear_feedback_fields()

    def clear_feedback_fields(self):
        self.feedback_category.setCurrentIndex(0)
        self.feedback_message.clear()

    def activate_sos(self):
        emergency_type = self.emergency_type.currentText()
        loc = self.sos_location.text().strip()
        contact = self.sos_contact.text().strip()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not emergency_type or not loc or not contact:
            QMessageBox.critical(self, "Error", "Please fill in all fields")
            return

        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO sos (emergency_type, location, contact, timestamp) VALUES (?, ?, ?, ?)",
                       (emergency_type, loc, contact, timestamp))
        self.conn.commit()

        QMessageBox.warning(self, "SOS Activated", "Emergency services have been notified. Stay safe!")
        self.clear_sos_fields()

    def clear_sos_fields(self):
        self.emergency_type.setCurrentIndex(0)
        self.sos_location.clear()
        self.sos_contact.clear()

    def refresh_reports(self):
        self.reports_tree.clear()

        cursor = self.conn.cursor()
        cursor.execute("SELECT type, location, status FROM reports ORDER BY timestamp DESC LIMIT 5")
        for row in cursor.fetchall():
            QTreeWidgetItem(self.reports_tree, list(row))

    def generate_heatmap(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT location FROM reports")
        locations = cursor.fetchall()

        m = folium.Map(location=[0, 0], zoom_start=2)
        heat_data = []
        for loc in locations:
            try:
                lat_lon = loc[0].split(',')
                if len(lat_lon) == 2:
                    lat, lon = map(float, lat_lon)
                    heat_data.append([lat, lon])
                    folium.Marker(location=[lat, lon], popup=loc[0]).add_to(m)
            except ValueError:
                continue

        HeatMap(heat_data).add_to(m)

        # Save to a temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.html')
        m.save(temp_file.name)
        
        # Load the temporary file in QWebEngineView
        self.heatmap_widget.load(QUrl.fromLocalFile(temp_file.name))

        QMessageBox.information(self, "Heatmap Generated", "Heatmap has been generated and displayed.")

    def open_new_post_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("New Forum Post")
        layout = QVBoxLayout(dialog)

        title_entry = QLineEdit()
        layout.addWidget(QLabel("Title:"))
        layout.addWidget(title_entry)

        content_entry = QTextEdit()
        layout.addWidget(QLabel("Content:"))
        layout.addWidget(content_entry)

        author_entry = QLineEdit()
        layout.addWidget(QLabel("Author:"))
        layout.addWidget(author_entry)

        submit_button = QPushButton("Submit Post")
        layout.addWidget(submit_button)

        def submit_post():
            title = title_entry.text().strip()
            content = content_entry.toPlainText().strip()
            author = author_entry.text().strip()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if not title or not content or not author:
                QMessageBox.critical(dialog, "Error", "Please fill in all fields")
                return

            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO forum_posts (title, content, author, timestamp) VALUES (?, ?, ?, ?)",
                           (title, content, author, timestamp))
            self.conn.commit()

            QMessageBox.information(dialog, "Success", "Post submitted successfully")
            dialog.accept()
            self.refresh_forum_posts()

        submit_button.clicked.connect(submit_post)
        dialog.exec_()

    def refresh_forum_posts(self):
        self.forum_posts.clear()
        cursor = self.conn.cursor()
        cursor.execute("SELECT title, author, timestamp FROM forum_posts ORDER BY timestamp DESC")
        for row in cursor.fetchall():
            self.forum_posts.addItem(f"{row[0]} - by {row[1]} on {row[2]}")

        self.forum_posts.itemClicked.connect(self.show_post_details)

    def show_post_details(self, item):
        title = item.text().split(' - ')[0]
        cursor = self.conn.cursor()
        cursor.execute("SELECT content, author, timestamp FROM forum_posts WHERE title = ?", (title,))
        post = cursor.fetchone()

        if post:
            content, author, timestamp = post
            details = QMessageBox(self)
            details.setWindowTitle("Post Details")
            details.setText(f"Title: {title}\n\nAuthor: {author}\nDate: {timestamp}\n\nContent:\n{content}")
            details.setStandardButtons(QMessageBox.Ok)
            details.exec_()

if __name__ == "__main__":
    app = QApplication([])
    window = CommunitySafetyApp()
    window.show()
    app.exec_()
