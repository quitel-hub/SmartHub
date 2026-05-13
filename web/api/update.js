import { google } from 'googleapis';

export default async function handler(req, res) {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Метод не підтримується' });
    }

    try {
        const { id, content } = req.body;
        const auth = new google.auth.GoogleAuth({
            credentials: {
                client_email: process.env.GOOGLE_CLIENT_EMAIL,
                private_key: process.env.GOOGLE_PRIVATE_KEY?.replace(/\\n/g, '\n'),
            },
            scopes: ['https://www.googleapis.com/auth/spreadsheets'],
        });

        const client = await auth.getClient();
        const sheets = google.sheets({ version: 'v4', auth: client });
        const SPREADSHEET_ID = '11Xvb3qQ3ZfVRkIp7TBgcJgd7WIYzfNbnTLzV9fq4K0w';

        const rowNumber = parseInt(id) + 1;
        const range = `Аркуш1!D${rowNumber}`;

        await sheets.spreadsheets.values.update({
            spreadsheetId: SPREADSHEET_ID,
            range: range,
            valueInputOption: 'USER_ENTERED',
            requestBody: {
                values: [[content]]
            }
        });

        return res.status(200).json({ success: true });
    } catch (error) {
        console.error('Update Error:', error);
        return res.status(500).json({ error: 'Помилка збереження в Google Sheets' });
    }
}