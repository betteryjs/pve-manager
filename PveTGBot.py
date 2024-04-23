import signal
import sys

import telebot
from telebot import types


from config import Config
from vms import VMS
from vm import VM


def signal_handler(signal, frame):
    print('You pressed Ctrl+C!')
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

authorized_users = Config["authorized_users"]


def is_authorized(user_identifier):
    # 检查用户 ID 或用户名是否在授权用户列表中

    if str(user_identifier.id) in authorized_users:
        return True
    elif user_identifier.username in authorized_users:
        return True
    return False






bot = telebot.TeleBot(Config["TGBotAPI"])

# 存储用户状态的字典
user_data = {}


@bot.message_handler(commands=['menu'])
def handle_start(message):
    if is_authorized(message.from_user):
        user_id = message.from_user.id
        # chat_id=message.chat.id

        user_data[user_id] = {'level': 1, 'path': []}
        send_menu(user_id)
    else:

        bot.reply_to(message, f"You are not authorized to use this bot. id is {message.from_user.id}"
                              f"username is {message.from_user.username}")


def send_menu(user_id, message_id=None, chat_id=None):
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

        buttons = [
            types.InlineKeyboardButton('PVE关机', callback_data='menu1#button1'),
            types.InlineKeyboardButton('PVE重启', callback_data='menu1#button2'),
            types.InlineKeyboardButton('管理虚拟机', callback_data='menu1#button3'),
            types.InlineKeyboardButton('退出菜单', callback_data='menu1#button4'),
        ]


        for i in range(0, len(buttons), 2):
            row = buttons[i:i + 2]
            markup.add(*row)
        if not chat_id:
            bot.send_message(user_id, '选择一个选项：', reply_markup=markup)
        else:
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="选择一个选项: ",
                                  reply_markup=markup)


    elif level == 2:
        # button1 = types.InlineKeyboardButton(f'子菜单1（从{path[-1]}进入）', callback_data='submenu1')
        # button2 = types.InlineKeyboardButton(f'子菜单2（从{path[-1]}进入）', callback_data='submenu2')
        # markup.add(button1, button2)
        res = VMS().getVM()
        res.sort()
        buttons = [types.InlineKeyboardButton(f'{vm[0]}-{vm[1]}', callback_data=f'menu2#{vm[0]}#{vm[1]}') for vm in res]

        # for i in range(0, len(buttons), 2):
        #     row = buttons[i:i + 2]
        #     markup.add(*row)
        # markup.add(*buttons)

        for button in buttons:
            markup.add(button)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text="选择你要管理的虚拟机: ",reply_markup=markup)



    elif level == 3:

        buttons = [
            types.InlineKeyboardButton(f'开机', callback_data='menu3#button1'),
            types.InlineKeyboardButton(f'关机', callback_data='menu3#button2'),
            types.InlineKeyboardButton(f'重启', callback_data='menu3#button3'),
            types.InlineKeyboardButton(f'断电', callback_data='menu3#button4'),
            types.InlineKeyboardButton(f'强制关机', callback_data='menu3#button5'),
        ]
        vmid = int(path[-1].split("#")[1])
        novm = VM(vmid)

        for button in buttons:
            markup.add(button)
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=novm.current(), parse_mode='HTML',reply_markup=markup)


    # if message_id:
    #     bot.edit_message_reply_markup(user_id, message_id, reply_markup=markup)
    # 
    # 
    # else:
    #     bot.send_message(user_id, '选择一个选项：', reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id
    data = call.data
    message_id = call.message.message_id
    level = user_data[user_id]['level']
    path = user_data[user_id]['path']

    chat_id = call.message.chat.id  # 获取当前聊天的chat_id
    vmsPVE=VMS()

    if data == 'menu1#button1':
        msg = "PVE关机"
        vmsPVE.stopPve()
        bot.send_message(chat_id, msg)
        bot.delete_message(chat_id, message_id)

    elif data == 'menu1#button2':
        msg = "PVE重启"
        vmsPVE.rebootPve()
        bot.send_message(chat_id, msg)
        bot.delete_message(chat_id, message_id)

    elif data == 'menu1#button4':
        bot.delete_message(chat_id, message_id)

    elif data == 'menu1#button3':
        user_data[user_id]['level'] = 2
        user_data[user_id]['path'].append(data)
        send_menu(user_id, message_id=message_id,chat_id=chat_id)

    if data == 'back':
        user_data[user_id]['level'] -= 1
        user_data[user_id]['path'].pop()
        send_menu(user_id, message_id,chat_id=chat_id)

    if data == 'home':
        user_data[user_id]['level'] = 1
        user_data[user_id]['path'] = []
        send_menu(user_id, message_id,chat_id=chat_id)



    if level == 2:
        user_data[user_id]['level'] = 3
        user_data[user_id]['path'].append(data)
        send_menu(user_id, message_id, chat_id)

    if level == 3:
        print(path[-1])
        vmid = int(path[-1].split("#")[1])
        vmname = path[-1].split("#")[2]
        novm = VM(vmid)
        choose = data.split("#")[1]
        # bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=novm.current())

        if choose == "button1":
            novm.start()
            bot.send_message(user_id, f'{vmname}-{vmid} 开机成功')
        elif choose == "button2":
            novm.stop()
            bot.send_message(user_id, f'{vmname}-{vmid} 关机成功')



        elif choose == "button3":
            novm.reboot()
            bot.send_message(user_id, f'{vmname}-{vmid} 重启成功')


        elif choose == "button4":
            novm.shutdown()
            bot.send_message(user_id, f'{vmname}-{vmid} 断电成功')

        elif choose == "button5":
            novm.forceStop()
            bot.send_message(user_id, f'{vmname}-{vmid} 强制关机成功')


        user_data[user_id]['level'] -= 1
        user_data[user_id]['path'].pop()
        send_menu(user_id, message_id,chat_id=chat_id)

if __name__ == '__main__':

    bot.polling()
