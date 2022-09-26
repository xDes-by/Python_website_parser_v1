# -*- coding: utf-8 -*-
import re
import requests
import os
import pyimgur
import shutil
import threading
import telebot
import my_sql
from telebot.callback_data import CallbackData
from config import TOKEN, URLS, IMGUR_TOKEN, TELEGRAPH_TOKEN, MY_ID, CHANEL_ID, PARSE_DELAY
from PIL import Image
from bs4 import BeautifulSoup
from urllib.request import urlopen
from telegraph import Telegraph
from datetime import datetime, timedelta
from random import randint
import cron


bot = telebot.TeleBot(TOKEN)
bot.remove_webhook()
call_back_info = CallbackData('title', 'status', 'db', prefix='keyboard')

my_sql_banana = '[index] INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, ' \
                'time_create TIME NOT NULL, ' \
                'article_number INTEGER NOT NULL, ' \
                'article_type STRING DEFAULT NULL, ' \
                'image_link STRING DEFAULT NULL, ' \
                'video_link STRING DEFAULT NULL, ' \
                'article_link STRING DEFAULT NULL, ' \
                'article_name STRING DEFAULT NULL, ' \
                'article_text STRING DEFAULT NULL, ' \
                'time_realize TIME NOT NULL, ' \
                'published BOOL,' \
                'can_published BOOL,'\
                'message_id INTEGER DEFAULT NULL, ' \


my_sql_util = my_sql.my_sql
my_sql_util.create_table('my_sql_banana', my_sql_banana)


def get_site_content(html, site):
    if site == 'banana':
        print(f'Старт парсинга сайта {site}')
        soup = BeautifulSoup(html.read(), 'html.parser')
        items = soup.find_all('div', class_='main_post')  # все новости с первой страницы
        items.pop(0)  # скип первой новости
        for item in items:
            link = item.find('a').get('href')
            article_id = link[-6:]
            in_database = my_sql_util.table_get('my_sql_banana', 'article_number', article_id)
            if not in_database:
                print(f'Статья {article_id} не спаршена, начинаю подготовку')
                parse_article(link, site, article_id)
    else:
        print(f'Старт парсинга сайта {site}')


def get_article_content(html, site, article_id):
    if site == 'banana':
        print(f'Старт парсинга статьи {article_id} с сайта {site}')
        soup = BeautifulSoup(html.read(), 'html.parser')
        article_name = check_name(soup.find('div', class_='post_head').text)
        articles = soup.find('div', id=f'news-id-{article_id}')
        for x in articles.select('span'):
            x.decompose()
        get_content(articles, article_id, article_name)


def check_name(article_name):
    ban_names = ['Попдборка', 'Подборка на видеорегистратор', 'Странные странности', 'Handbra', 'Прикольные картинки',
                 'Улов из социальных сетей', 'Девушки из Зазеркалья',
                 'Модники в метро', 'Красотки в бикини', 'Красивые очкарики', 'Это называется Butt Over Back',
                 'Идеальный мир', 'Расписные девушки', 'Спортивные девушки',
                 'Сокровища из американских комиссионок', 'Пошлые откровения', 'Самое нижнее бельё', 'Неудачи',
                 'Нюдсочетверг', 'Пошлые селфи с работы', 'Разноцветные головы',
                 'Джинсовые леди', 'Дорогая, я все починил сам!', 'Мы хотим тарелки!', 'Вовремя!', 'Полный Underboob!',
                 'Горячие девушки в латексе и коже', 'Линии загара',
                 'Бесполезные факты', 'Красивые азиатки', 'Микрошортики', 'Пятничные эйрбэги', 'Взрослый юмор',
                 'Страх и ненависть в социальных сетях', 'Крупный калибр!', 'Селфи в авто!', ' Затяни корсет потуже']
    for i in ban_names:
        if article_name.find(i) != -1:
            article_name = i

    if not article_name.find('Шкарпэткі, панчохі'):
        article_name = 'Чулки'
    return article_name


@bot.message_handler(commands=['start'])
def start(ms):
    print(ms)
    #my_sql_util.table_delete('my_sql_banana', 301907)
    #parse_site()


@bot.callback_query_handler(func=lambda call: True)
def iq_callback(query):
    user_id = query.from_user.id
    message_id = query.message.id
    data = query.data.split(":")
    if data[2] == "accept":
        article_publish(user_id, message_id, data[1], data[3])
    elif data[2] == "decline":
        article_delete(user_id, message_id, data[1], data[3])


def article_publish(user_id, message_id, art_number, db_table):
    article_in_db = my_sql_util.table_get(db_table, 'article_number', art_number)
    if article_in_db[0][3] == 'small_article' and article_in_db[0][11]:
        img = Image.open(article_in_db[0][4])
        bot.send_photo(CHANEL_ID, img, caption=f'🍳 *{article_in_db[0][7]}*\n\n{article_in_db[0][8]}',
                       parse_mode='Markdown')
    elif article_in_db[0][3] == 'video_article' and article_in_db[0][11]:
        bot.send_message(CHANEL_ID, f'[🍳]({article_in_db[0][5]}) {article_in_db[0][7]}', parse_mode='Markdown')
    elif article_in_db[0][3] == 'big_article' and article_in_db[0][11]:
        bot.send_message(CHANEL_ID, f'[🍳]({article_in_db[0][6]}) {article_in_db[0][7]}', parse_mode='Markdown')
    bot.delete_message(chat_id=user_id, message_id=message_id)
    bot.send_message(MY_ID, 'Новость опубликована', parse_mode='Markdown')
    find_data = {'article_number': art_number}
    update_data = {'published': True}
    my_sql_util.table_update(db_table, find_data, update_data)


def article_delete(user_id, message_id, art_number, db_table):
    bot.delete_message(chat_id=user_id, message_id=message_id)
    bot.send_message(MY_ID, 'Новость удалена из публикации', parse_mode='Markdown')
    find_data = {'article_number': art_number}
    update_data = {'can_published': False}
    my_sql_util.table_update(db_table, find_data, update_data)


def get_content(articles, article_id, article_name):
    if not os.path.exists(f'articles/banana/{article_id}'):
        path = f'articles/banana/{article_id}/images'
        os.makedirs(path)
    video = articles.find('iframe')
    x = articles.get_text(separator='\n')
    text = re.sub(r'\s*([^\n!.?]*?од кат[^!.?]*?[!.?])', '', x)
    time_article_create = datetime.now()
    time_release = created_time_release(time_article_create)
    if video:
        print('Видео контент')
        video_link = '/'.join(video.get('src').split('/')[4:])
        keyboard = buttons(time_release, article_id)
        my_sql_util.table_insert('my_sql_banana', (
            time_article_create, article_id, 'video_article', None, f'https://youtu.be/{video_link}', None, article_name,
            None,
            time_release, False, True))
        bot.send_message(MY_ID, f'[🍳](https://youtu.be/{video_link}) {article_name}', parse_mode='Markdown',
                         reply_markup=keyboard)
    else:
        img_count = articles.findAll('img')
        if len(img_count) == 1 and len(text) < 950:  # max len = 1024
            print('Небольшой объем контента')
            for i in img_count:
                img, local_link = get_img(i, article_id)
                keyboard = buttons(time_release, article_id)
                my_sql_util.table_insert('my_sql_banana', (
                    time_article_create, article_id, 'small_article', local_link, None, None, article_name, text,
                    time_release,
                    False, True))
                bot.send_photo(MY_ID, img, caption=f'🍳 *{article_name}*\n\n{text}', parse_mode='Markdown',
                               reply_markup=keyboard)
        else:
            pass
            print('Большой объем контента')
            for i in img_count:
                img, local_link = get_img(i, article_id)
                try:
                    im = pyimgur.Imgur(IMGUR_TOKEN)
                    upload = im.upload_image(local_link, title='any')
                    i['src'] = upload.link  # подмена ссылок картинки
                except Exception as e:
                    print(f'Тайм-аут имгур!? {e}')
                    my_sql_util.table_delete('my_sql_banana', article_id)
                    shutil.rmtree(f'articles/banana/{article_id}')
                    print(f'Новость {article_id} удалена')
                    return
            a = re.sub(r'\<div id=.*\:inline;"', '<p', str(articles))
            x = a.replace('div', 'p')
            content = re.sub(r'\s*([^\n>!.?]*?од кат[^!.?]*?[!.?])', '', x)
            telegraph = Telegraph(TELEGRAPH_TOKEN)
            response = telegraph.create_page(f'{article_name}', html_content=f'{content}')
            news = 'https://telegra.ph/{}'.format(response['path'])
            keyboard = buttons(time_release, article_id)
            my_sql_util.table_insert('my_sql_banana', (
                time_article_create, article_id, 'big_article', None, None, news, article_name, None,
                time_release,
                False, True))
            bot.send_message(MY_ID, f'[🍳]({news}) {article_name} ', parse_mode='Markdown', reply_markup=keyboard)
    print("Ok")


def buttons(time_release, article_id):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(telebot.types.InlineKeyboardButton(f'Публикация в {time_release.time()} / Опубликовать прямо '
                                                    f'сейчас',
                                                    callback_data=call_back_info.new(title=article_id,
                                                                                     status='accept',
                                                                                     db='my_sql_banana')))
    keyboard.row(telebot.types.InlineKeyboardButton('Удалить из списка публикаций',
                                                    callback_data=call_back_info.new(title=article_id,
                                                                                     status='decline',
                                                                                     db='my_sql_banana')))
    return keyboard


def get_img(i, article_id):
    link_image = i.get('src')
    p = requests.get(link_image)
    local_link = f'articles/banana/{article_id}/images/{link_image[-15:]}'
    with open(local_link, 'wb') as file:
        file.write(p.content)
    img = Image.open(local_link)
    width, height = img.size
    new_image = img.crop((0, 0, width, height - 25))
    new_image.save(local_link)
    return new_image, local_link


def created_time_release(created_time):
    if not cron.TIME_PUBLISH:
        a = datetime.strptime(created_time.strftime("%m/%d/%Y, %H:%M:%S"), "%m/%d/%Y, %H:%M:%S")
        return a + timedelta(minutes=randint(2, 2))
    for i in cron.TIME_PUBLISH[:]:
        a = created_time.date().strftime("%Y-%m-%d") + " " + i #дата + время из таблицы сегодняшняя!
        int_table_date = re.sub("[^0-9]", "", a)
        str_now_time = created_time.strftime("%Y-%m-%d %H:%M")
        int_now_time = re.sub("[^0-9]", "", str_now_time)
        release_time = datetime.strptime(a, "%Y-%m-%d %H:%M")
        if (int(int_now_time) - int(int_table_date)) < 0:
            cron.TIME_PUBLISH.remove(i)
            return release_time + timedelta(minutes=randint(-7, 7))
        else:
            cron.TIME_PUBLISH.remove(i)


def parse_site():
    for site, url in URLS.items():
        try:
            html = urlopen(url, timeout=10)
            get_site_content(html, site)
        except Exception as e:
            print(f'Ошибка парсинга сайта {site} - {e}')
    threading.Timer(PARSE_DELAY, parse_site).start()


def parse_article(link, site, article_id):
    try:
        html = urlopen(link, timeout=10)
        get_article_content(html, site, article_id)
    except Exception as e:
        print(f'Ошибка парсинга статьи {article_id} - {e}')


def main():
    from cron import start_cron
    thread = threading.Thread(target=start_cron)
    thread.start()
    parse_site()
    thread = threading.Thread(target=poll)
    thread.start()
    # bot.polling(none_stop=True)


def poll():
    while True:
        try:
            # bot = telebot.TeleBot(TOKEN, parse_mode=None)
            bot.polling(none_stop=True)
        except Exception as e:
            print(e)
            cron.time.sleep(15)


if __name__ == '__main__':
    main()
