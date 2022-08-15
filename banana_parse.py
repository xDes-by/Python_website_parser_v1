# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import requests
import os
import json
from telegraph import Telegraph
import time, threading
import telebot
from config import TOKEN, URL, URL_2, IMGUR_TOKEN_1
from PIL import Image
import pyimgur

PARSE_DELAY = 600
DB_NAME = "parse.db"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}

bot = telebot.TeleBot(TOKEN)

def get_site_content(html):
    print("Старт парсинга сайта")
    soup = BeautifulSoup(html.read(), "html.parser")
    items = soup.find_all('div', class_='main_post')
    items.pop(0)
    for item in items:
        article = item.find('span').text
        link = item.find('a').get('href')
        name_table = article.replace(" ", "_")
        name = re.sub("[^A-Za-z^А-Яа-я_]", "", name_table)
        parse_article(link)


def get_article_content(html, link):
    article_id = link[-6:]
    soup = BeautifulSoup(html.read(), "html.parser")
    article_name = soup.find('div', class_='post_head').text
    article_name = check_name(article_name)
    articles = soup.find('div', id=f'news-id-{article_id}')
    if not os.path.exists(f"articles/banana/{article_id}"):
        print("Старт парсинга статьи")
        path = f"articles/banana/{article_id}/article"
        os.makedirs(path)
        print(f"Directory {article_id} created")
        with open(f"articles/banana/{article_id}/article/art.txt", 'w', encoding="utf-8"):
            print("File  created")
        for item in articles:
            a = item.text.split("\n")
            for k in a:
                if len(k) > 3:
                    news = re.sub(r'Под катом', r'В статье', k)
                    with open(f"articles/banana/{article_id}/article/art.txt", 'a', encoding="utf-8") as file:
                        file.write(news + "\n")
        """создание папок и скачивание в них картинок"""
        update_image(articles, article_id, article_name)

def check_name(article_name):
    ban_names = ["Попдборка", "Подборка на видеорегистратор", "Странные странности", "Handbra", "Прикольные картинки", "Улов из социальных сетей", "Девушки из Зазеркалья",
                 "Модники в метро", "Красотки в бикини", "Красивые очкарики", "Это называется Butt Over Back", "Идеальный мир", "Расписные девушки", "Спортивные девушки",
                 "Сокровища из американских комиссионок", "Пошлые откровения", "Самое нижнее бельё", "Неудачи", "Нюдсочетверг", "Пошлые селфи с работы", "Разноцветные головы",
                 "Джинсовые леди", "Дорогая, я все починил сам!", "Мы хотим тарелки!", "Вовремя!", "Полный Underboob!", "Горячие девушки в латексе и коже", "Линии загара",
                 "Бесполезные факты", "Красивые азиатки", "Микрошортики", "Пятничные эйрбэги" ]
    for i in ban_names:
        if article_name.find(i) != -1:
            article_name = i

    if not article_name.find("Шкарпэткі, панчохі"):
        article_name = "Чулки"
    print(article_name)
    return article_name

def update_image(articles, article_id, article_name):
    try:
        path = f"articles/banana/{article_id}/images"
        os.makedirs(path)
        z = articles.findAll("div")
        for i in z:
            link_image = i.find('img').get("src")
            p = requests.get(link_image)
            out = open(f"articles/banana/{article_id}/images/{link_image[-15:]}", "wb")  #скачивание картинки
            out.write(p.content)

            # обрезаем картинку
            img = Image.open(f"articles/banana/{article_id}/images/{link_image[-15:]}")
            size = img.size
            width, height = img.size
            new_image = img.crop((0, 0, width, height - 25))
            new_image.save(f'articles/banana/{article_id}/images/{link_image[-15:]}')

            im = pyimgur.Imgur(IMGUR_TOKEN_1)
            upload = im.upload_image(f"articles/banana/{article_id}/images/{link_image[-15:]}", title="any")
            d = i.find('img') # получение пути для картинки
            d['src'] = upload.link #подмена картинки
            out.close()
    except:
        print("asdasd")

    create_article_for_post(articles, article_name, article_id)


def create_article_for_post(articles, article_name, article_id):
    a = re.sub(r'\<div id=.*\:inline;"', '<p', str(articles))
    x = a.replace("div", "p")
    x = x.replace("span", "p")
    # x = x.replace('<br/>', '\n')
    x = re.sub(r'Под катом', r'В статье', x)
    youtube = re.findall(r'https://www.youtube.com/embed/\w+', x)
    if youtube:
        a = youtube[0]
        youtube_link = a.replace("https://www.youtube.com/embed/", "")
        x = re.sub(r'\<iframe.*\</iframe>',
                   f'<figure><iframe src="/embed/youtube?url=https%3A%2F%2Fwww.youtube.com%2Fwatch%3Fv%3D{youtube_link}"></iframe></figure>',
                   x)
    create_news(article_name, x, article_id)


def create_news(head, main, article_id):
    telegraph = Telegraph()
    result = telegraph.create_account(short_name='1337')
    with open('graph_bot.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)  # сохраняю в файл graph_bot
    with open('graph_bot.json') as f:
        graph_bot = json.load(f)
    telegraph = Telegraph(graph_bot["access_token"])  # передаём токен доступ к страницам аккаунтаs
    response = telegraph.create_page(
        f'{head}',  # заголовок страницы
        html_content=f"{main}"
    )
    print('https://telegra.ph/{}'.format(response['path']))  # распечатываем адрес страницы
    a = 'https://telegra.ph/{}'.format(response['path'])  # распечатываем адрес страницы
    # bot.send_message(534738342, f"[🍳]({a}) {head} ", parse_mode="Markdown") #иван
    # bot.send_message(1145437985, f"[🍳]({a}) {head} ", parse_mode="Markdown") #я


def parse_site():
    try:
        html = urlopen(URL,  timeout=10)
        get_site_content(html)
    except Exception as e:
        print(e)
        print("error site parse")
    threading.Timer(PARSE_DELAY, parse_site).start()


def parse_article(link):
    try:
        html = urlopen(link,  timeout=10)
        print(type(html))
        get_article_content(html, link)
    except Exception as e:
        print(e)
        print("error article parse")

parse_site()

while True:
    try:
        bot = telebot.TeleBot(TOKEN, parse_mode=None)
        bot.polling(none_stop=True)
    except Exception as e:
        print(e)
        time.sleep(15)
