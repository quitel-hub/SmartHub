import express from 'express';
import cors from 'cors';
import { google } from 'googleapis';
import path from 'path';
import { fileURLToPath } from 'url';


const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const app = express();
app.use(cors());

const CREDENTIALS_PATH = path.resolve(__dirname, '../credentials.json');
const SPREADSHEET_ID = '11Xvb3qQ3ZfVRkIp7TBgcJgd7WIYzfNbnTLzV9fq4K0w'; 

app.get('/api/records', async (req, res) => {
    try {
        const auth = new google.auth.GoogleAuth({
            keyFile: CREDENTIALS_PATH,
            scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
        });

        const client = await auth.getClient();
        const sheets = google.sheets({ version: 'v4', auth: client });

        const response = await sheets.spreadsheets.values.get({
            spreadsheetId: SPREADSHEET_ID,
            range: 'Аркуш1!A:D', 
        });

        const rows = response.data.values;
        if (!rows || rows.length === 0) {
            return res.json([]);
        }

        const records = rows.map((row, index) => {
            const meta = row[0] || '';
            const authorMatch = meta.match(/Author:\s*\*?([^\*|]+)/);
            const typeMatch = meta.match(/Type:\s*\*?([^\*\n\s]+)/);
            const timeMatch = meta.match(/Processed at:\s*\*?([^\*]+)/);

            return {
                id: index.toString(),
                author: authorMatch ? authorMatch[1].trim() : 'Unknown',
                docType: typeMatch ? typeMatch[1].trim() : 'OCR',
                date: timeMatch ? timeMatch[1].trim() : '',
                content: row[3] || 'Текст відсутній'
            };
        }).reverse(); 

        res.json(records);
    } catch (error) {
        console.error('Google Sheets Error:', error);
        res.status(500).json({ error: 'Помилка отримання даних' });
    }
});

const PORT = 5000;
app.listen(PORT, () => {
    console.log(`✅ Backend API server is running on http://localhost:${PORT}`);
});