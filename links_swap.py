from telegraph import Telegraph
import json
import telebot
import re
import requests
import pyimgur
from config import TOKEN, URL, URL_2, IMGUR_TOKEN_1, IMGUR_TOKEN_2

bot = telebot.TeleBot(TOKEN)


def create_news():
    main = input("Подмена ссылок: ")
    result = re.findall(r'\<img alt=.*\ class=""', main)
    x = result[0].replace('<img alt="', '')
    art = re.sub(r'\" class="".*$', '', x)
    print("Жди!")

    urls = re.findall(r'http(?:s)?://\S+"', main)
    for i in urls:
        a = i.replace('"', '')
        p = requests.get(a)
        out = open(f"re_save/{a[-15:]}", "wb")  # скачивание картинки
        out.write(p.content)

        try:
            im = pyimgur.Imgur(IMGUR_TOKEN_1)
            upload = im.upload_image(f"re_save/{a[-15:]}", title="any")
            g = upload.link+'"'
        except:
            im = pyimgur.Imgur(IMGUR_TOKEN_2)
            upload = im.upload_image(f"re_save/{a[-15:]}", title="any")
            g = upload.link + '"'

        main = main.replace(a, g)

    telegraph = Telegraph()
    result = telegraph.create_account(short_name='xdes')
    with open('graph_bot.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)  # сохраняю в файл graph_bots
    with open('graph_bot.json') as f:
        graph_bot = json.load(f)
    telegraph = Telegraph(graph_bot["access_token"])  # передаём токен доступ к страницам аккаунта
    response = telegraph.create_page(
        f'{art}',
        html_content=f"{main}"
    )
    print('https://telegra.ph/{}'.format(response['path']))  # распечатываем адрес страницы
    a = 'https://telegra.ph/{}'.format(response['path'])  # распечатываем адрес страницы
    bot.send_message(534738342, a)


while True:
    try:
        create_news()
    except Exception as e:
        print(e)
