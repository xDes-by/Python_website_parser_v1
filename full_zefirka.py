# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup
from urllib.request import urlopen
import re
import os
import requests

PARSE_DELAY = 600
DB_NAME = "parse.db"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}


def get_site_content(html):
    print("Старт парсинга сайта Зефирка")
    soup = BeautifulSoup(html.read(), "html.parser")
    items = soup.find_all('article', class_='post-entry')
    for item in items:
        link = item.find('a').get('href')
        parse_article(link)


def get_article_content(html, link):
    soup = BeautifulSoup(html.read(), "html.parser")
    article_name = soup.find('h1', class_='content-headline').text
    articles = soup.find('div', class_='entry-content-inner')
    folder_name = re.sub("[^A-Za-z^А-Яа-я_^0-9^ёЁ]", " ", article_name)
    # folder_name = re.sub("[0-9a-zA-Zа-яА-ЯёЁ]", " ", article_name)
    print("Старт парсинга статьи Зефирка")

    if not os.path.exists(f"articles/full_zefirka/{folder_name}"):
        print("Новая статья, создаю папку!")
        path = f"articles/full_zefirka/{folder_name}/1"
        os.makedirs(path)
    else:
        print("Статья уже есть, создаю вложение!")
        count = len([lists for lists in os.listdir(f"articles/full_zefirka/{folder_name}/") if
                     os.path.isdir(os.path.join(f"articles/full_zefirka/{folder_name}/", lists))]) + 1
        path = f"articles/full_zefirka/{folder_name}/{count}"
        os.makedirs(path)

    print("Папка создана, начинаю подготовку статьи!")
    articles.select_one('.breadcrumb-navigation').decompose()
    articles.select_one('.content-headline').decompose()
    a = str(articles)
    b = a.partition('<div class="addtoany')[0]
    c = b.replace('<div class="entry-content-inner">', '')
    d = c.replace('h2', 'h3')
    e = re.sub(r'\<p>Источник:.*\</p>;', '', d)
    g = e.replace('jpg"/><br/>', 'jpg"/><br/></p><p>')
    f = g.replace('\n', '')
    try:
        save_text(f, path)
        download_image(articles, path)
    except:
        print("Ошибка парсинга!")
        with open(f"articles/full_zefirka/logs.txt", 'a', encoding="utf-8") as file:
            file.write(link +'\n')


def save_text(main, path):
    with open(f"{path}/art.txt", 'w', encoding="utf-8") as file:
        file.write(main)


def download_image(articles, path):
    z = articles.findAll("img")
    try:
        for i in z:
            link_image = i.get("src")
            p = requests.get(link_image)
            if not link_image.find("120x120.jpg") != -1:
                out = open(f"{path}/{link_image[-15:]}", "wb")
                out.write(p.content)
    except Exception as e:
        print(e)
        print("error")


def parse_site(URL):
    try:
        html = urlopen(URL)
        get_site_content(html)
    except Exception as e:
        print(e)
        print("error site parse")


def parse_article(link):
    try:
        html = urlopen(link)
        get_article_content(html, link)
    except Exception as e:
        print(e)
        print("error article parse")


for i in range(694, 2282):
    URL = f"https://zefirka.net/page/{i}/"
    print(URL)
    parse_site(URL)
