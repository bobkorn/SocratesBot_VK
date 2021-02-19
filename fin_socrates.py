import random
import re
import ssl
import urllib.error
import urllib.parse
import urllib.request
import vk_api
from bs4 import BeautifulSoup
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

token = ""  # Secret token of your VK community
id_num = ""  # Public id of your community. If you changed it, it can still be found in club settings
vk_session = vk_api.VkApi(token=token)
vk = vk_session.get_api()
longpoll = VkBotLongPoll(vk_session, id_num)


def new_msg(self):
    # Gives reply to any messages ending with "да" or "нет" regardless of lower\uppercase or non-letter characters
    if re.search('(да)\W+', self) is not None or re.search('(да)$', self) is not None:
        return "Обнаружено сообщение оканчивающееся на 'да', срочно посмотрите фильм с Джимом Керри!"

    elif re.search('(нет)\W+', self) is not None or re.search('(нет)$', self) is not None:
        return "Обнаружено сообщение оканчивающееся на 'нет', будьте более позитивным!"


def reply_to_photo():
    # Gives random reply from "replies" list to any photo in group-chat
    fir = 'Странная картинка...'
    sec = 'Отличная картинка!'
    thi = 'Не знаю, мем ли это, но вроде неплохо'
    fou = 'Подойдет для обложки альбома'
    fif = 'Бот не доволен данной картинкой'

    replies = [fir, sec, thi, fou, fif]

    return replies[random.randint(0, 4)]


def reply_to_person(self):
    # Collects public data of anyone who tagged the Bot in group-chat
    profiles = vk.users.get(user_id=self, fields='sex')

    for profile in profiles:
        userlist = list()
        userlist.append(profile.get('first_name'))
        userlist.append(profile.get('sex'))

    return userlist


def give_a_quote():
    # Searches for and returns a random quote of Socrates
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    url = 'https://aforisimo.ru/autor/Сократ/page/' + str(random.randint(1, 6)) + '/'
    html_text = urllib.request.urlopen(url, context=ctx).read()
    soup = BeautifulSoup(html_text, 'html.parser')

    div = soup.find_all("div", class_="af")
    phrases = list()

    for phrase in div:
        phrase = phrase.text
        if phrase.endswith('Подробнее... '):
            phrase = phrase.rstrip('Подробнее...')
        phrases.append(phrase)
    return phrases[random.randint(0, 25)]


def my_dear_socrates():
    print('Started')

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:

            try:

                msg = event.obj.text.lower()
                tag = '[club000000000|@your_bot]'  # Tag of your Bot, consisting of its id_num and tag_name
                if event.from_user:

                    if not event.obj.attachments:

                        print('New message:', msg)
                        print(f'For me by: {event.obj.from_id}')

                        vk.messages.send(
                            user_id=event.obj.from_id,
                            message=new_msg(msg),
                            random_id=random.getrandbits(64)
                        )

                    elif event.obj.attachments[0].get('type') == 'photo':

                        vk.messages.send(
                            user_id=event.obj.from_id,
                            message=reply_to_photo(),
                            random_id=random.getrandbits(64)
                        )

                elif event.from_chat and event.obj.text.find(tag):

                    user = event.obj.from_id

                    if reply_to_person(user)[1] == 2:

                        vk.messages.send(
                            chat_id=event.chat_id,
                            random_id=random.getrandbits(64),
                            message=f"Зачем вызывали, дядюшка {reply_to_person(user)[0]}? Я тут работаю!"
                        )

                    elif reply_to_person(user)[1] == 1:

                        vk.messages.send(
                            chat_id=event.chat_id,
                            random_id=random.getrandbits(64),
                            message=f"Зачем вызывали, госпожа {reply_to_person(user)[0]}? Я тут работаю!"
                        )

                elif event.from_chat:

                    if not event.obj.attachments and event.obj.text.find('цитат') or event.obj.text.find('цитир') != -1:

                        print('New message:', msg)
                        print(f'For me by: {event.chat_id}')
                        vk.messages.send(
                            chat_id=event.chat_id,
                            random_id=random.getrandbits(64),
                            message=give_a_quote()
                        )

                    elif not event.obj.attachments:

                        print('New message:', msg)
                        print(f'For me by: {event.chat_id}')
                        vk.messages.send(
                            chat_id=event.chat_id,
                            random_id=random.getrandbits(64),
                            message=new_msg(msg)
                        )

                    elif event.obj.attachments[0].get('type') == 'photo':

                        vk.messages.send(
                            chat_id=event.chat_id,
                            message=reply_to_photo(),
                            random_id=random.getrandbits(64)
                        )

            except:
                continue


my_dear_socrates()
