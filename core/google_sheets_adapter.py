import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from core.report_builder import OCRReport


# PATTERN 7: ADAPTER
class GoogleSheetsAdapter:
    """
    @brief Адаптер для інтеграції з Google Sheets API (Патерн Adapter).
    
    Перетворює внутрішній об'єкт `OCRReport` на формат (список рядків), 
    зрозумілий та придатний для відправки в Google Sheets API.
    """
    def __init__(self, spreadsheet_id: str):
        """
        @brief Ініціалізує адаптер для конкретної таблиці.
        
        @param spreadsheet_id ID документа Google Sheets.
        """
        self.spreadsheet_id = spreadsheet_id
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials_file = 'credentials.json'
        self.sheet_name = 'Аркуш1' 
        self.service = self._build_service()

    def _build_service(self):
        """
        @brief Будує та автентифікує клієнт Google Sheets API.
        
        @return Об'єкт сервісу Google API або None, якщо файл ключів відсутній.
        """
        if not os.path.exists(self.credentials_file):
            print("Warning: credentials.json not found. Google Sheets integration disabled.")
            return None
        
        creds = Credentials.from_service_account_file(self.credentials_file, scopes=self.scopes)
        return build('sheets', 'v4', credentials=creds)

    def save_report(self, report: OCRReport, user_id: int) -> bool:

        """
        @brief Адаптує об'єкт OCRReport та зберігає його як новий рядок у таблиці.
        
        Очищає HTML теги з тексту перед збереженням у таблицю.
        
        @param report Звіт, згенерований після розпізнавання.
        @param user_id ID користувача Telegram, який надіслав запит.
        @return True, якщо дані успішно збережені, False в разі помилки.
        """

        if not self.service:
            return False


        # Адаптація даних: масив для колонок (A, B, C, D)
        row_data = [
            report.metadata.replace('\n', ' '),
            str(user_id),
            report.header,
            report.content.replace('<pre>', '').replace('</pre>', '') 
        ]

        try:
            sheet = self.service.spreadsheets()
            body = {'values': [row_data]}
            
            sheet.values().append(
                spreadsheetId=self.spreadsheet_id,
                range=f"{self.sheet_name}!A:D",
                valueInputOption="USER_ENTERED",
                body=body
            ).execute()
            
            return True
        except Exception as e:
            print(f"Google Sheets Error: {e}")
            return False