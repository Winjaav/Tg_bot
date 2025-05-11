import telebot
from telebot import types as t
from config import token
from datetime import datetime
import pytz
import sqlite3
import ollama

time = datetime.now(pytz.utc)
timezone = pytz.timezone("Asia/Yekaterinburg")
fix_time = time.astimezone(timezone)
date_time = fix_time.strftime("%d/%m/%Y")
time_time = fix_time.strftime("%H:%M")

bot = telebot.TeleBot(token)  # что-то типо ID
MODEL_NAME = "llama3-ru"


def start_markup_start():  # Данные о стартовой кнопке выбора
	markup = t.InlineKeyboardMarkup()
	button1 = t.InlineKeyboardButton(text="Photo", callback_data="send_photo")
	button2 = t.InlineKeyboardButton(text="More information", callback_data="send_text")
	markup.add(button1, button2)
	return markup


def start_markup_button2():  # данные о кнопке выбора 2
	markup = t.InlineKeyboardMarkup()
	button1 = t.InlineKeyboardButton(text="4chan", callback_data="click1_button2")
	button2 = t.InlineKeyboardButton(text="Your ID", callback_data="click2_button2")
	markup.add(button1, button2)
	return markup


def start_markup_button3():  # данные о кнопке выбора 3
	markup = t.InlineKeyboardMarkup()
	button1 = t.InlineKeyboardButton(text="Click 1", callback_data="click1_button3")
	button2 = t.InlineKeyboardButton(text="Click 2", callback_data="click2_button3")
	markup.add(button1, button2)
	return markup


@bot.message_handler(commands=["start"])
def start_message(message):
	bot.send_message(message.chat.id,
					 "Hello, user. \n \nChoose button\n \nPossible commands:\n/commands",
					 reply_markup=start_markup_start())


@bot.callback_query_handler(func=lambda call: True)
def check_click(call):
	try:
		if call.data == "send_photo":
			try:
				with open("USSR.jpg", "rb") as photo:
					
					bot.delete_message(call.message.chat.id, call.message.message_id)
					
					bot.send_photo(call.message.chat.id, photo, caption="USSR")
			except FileNotFoundError:
				bot.edit_message_text("Фото не найдено!",
									  call.message.chat.id,
									  call.message.message_id,
									  reply_markup=None)
		
		elif call.data == "send_text":
			
			bot.edit_message_text("Something new will appear here\n \n Choose button",
								  call.message.chat.id,
								  call.message.message_id)
			
			bot.edit_message_reply_markup(call.message.chat.id,
										  call.message.message_id,
										  reply_markup=start_markup_button2())
		
		elif call.data == "click1_button2":
			try:
				with open("4chan.jpg", "rb") as photo1:
					
					bot.delete_message(call.message.chat.id, call.message.message_id)
					
					bot.send_photo(call.message.chat.id, photo1, caption="rest in peace")
			except FileNotFoundError:
				bot.edit_message_text("Фото не найдено!",
									  call.message.chat.id,
									  call.message.message_id,
									  reply_markup=None)
		
		elif call.data == "click2_button2":
			date_log = time.strftime("%d-%m-%Y")
			time_log = time.strftime("%H:%M:%S")
			bot.edit_message_text(f"ID of this chat: {call.message.chat.id}\n\nDate: {date_log}\n\nTime: {time_log}",
								  call.message.chat.id,
								  call.message.message_id,
								  reply_markup=None)
			
			try:
				db = sqlite3.connect('users.db')
				cursor = db.cursor()
				
				cursor.execute("""CREATE TABLE IF NOT EXISTS user_log (
		                        user_id INTEGER,
		                        date_log INTEGER,
		                        time_log INTEGER)""")
				
				cursor.execute("INSERT INTO user_log (user_id, date_log, time_log) VALUES (?, ?, ?)",
							   (call.message.chat.id, date_log, time_log))
				
				db.commit()
				db.close()
			
			except Exception as e:
				print(f"Ошибка SQL: {e}")
	
	
	
	except Exception as e:
		print(f"Ошибка при обработке нажатия кнопки: {e}")


@bot.message_handler(commands=["commands", "help"])
def commands(commands_chat):
	bot.send_message(commands_chat.chat.id, "All commands:\n\n/start\n/Best_country\n/rest_in_peace\n/Chat_ID"
											"\n\nNEW: /AI")


@bot.message_handler(commands=["Best_country", "best_country"])
def photo_message(message_photo):
	text = "USSR"
	try:
		with open("USSR.jpg", "rb") as photo:
			bot.send_photo(message_photo.chat.id, photo, caption=text)
	except FileNotFoundError:
		bot.send_message(message_photo.chat.id, "Photo not found!")


@bot.message_handler(commands=["rest_in_peace", "rest"])
def photo_message(message_photo):
	text = "rest in peace"
	try:
		with open("4chan.jpg", "rb") as photo:
			bot.send_photo(message_photo.chat.id, photo, caption=text)
	except FileNotFoundError:
		bot.send_message(message_photo.chat.id, "Photo not found!")


@bot.message_handler(commands=["Chat_ID", "chat_id"])
def id_your_chat(message):
	chat_id = message.chat.id
	bot.reply_to(message, "ID of this chat: " + str(chat_id))


@bot.message_handler(commands=["Anime"])
def anime(message):
	chat_id = message.chat.id
	bot.reply_to(message, "ID of this chat: " + str(chat_id))
	date_log = time.strftime("%d/%m/%Y")
	time_log = time.strftime("%H:%M:%S")
	try:
		db = sqlite3.connect('top_anime.db')
		cursor = db.cursor()
		
		cursor.execute("""CREATE TABLE IF NOT EXISTS anime_top (
			                        user_id INTEGER,
			                        date_log INTEGER,
			                        time_log INTEGER,
			                        anime_name TEXT,
			                        top_points INTEGER)""")
		
		cursor.execute("INSERT INTO anime_top (user_id, date_log, time_log) VALUES (?, ?, ?)",
					   (message.chat.id, date_log, time_log))
		db.commit()
		
		db.close()
	
	
	except Exception as e:
		print(f"Ошибка SQL - добавление аниме в топ: {e}")
	
	bot.send_message(message.chat.id, "send anime name")
	bot.register_next_step_handler(message, name_anime, time_log=time_log)


def name_anime(message, time_log):
	db = sqlite3.connect('top_anime.db')
	cursor = db.cursor()
	
	cursor.execute("UPDATE anime_top SET anime_name = ? WHERE time_log = ?", (message.text, time_log))
	
	db.commit()
	db.close()
	bot.send_message(message.chat.id, "How much points u can give at this title?")
	bot.register_next_step_handler(message, points_anime, time_log)


def points_anime(message, time_log):
	try:
		db = sqlite3.connect('top_anime.db')
		cursor = db.cursor()
		
		cursor.execute("UPDATE anime_top SET top_points = ? WHERE time_log = ?", (int(message.text), time_log))
		
		bot.send_message(message.chat.id, "Your opinion is very good!")
		db.commit()
		
	except Exception as e:
		print(f"Ошибка, ТУПОЙ ПОЛЬЗОВАТЕЛЬ: {e}")
		bot.send_message(message.chat.id, "U need to use only INTEGER value")
		bot.register_next_step_handler(message, points_anime, time_log)


@bot.message_handler(commands=["my_anime_top"])
def my_anime_top(message):
	db = sqlite3.connect('top_anime.db')
	try:
		cursor = db.cursor()
		chat_id = message.chat.id
		
		# Проверяем существование пользователя
		user = cursor.execute("SELECT user_id FROM anime_top WHERE user_id = ?", (chat_id,)).fetchone()
		
		if not user:
			# Если пользователя нет, добавляем его
			date_log = time.strftime("%d/%m/%Y")
			time_log = time.strftime("%H:%M:%S")
			cursor.execute("INSERT INTO anime_top (user_id, date_log, time_log) VALUES (?, ?, ?)",
						   (chat_id, date_log, time_log))
			db.commit()
			my_top = ""
			bot.send_message(message.chat.id, "У вас еще нет аниме списка, вы добавлены в db")
			
		else:
			# Если пользователь есть, получаем его топ
			my_top = cursor.execute("SELECT user_id, anime_name, top_points FROM anime_top WHERE user_id = ?",
									(chat_id,)).fetchall()
			print(*my_top)
		# Здесь можно отправить пользователю его топ
		z = ""
		for p in my_top:
			z += str(p)+" "
		
		bot.send_message(message.chat.id, f"{z}")
	except Exception as e:
		print(f"Ошибка: {e}")
		bot.send_message(message.chat.id, "Произошла ошибка при обработке запроса")
	finally:
		db.close()







# BETA TEST


active_ai_chats = {}
user_contexts = {}

SYSTEM_PROMPT = {
	"role": "system",
	"content": """

"""
}


@bot.message_handler(commands=["ai", "Ai", "AI"])  # Регистронезависимые команды
def activate_ai_chat(message):
	chat_id = message.chat.id
	
	# Инициализация контекста с системным промптом
	user_contexts[chat_id] = [SYSTEM_PROMPT]
	active_ai_chats[chat_id] = True
	
	# Стартовое сообщение с инструкциями
	welcome_msg = """🤖 <b>AI-режим активирован</b>

• Я могу обсуждать <i>любые</i> темы без ограничений
• Используйте /stop чтобы выключить
• Контекст сохраняется до отключения


(Пишите запрос как можно более понятно, ИИ находится в бета-тесте и довольно туповат)


Задавайте ваш вопрос:"""
	
	bot.send_message(chat_id, welcome_msg, parse_mode="HTML")


@bot.message_handler(commands=["stop"])
def deactivate_ai_chat(message):
	chat_id = message.chat.id
	if chat_id in active_ai_chats:
		del active_ai_chats[chat_id]
		if chat_id in user_contexts:
			del user_contexts[chat_id]
	bot.reply_to(message, "🛑 AI-режим отключен. Контекст очищен.")


@bot.message_handler(func=lambda msg: True)
def handle_text(message):
	chat_id = message.chat.id
	
	# Проверка активного AI-режима
	if chat_id not in active_ai_chats:
		return
	
	# Добавление сообщения пользователя в контекст
	if chat_id not in user_contexts:
		user_contexts[chat_id] = [SYSTEM_PROMPT]
	
	user_contexts[chat_id].append({"role": "user", "content": message.text})
	bot.send_chat_action(chat_id, 'typing')
	
	try:
		# Запрос к модели с текущим контекстом
		response = ollama.chat(
			model=MODEL_NAME,
			messages=user_contexts[chat_id],
		)
		
		# Сохранение ответа и отправка пользователю
		ai_response = response['message']['content']
		user_contexts[chat_id].append({"role": "assistant", "content": ai_response})
		
		# Форматирование ответа (можно добавить Markdown/HTML)
		bot.reply_to(message, f"🤖 {ai_response}")
	
	except Exception as e:
		print(f"AI Error: {e}")
		bot.reply_to(message, "⚠️ Ошибка генерации. Попробуйте позже.")


bot.polling(non_stop=True)



