import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

# Konfigurasi logging 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ID lembar kerja Google Sheets 
SPREADSHEET_ID = '1Cgjj8fPBsBWVU3ICSOYVfbeKn4WPLZZnYh7JqZxd5Yk'
RANGE_NAME = 'Sheet1!A1:B'

# Mengambil kredensial dari variabel lingkungan 
SERVICE_ACCOUNT_FILE = os.environ.get('GOOGLE_SHEET_CREDENTIALS')

if not SERVICE_ACCOUNT_FILE or not os.path.exists(SERVICE_ACCOUNT_FILE):
    raise Exception("File kredensial tidak ditemukan! Pastikan variabel lingkungan sudah diset dengan benar.")

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Halo! Kirimkan pesan dalam format "Item, Jumlah" (misalnya "Bensin, 20000").')

def record_expense(update: Update, context: CallbackContext) -> None:
    try:
        item, amount = update.message.text.split(', ')
        amount = float(amount)

        creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
        service = build('sheets', 'v4', credentials=creds)

        values = [[item, amount]]
        body = {'values': values}
        
        # Menambahkan data ke Google Sheets 
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption='RAW',
            body=body).execute()

        # Mengambil semua data dari sheet untuk merumuskan ringkasan 
        result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID,
                                                      range=RANGE_NAME).execute()
        
        total_expense = sum(float(row[1]) for row in result.get('values', [])[1:])
        
        update.message.reply_text(f'Pengeluaran berhasil dicatat! Total pengeluaran saat ini: Rp {total_expense:,.0f}')
    
    except ValueError:
         update.message.reply_text('Format pesan tidak valid! Gunakan format "Item, Jumlah".')
    
    except Exception as e:
         update.message.reply_text(f'Terjadi kesalahan: {e}')

def main() -> None:
    TOKEN = '8066770324:AAHQBJAvLB95a1jPGZrKjq0mAzVKWMRCO2w'
    
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command , record_expense))
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
   main()
