from telegram import InlineQueryResultArticle, InputTextMessageContent, ChatMember
from telegram.ext import Updater, InlineQueryHandler, CommandHandler, CallbackContext
from yt_dlp import YoutubeDL
from telegram import Update
import os
from queue import Queue
from config import BOT_TOKEN
from config import *


song_queue = Queue()
current_song = None

def is_admin_or_sudo(update: Update) -> bool:
    """Check if the user is an admin in the group or the sudo user."""
    user_id = update.effective_user.id
    if user_id == SUDO_USER_ID:
        return True
    member_status = update.effective_chat.get_member(user_id).status
    return member_status in [ChatMember.ADMINISTRATOR, ChatMember.CREATOR]

def download_audio(url: str):
    # Directory to save the audio file
    output_dir = "downloads"
    os.makedirs(output_dir, exist_ok=True)
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'quiet': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        file_name = os.path.join(output_dir, f"{info['title']}.mp3")
        return file_name

def play_song(update: Update, context: CallbackContext, song_name: str) -> None:
    global current_song
    file_name = download_audio(song_name)
    current_song = file_name
    with open(file_name, 'rb') as audio_file:
        update.message.reply_audio(audio=audio_file)
    update.message.reply_text(f"Now playing: {song_name}")

def play(update: Update, context: CallbackContext) -> None:
    song_name = ' '.join(context.args)
    if not song_name:
        update.message.reply_text("Please provide a song name or URL.")
        return
    song_queue.put(song_name)
    if not current_song:
        play_next_song(update)

def play_next_song(update: Update) -> None:
    if not song_queue.empty():
        song_name = song_queue.get()
        play_song(update, None, song_name)

def skip(update: Update, context: CallbackContext) -> None:
    if not is_admin_or_sudo(update):
        update.message.reply_text("Only admins or the sudo user can use this command.")
        return
    global current_song
    if current_song:
        update.message.reply_text("Skipping current song.")
        os.remove(current_song)
        current_song = None
        play_next_song(update)
    else:
        update.message.reply_text("No song is currently playing.")

def end(update: Update, context: CallbackContext) -> None:
    if not is_admin_or_sudo(update):
        update.message.reply_text("Only admins or the sudo user can use this command.")
        return
    global current_song
    if current_song:
        os.remove(current_song)
        current_song = None
    song_queue.queue.clear()
    update.message.reply_text("Stopped playback and cleared the queue.")

def next(update: Update, context: CallbackContext) -> None:
    if not is_admin_or_sudo(update):
        update.message.reply_text("Only admins or the sudo user can use this command.")
        return
    if not song_queue.empty():
        update.message.reply_text("Playing next song in the queue.")
        play_next_song(update)
    else:
        update.message.reply_text("No more songs in the queue.")

def stop(update: Update, context: CallbackContext) -> None:
    if not is_admin_or_sudo(update):
        update.message.reply_text("Only admins or the sudo user can use this command.")
        return
    global current_song
    if current_song:
        os.remove(current_song)
        current_song = None
    else:
        update.message.reply_text("No song is currently playing.")

def queue(update: Update, context: CallbackContext) -> None:
    if song_queue.empty():
        update.message.reply_text("The queue is empty.")
    else:
        queue_list = list(song_queue.queue)
        update.message.reply_text("Current queue:\n" + "\n".join(queue_list))

def inline_query(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    results = []

    if query:
        results.append(
            InlineQueryResultArticle(
                id=query,
                title="Play Song",
                input_message_content=InputTextMessageContent("Here's your song!"),
                url="https://your-web-app-url.com",
                thumb_url="https://example.com/thumbnail.jpg"
            )
        )

    update.inline_query.answer(results)

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("play", play))
    dispatcher.add_handler(CommandHandler("skip", skip))
    dispatcher.add_handler(CommandHandler("end", end))
    dispatcher.add_handler(CommandHandler("next", next))
    dispatcher.add_handler(CommandHandler("stop", stop))
    dispatcher.add_handler(CommandHandler("queue", queue))
    dispatcher.add_handler(InlineQueryHandler(inline_query))

    updater.start_polling()
    updater.idle()
