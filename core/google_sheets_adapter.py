import os
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from core.report_builder import OCRReport


# PATTERN 7: ADAPTER
class GoogleSheetsAdapter:
    """
    Adapter pattern: Converts the internal OCRReport object into a format 
    (list of strings) suitable for the Google Sheets API.
    """
    def __init__(self, spreadsheet_id: str):
        self.spreadsheet_id = spreadsheet_id
        self.scopes = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials_file = 'credentials.json'
        self.sheet_name = 'Аркуш1' 
        self.service = self._build_service()

    def _build_service(self):
        """Builds the Google Sheets API service."""
        if not os.path.exists(self.credentials_file):
            print("Warning: credentials.json not found. Google Sheets integration disabled.")
            return None
        
        creds = Credentials.from_service_account_file(self.credentials_file, scopes=self.scopes)
        return build('sheets', 'v4', credentials=creds)

    def save_report(self, report: OCRReport, user_id: int) -> bool:
        """Adapts the OCRReport and sends it to Google Sheets."""
        if not self.service:
            return False

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