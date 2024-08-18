import os
import json
import asyncio
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
import yt_dlp
import socketio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

app = FastAPI()
sio = socketio.AsyncServer()
sio.attach(app)

DOWNLOAD_DIR = "./downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

TOKEN = 'YOUR_BOT_TOKEN'
updater = Updater(TOKEN, use_context=True)
dispatcher = updater.dispatcher

def play(update: Update, context: CallbackContext) -> None:
    song_name = ' '.join(context.args)
    if not song_name:
        update.message.reply_text('Please provide a song name.')
        return

    # Generate the Mini App URL with song information
    mini_app_url = f"https://t.me/{context.bot.username}?startapp=song_{song_name.replace(' ', '_')}"

    # Create a button to join the Mini App
    keyboard = [[InlineKeyboardButton("Listen on Web", url=mini_app_url)]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    update.message.reply_text(f'Searching for {song_name}...', reply_markup=reply_markup)

    # Emit the play command to the WebSocket
    asyncio.run(sio.emit('play_song', {'song_name': song_name}))

dispatcher.add_handler(CommandHandler('play', play))

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        if data == 'play':
            await websocket.send_text("Streaming started...")

@app.get("/stream/{filename}")
async def stream(filename: str):
    file_path = os.path.join(DOWNLOAD_DIR, filename)
    return StreamingResponse(open(file_path, "rb"), media_type="audio/mp3")

if __name__ == "__main__":
    updater.start_polling()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
