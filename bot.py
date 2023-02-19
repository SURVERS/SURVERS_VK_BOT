import vk_api
import configparser
from python_rucaptcha import ImageCaptcha
import random
import time
from datetime import datetime as dt
import requests
import re

def print_bot(text):
    print(f"[SURVERS VK BOT]: {text}")

config = configparser.ConfigParser()
config.read('config/vk_accounts.ini')
headers = ({'User-Agent': config["SETTINGS"]["User_Agent"]})

print("\n")
print("----------------------------------------------------")
print("     Создатель: SURVERS FAMILY                      ")
print("     Все настройки находятся в папке \"config\"     ")
print("     Скрипт успешно запустился!                     ")
print("----------------------------------------------------")
print("\n")

proxy_ip = config["SETTINGS"]["Proxy_IP"]
proxy_port = config["SETTINGS"]["Proxy_Port"]
proxy_user = config["SETTINGS"]["Proxy_User"]
proxy_pass = config["SETTINGS"]["Proxy_Pass"]
proxies = {
    "http": f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}/",
    "https": f"http://{proxy_user}:{proxy_pass}@{proxy_ip}:{proxy_port}/"
}

url = 'https://api.ipify.org'

try:
    print_bot("Прокси к бот успешно подключился!")
    print_bot("Идёт загрузка бота...")
    response = requests.get(url, proxies=proxies)
    assert response.text==proxy_ip
    groups_id = open("config/groups.txt", "r").read().split("\n")
    if len(groups_id) > 0:
        messages_id = open("config/messages.txt", "r").read().split("\n")
        if len(messages_id) > 0:
            max_accounts = config['SETTINGS']['Max_Accounts']
            time_next = config['SETTINGS']['Time_next']
            accounts = []
            passwords = []
            vk_session = []
            auth_success = []
            vk = []
            turn_bot = 0

            def captcha_handler(captcha_url):
                user_answer = ImageCaptcha.ImageCaptcha(rucaptcha_key=config['SETTINGS']['RuCaptcha']).captcha_handler(
                    captcha_link=captcha_url)
                if not user_answer['error']:
                    return user_answer['captchaSolve']

            def StartPost(id):
                if auth_success[id] == True:
                    global turn_bot
                    now = dt.now()
                    random_message = random.randrange(len(messages_id))
                    random_group = random.randrange(len(groups_id))

                    result = messages_id[random_message]

                    while re.search(r'{.*}', result):
                        result = re.sub(
                            r'{([^{}]*)}', 
                            lambda m: random.choice(m.group(1).split('|')), 
                            result)

                    vk[id].wall.post(owner_id=f"-{groups_id[random_group]}", message=result, attachments=config["SETTINGS"]["Photo_Post"])
                    print_bot(f"Бот №{id + 1} отпубликовал пост в группе https://vk.com/club{groups_id[random_group]}. Время: {now.strftime('%H:%M:%S')} Текст: {result}")
                    time.sleep(int(time_next))
                    if id != int(max_accounts):
                        turn_bot = id + 1
                    else:
                        turn_bot = 0
                    StartPost(turn_bot)

            def AuthBot(id):
                global auth_success
                user_id = f"user_{id + 1}"
                pass_id = f"pass_{id + 1}"
                accounts.append(config["ACCOUNTS"][user_id])
                passwords.append(config["PASSWORDS"][pass_id])
                print_bot(f"Идёт авторизация аккаунта {accounts[id]}...")
                vk_session.append(vk_api.VkApi(login=accounts[id], password=passwords[id], scope='friends,wall,groups,offline'))
                try:
                    vk_session[id].auth()
                    vk.append(vk_session[id].get_api())
                    auth_success.append(True)
                    if id != int(max_accounts):
                        AuthBot(id + 1)
                    StartPost(id)
                except vk_api.exceptions.Captcha as captcha:
                    captcha.try_again(captcha_handler(captcha.get_url()))
                    print(f"Боту вылезла капча, бот успешно ее прошёл! Пост был повторно отпубликован!")
                    AuthBot(id)

            AuthBot(0)
        else:
            print_bot("Не найден файл config/messages.txt ибо в этом файле нету ни одного сообщения!")
            print_bot("Скрипт был выключен.")
            time.sleep(1000000)

    else:
        print_bot("Не найден файл в config/groups.txt ибо в этом файле нету ни одной группы!")
        print_bot("Скрипт был выключен.")
        time.sleep(1000000)
except FileNotFoundError as e:
    print_bot("Прокси не удалось подключить по неизвестной ошибке!")
    print_bot(f"Ошибка: {e}")
    time.sleep(100000)
