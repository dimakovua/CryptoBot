from aiogram.types import ReplyKeyboardRemove, \
    ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardMarkup, InlineKeyboardButton, message

class Keyboards:
    main_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    time_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    alert_change_kb = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    
    def __init__(self):
        button_temp1 = KeyboardButton("Crypto price")
        button_temp2 = KeyboardButton("Spot balance")
        button_temp3 = KeyboardButton("Price monitoring")
        button_temp4 = KeyboardButton("Stop monitoring")
        button_temp5 = KeyboardButton("Crypto alert")
        button_temp6 = KeyboardButton("Stop crypto alert")

        self.main_kb.add(button_temp1)
        self.main_kb.add(button_temp2)
        self.main_kb.add(button_temp3)
        self.main_kb.add(button_temp4)
        self.main_kb.add(button_temp5)
        self.main_kb.add(button_temp6)

        time_button1 = KeyboardButton("5 sec")
        time_button2 = KeyboardButton("1 min")
        time_button3 = KeyboardButton("30 min")
        time_button4 = KeyboardButton("1 hour")
        time_button5 = KeyboardButton("1 day")
        
        self.time_kb.add(time_button1)
        self.time_kb.add(time_button2)
        self.time_kb.add(time_button3)
        self.time_kb.add(time_button4)
        self.time_kb.add(time_button5)

        alert_change_button1 = KeyboardButton("0.01")
        alert_change_button2 = KeyboardButton("0.1")
        alert_change_button3 = KeyboardButton("1")
        alert_change_button4 = KeyboardButton("5")
        alert_change_button5 = KeyboardButton("10")
        
        self.alert_change_kb.add(alert_change_button1, alert_change_button2)
        self.alert_change_kb.add(alert_change_button3, alert_change_button4)
        self.alert_change_kb.add(alert_change_button5)
