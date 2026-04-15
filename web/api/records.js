import { google } from 'googleapis';

export default async function handler(req, res) {
    try {
        const auth = new google.auth.GoogleAuth({
            credentials: {
                client_email: process.env.GOOGLE_CLIENT_EMAIL,
                private_key: process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
            },
            scopes: ['https://www.googleapis.com/auth/spreadsheets.readonly'],
        });

        const client = await auth.getClient();
        const sheets = google.sheets({ version: 'v4', auth: client });
        const SPREADSHEET_ID = '11Xvb3qQ3ZfVRkIp7TBgcJgd7WIYzfNbnTLzV9fq4K0w';

        const response = await sheets.spreadsheets.values.get({
            spreadsheetId: SPREADSHEET_ID,
            range: 'Аркуш1!A:D', 
        });

        const rows = response.data.values;
        if (!rows || rows.length === 0) {
            return res.status(200).json([]);
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

        return res.status(200).json(records);
    } catch (error) {
        console.error('Google Sheets Error:', error);
        return res.status(500).json({ error: 'Помилка отримання даних' });
    }
}