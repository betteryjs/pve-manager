import telebot
from telebot import types

# 替换为您的Telegram Bot的Token
TOKEN = 'YOUR_TELEGRAM_BOT_TOKEN'

bot = telebot.TeleBot(TOKEN)

# 存储用户状态的字典
user_data = {}


@bot.message_handler(commands=['start', 'menu'])
def handle_start(message):
    user_id = message.from_user.id
    user_data[user_id] = {'level': 1, 'path': []}
    send_menu(user_id)


def send_menu(user_id, message_id=None):
    level = user_data[user_id]['level']
    path = user_data[user_id]['path']

    markup = types.InlineKeyboardMarkup()

    if level > 1:
        back_button = types.InlineKeyboardButton('返回上一层', callback_data='back')
        markup.add(back_button)

    if level > 2:
        home_button = types.InlineKeyboardButton('返回第一层', callback_data='home')
        markup.add(home_button)

    if level == 1:
        button1 = types.InlineKeyboardButton('菜单1', callback_data='menu1')
        button2 = types.InlineKeyboardButton('菜单2', callback_data='menu2')
        markup.add(button1, button2)

    elif level == 2:
        button1 = types.InlineKeyboardButton(f'子菜单1（从{path[-1]}进入）', callback_data='submenu1')
        button2 = types.InlineKeyboardButton(f'子菜单2（从{path[-1]}进入）', callback_data='submenu2')
        markup.add(button1, button2)

    elif level == 3:
        button1 = types.InlineKeyboardButton(f'子菜单3（从{path[-1]}进入）', callback_data='submenu3')
        button2 = types.InlineKeyboardButton(f'子菜单4（从{path[-1]}进入）', callback_data='submenu4')
        markup.add(button1, button2)

    if message_id:
        bot.edit_message_reply_markup(user_id, message_id, reply_markup=markup)
    else:
        bot.send_message(user_id, '选择一个选项：', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    message_id = call.message.message_id
    level = user_data[user_id]['level']

    if data == 'back':
        user_data[user_id]['level'] -= 1
        user_data[user_id]['path'].pop()
        send_menu(user_id, message_id)
        return

    if data == 'home':
        user_data[user_id]['level'] = 1
        user_data[user_id]['path'] = []
        send_menu(user_id, message_id)
        return

    if level == 1:
        user_data[user_id]['level'] = 2
        user_data[user_id]['path'].append(data)
        send_menu(user_id, message_id)

    elif level == 2:
        user_data[user_id]['level'] = 3
        user_data[user_id]['path'].append(data)
        send_menu(user_id, message_id)

    elif level == 3:
        bot.send_message(user_id, f'您选择了{data}。')
        user_data[user_id]['level'] = 1
        user_data[user_id]['path'] = []
        send_menu(user_id, message_id)


bot.polling()
