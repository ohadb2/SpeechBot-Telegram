# !/usr/bin/env python
# -*- coding: utf-8 -*-
from pydub import AudioSegment
import os
import voiceToText
import changeVoiceSpeed
import genderRecognize
import emotionDetect
import languageMenu
import usersDB
import textTranslate

update_id = None
print("Ready")


def echo(bot):
    global update_id, lang
    for update in bot.get_updates(offset=update_id, timeout=10):
        update_id = update.update_id + 1
        # check if the answer is from the language menu
        if update.callback_query:
            if not usersDB.get_user_lang(update.callback_query.message.chat.username):
                user_lang = update.callback_query.data
                usersDB.write_to_db(update.callback_query.message.chat.username, user_lang)
                bot.sendMessage(chat_id=update.callback_query.message.chat.id, text="OK. Your preferred language has "
                                                                                    "been saved.")
                update = None
            else:  # If user not exist in DB
                user_lang = usersDB.get_user_lang(update.callback_query.message.chat.username)
                bot.sendMessage(chat_id=update.callback_query.message.chat.id,
                                text=f"Your preffered language is: {user_lang}, if you want to change please type "
                                     f"'/start'")
        elif update.message.text:
            # /start command
            if "/start" in update.message.text:
                update.message.reply_text(f"Hi {update.message.chat.first_name}, "
                                          f"Good to see you 😀, I'm here to help you.\nFeel free to send me a voice "
                                          f"message and I will text you the voice contents, emotion and speaker's "
                                          f"gender", quote=True)
                # If user already in DB, remove him and send him the language menu to choose a language
                if usersDB.get_user_lang(update.message.chat.username):
                    usersDB.remove_user(update.message.chat.username)
                languageMenu.start(update)
            # Translate option
            elif "translate" in update.message.text and update.message.reply_to_message:
                # Check if the translate request is for text that return from the bot
                if "to your language? Just reply" in update.message.reply_to_message.text:
                    # User can ask to translate only if he choose language in the language menu
                    if usersDB.get_user_lang(update.message.chat.username):
                        text = (update.message.reply_to_message.text).split("text: ", 1)[1].split("\n", 1)[0]
                        user_lang = usersDB.get_user_lang(update.message.chat.username)
                        update.message.reply_text(f"{textTranslate.trans(text, user_lang)}",
                                                  reply_to_message_id=update.message.reply_to_message.message_id)
                    else:  # If user not in DB (not choose preferred language)
                        update.message.reply_text(f"Your preferred language isn't set, please type '/start' to set "
                                                  f"your preferred language.")
                else:  # If user ask to translate other message send him an error
                    update.message.reply_text(f"Sorry, I can't translate it",
                                              reply_to_message_id=update.message.reply_to_message.message_id)
        # User send voice message \ audio file
        elif update.message.voice or update.message.audio:
            user_lang = usersDB.get_user_lang(update.message.chat.username)
            update.message.reply_text(f"Hi {update.message.chat.first_name}, let me listen to this...", quote=True)
            # Save the voice message to file (ogg extension)
            if update.message.voice:
                voiceMsg = bot.get_file(update.message.voice.get_file().file_id)
            elif update.message.audio:
                voiceMsg = bot.get_file(update.message.audio.get_file().file_id)
            voiceMsg.download('tempVoice.ogg')
            # Convert the ogg file to mp3 + wav
            AudioSegment.from_file('tempVoice.ogg').export('voice.mp3', format='mp3')
            AudioSegment.from_file('tempVoice.ogg').export('voice.wav', format='wav')
            # Change the voice speed
            changeVoiceSpeed.changeSpeed('voice.mp3').export('speedVoice.mp3')
            # Convert the voice msg to text (the return value contains the text + language code)
            text = voiceToText.toText('speedVoice.mp3')
            # Can't convert to text (maybe the record doesn't contain speech)
            if text is None:
                text = "The record is empty"
                gender = "Can't recognize"
                emotion = "None"
            else:
                lang = format(text.language_code)
                text = format(text.alternatives[0].transcript)
                gender = genderRecognize.recognize('voice.wav')
                emotions = {'neutral': '😐', 'calm': '😎', 'happy': '😃', 'disgust': '🤮', 'sad': '😟', 'angry': '😡'}
                emotionText = emotionDetect.emotionRecognize('voice.wav')
                if emotionText:
                    emotion = f"{emotions[emotionText]} ({emotionText})"
                else:
                    emotion = "None (Maybe there are many speakers?!)"
            if lang != user_lang:
                # Reply to user with translate option (if the user's lang in DB different from the text's lang)
                update.message.reply_text(
                    f"<u>Speaker's gender:</u> {gender}\n<u>text:</u> {text}\n<u>emotion:</u> {emotion}"
                    f".\n\n<b>Need a translate to your language? Just reply 'translate'</b>",
                    parse_mode='HTML')
            else: # Reply to user without translate option
                update.message.reply_text(
                    f"<u>Speaker's gender:</u> {gender}\n<u>text:</u> {text}\n<u>emotion:</u> {emotion}",
                    parse_mode='HTML')
            # Remove working files
            os.remove("tempVoice.ogg")
            os.remove("voice.wav")
            os.remove("speedVoice.mp3")
            os.remove("voice.mp3")
