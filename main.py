import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboardColor, VkKeyboard
import psycopg2
from config import host, user, password, db_name, vk_token, admin_id
from vktools import Keyboard, Carousel, Element, Text, ButtonColor

#необходимые переменные
vk_session = vk_api.VkApi(token=vk_token)
session_api = vk_session.get_api()
longpool = VkLongPoll(vk_session)

#подключение к постгрес
connection = psycopg2.connect(
    host=host,
    user=user,
    password=password,
    database=db_name,
)
connection.autocommit = True
cursor = connection.cursor()



#отправка сообщения
def send_some_message(id, some_text, keyboard=None, carousel=None):
    post = {
        "user_id": id,
        "message": some_text,
        "random_id": 0
    }
    if keyboard != None:
        post["keyboard"] = keyboard.get_keyboard()
    if carousel != None:
        post["template"] = carousel.add_carousel()

    vk_session.method("messages.send", post)



for event in longpool.listen():
    if event.type == VkEventType.MESSAGE_NEW:
        if event.to_me:
            msg = event.text.lower()
            id = event.user_id
            if msg == "отправь id":
                send_some_message(id, "id отпралвен")
                print(event.user_id)
            elif msg == "мерч":
                keyboard_main = VkKeyboard(one_time=True)
                buttons_main = ['Весь каталог','В наличии']
                button_colors_main = [VkKeyboardColor.PRIMARY, VkKeyboardColor.SECONDARY]

                for btn_main, btn_color_main in zip(buttons_main, button_colors_main):
                    keyboard_main.add_button(btn_main, btn_color_main)

                send_some_message(id, 'Отфильтруйте поиск', keyboard_main)
            elif msg == "весь каталог":
                cursor.execute("SELECT TITLE, size, price, isavailable FROM merch")
                goods_ves = cursor.fetchall()
                if len(goods_ves) != 0:
                    text_ves = '\n  '.join([' '.join(map(str, x1)) for x1 in goods_ves])
                    text_ves = text_ves.replace('False', 'Нет в наличии')
                    text_ves = text_ves.replace('True', 'В наличии')
                    text_ves = text_ves.replace('None', '')
                    send_some_message(id, (str(text_ves)))
                keyboard = VkKeyboard(one_time=True)
                buttons = ["Меню"]
                button_colors = [VkKeyboardColor.NEGATIVE]

                for btn, btn_color in zip(buttons, button_colors):
                    keyboard.add_button(btn, btn_color)

                send_some_message(id, "Меню", keyboard)

            elif msg == "в наличии":
                cursor.execute("SELECT title, size, price FROM merch WHERE isavailable = True")
                goods = cursor.fetchall()
                if len(goods) != 0:
                    text = '\n   '.join([' '.join(map(str, x)) for x in goods])
                    text = text.replace('False', 'Нет в наличии')
                    text = text.replace('True', 'В наличии')
                    text = text.replace('None', '')
                    send_some_message(id, (str(text)))
                keyboard = VkKeyboard(one_time=True)
                buttons = ["Меню"]
                button_colors = [VkKeyboardColor.NEGATIVE]

                for btn, btn_color in zip(buttons, button_colors):
                    keyboard.add_button(btn, btn_color)

                send_some_message(id, "Меню", keyboard)

            elif msg == "меню":
                if event.user_id != admin_id:
                    keyboard = VkKeyboard(one_time=True)
                    buttons = ["Мерч", "Концерты"]
                    button_colors = [VkKeyboardColor.PRIMARY, VkKeyboardColor.SECONDARY]

                    for btn, btn_color in zip(buttons, button_colors):
                        keyboard.add_button(btn, btn_color)

                    send_some_message(id, "Выберите нужную категорию", keyboard)
                elif event.user_id == admin_id:
                    keyboard = VkKeyboard(one_time=True)
                    buttons = ["Мерч", "Концерты", "admin"]
                    button_colors = [VkKeyboardColor.PRIMARY, VkKeyboardColor.SECONDARY, VkKeyboardColor.NEGATIVE]

                    for btn, btn_color in zip(buttons, button_colors):
                        keyboard.add_button(btn, btn_color)

                    send_some_message(id, "Выберите нужную категорию", keyboard)
            elif msg == "карусель мерча":
                carousel_available = Carousel(
                    [
                        Element(
                            "Первый титульник",
                            "Первое описание товара",
                            "-216515089_457239030",
                            "https://vk.com/market-143314838?w=product-143314838_5867520%2Fquery",
                            [Text("Button 1", ButtonColor.NEGATIVE)]
                        ),
                        Element(
                            "Второй титул",
                            "Описание товара 2",
                            "-216515089_457239030",
                            "https://vk.com/market-143314838?w=product-143314838_5867519%2Fquery",
                            [Text("Button num 2", ButtonColor.POSITIVE)]
                        ),
                        Element(
                            "третий титул",
                            "Описание товара 3",
                            "-216515089_457239030",
                            "https://vk.com/market-143314838?w=product-143314838_5867519%2Fquery",
                            [Text("Button num 3", ButtonColor.PRIMARY)]
                        )
                    ]
                )
                send_some_message(id, "Карусель карусель", carousel=carousel_available)

            elif msg == "admin" and event.user_id == admin_id:
                keyboard = VkKeyboard(one_time=True)
                buttons = ["НаличиеADM", "ТоварыADM", "КоличествоADM"]
                button_colors = [VkKeyboardColor.NEGATIVE, VkKeyboardColor.NEGATIVE, VkKeyboardColor.NEGATIVE]

                for btn, btn_color in zip(buttons, button_colors):
                    keyboard.add_button(btn, btn_color)
                send_some_message(id, "Выберите что хотите изменить", keyboard)



