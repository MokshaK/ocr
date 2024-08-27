import sys
import easyocr
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QComboBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDragEnterEvent, QDropEvent
import pytesseract
from PIL import Image

class OCRApp(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()
        self.reader = easyocr.Reader(['ko', 'en'])  # Initialize EasyOCR with Korean and English

    def initUI(self):
        self.setWindowTitle('Multi-language OCR App')
        self.setGeometry(100, 100, 800, 600)

        main_layout = QHBoxLayout()

        left_layout = QVBoxLayout()

        # Drop area
        self.drop_area = QLabel('Drop Image Here')
        self.drop_area.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.drop_area.setStyleSheet('''
            QLabel {
                border: 2px dashed #aaa;
                border-radius: 5px;
                font-size: 20px;
                color: #555;
            }
        ''')
        self.drop_area.setMinimumSize(300, 400)

        # OCR Engine selection
        self.engine_selector = QComboBox()
        self.engine_selector.addItems(['EasyOCR', 'Tesseract'])

        # Encoding selection
        self.encoding_selector = QComboBox()
        self.encoding_selector.addItems(['utf-8', 'euc-kr', 'cp949'])

        # Reprocess button
        self.reprocess_button = QPushButton('Reprocess')
        self.reprocess_button.clicked.connect(self.reprocess_last_image)

        left_layout.addWidget(self.drop_area)
        left_layout.addWidget(self.engine_selector)
        left_layout.addWidget(self.encoding_selector)
        left_layout.addWidget(self.reprocess_button)

        # Text display area
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setPlaceholderText("Extracted text will appear here")

        main_layout.addLayout(left_layout)
        main_layout.addWidget(self.text_display)

        self.setLayout(main_layout)

        # Enable drag and drop
        self.setAcceptDrops(True)

        self.last_processed_image = None

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            event.accept()
        else:
            event.ignore()

    def dropEvent(self, event: QDropEvent):
        files = [u.toLocalFile() for u in event.mimeData().urls()]
        for file_path in files:
            self.process_image(file_path)

    def process_image(self, file_path):
        self.last_processed_image = file_path
        try:
            if self.engine_selector.currentText() == 'EasyOCR':
                result = self.reader.readtext(file_path)
                extracted_text = '\n'.join([text for _, text, _ in result])
            else:  # Tesseract
                image = Image.open(file_path)
                extracted_text = pytesseract.image_to_string(image, lang='kor+eng')

            encoding = self.encoding_selector.currentText()
            self.text_display.setText(extracted_text.encode(encoding, errors='replace').decode(encoding))
        except Exception as e:
            self.text_display.setText(f"Error processing image: {str(e)}")

    def reprocess_last_image(self):
        if self.last_processed_image:
            self.process_image(self.last_processed_image)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = OCRApp()
    ex.show()
    sys.exit(app.exec())