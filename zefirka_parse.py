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
from config import TOKEN, URL, URL_2
from PIL import Image
import pyimgur

PARSE_DELAY = 600
DB_NAME = "parse.db"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}


# bot = telebot.TeleBot(TOKEN)

def get_site_content(html):
    print("Старт парсинга сайта Зефирка")
    soup = BeautifulSoup(html.read(), "html.parser")
    items = soup.find_all('article', class_='post-entry')
    for item in items:
        link = item.find('a').get('href')
        parse_article(link)


def get_article_content(html):
    soup = BeautifulSoup(html.read(), "html.parser")
    article_name = soup.find('h1', class_='content-headline').text
    articles = soup.find('div', class_='entry-content-inner')
    folder_name = re.sub("[^A-Za-z^А-Яа-я_]", " ", article_name)
    if not os.path.exists(f"articles/zefirka/{folder_name}"):
        print("Старт парсинга статьи Зефирка")
        path = f"articles/zefirka/{folder_name}"
        os.makedirs(path)
        print("Directory  created")
        articles.select_one('.breadcrumb-navigation').decompose()
        articles.select_one('.content-headline').decompose()
        a = str(articles)
        b = a.partition('<div class="addtoany')[0]
        c = b.replace('<div class="entry-content-inner">', '')
        d = c.replace('h2', 'h3')
        e = re.sub(r'\<p>Источник:.*\</p>;', '', d)
        g = e.replace('jpg"/><br/>', 'jpg"/><br/></p><p>')
        f = g.replace('\n', '')

        create_news(article_name, f)


def create_news(head, main):
    telegraph = Telegraph()
    result = telegraph.create_account(short_name='xdes')
    with open('graph_bot.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)  # сохраняю в файл graph_bots
    with open('graph_bot.json') as f:
        graph_bot = json.load(f)
    telegraph = Telegraph(graph_bot["access_token"])  # передаём токен доступ к страницам аккаунта
    response = telegraph.create_page(
        f'{head}',  # заголовок страницы
        html_content= f"{main}"
        # '<p>Наша история – это история войн. Начиная с бронзового века и до современных дней общество прожило в мире всего 240 лет. В этой статье мы подобрали пятерку наиболее абсурдных вооруженных конфликтов, разыгравшихся по самым ничтожным мотивам. За какие безумные мотивы воевали люди?</p><h3>1.</h3><p><b>Конфликт за похищенное ведро</b><br/><img alt="Пять самых абсурдных войн в истории человечества" class="" src="https://s.zefirka.net/images/2022-08-08/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva-1.jpg"/><br/></p><p>Модена и Болонья на карте</p><p>Эта война разгорелась между итальянскими городами Болонья и Модена в 1325 году. В Средние века Аппенинский полуостров был разделён на множество феодальных владений, между которыми регулярно возникали противоречия. В регионе царили хаос и постоянные пограничные войны.</p><p>Соперничество между соседствующими Болоньей и Моденой тлело уже больше столетия. Осенью 1325 года между ними вспыхнул очередной конфликт. Пользуясь неразберихой, несколько солдат Модены ночью выкрали из колодца в Болонье дубовое ведро. Утром они торжественно продемонстрировали его соотечественникам.</p><p>Для жителей Болоньи акт воровства стал последней каплей терпения. Городской совет потребовал у соседей вернуть пропажу на место. Совет Модены требование проигнорировал.</p><h3>2.</h3><p><img alt="Пять самых абсурдных войн в истории человечества" class="" src="https://s.zefirka.net/images/2022-08-08/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva-2.jpg"/><br/></p><p>Копия ведра, из-за которого началась эта война</p><p>Тогда болонцы собрали двадцатитысячную армию и двинулись на Модену войной. К несчастью для мстителей, сражение они проиграли. С обеих сторон на поле боя остались лежать более 2-х тысяч мужчин.</p><p>Посрамленным болонцам пришлось заключить мир, а украденное ведро (сегодня это его копия), так и висит в колокольне моденского кафедрального собора.</p><p>Ведро, конечно, стало лишь поводом: Болонья и Модена соперничали на протяжении столетий. Но повод всё же попал в историю и стал символом как бессмысленной войны, так и трофеем Модены.</p><h3>3.</h3><p><b>Война между Голландией и архипелагом Силли</b><br/><img alt="Пять самых абсурдных войн в истории человечества" class="" src="https://s.zefirka.net/images/2022-08-08/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva-3.jpg"/><br/></p><p>Архипелаг Силли – 55 крошечных островов, расположенных в 45 км к юго-западу от Англии и входящих в состав Британской короны. В 1641 году в Британии разгорелась гражданская война между сторонниками парламента и роялистами. Голландцы вмешались и поддержали парламентариев.</p><p>Сторонники короля терпели поражение, но их флот смог укрепиться на островах Силли. В 1651 году Голландия объявила этим остаткам роялистов войну. Вскоре повстанцы сдались Лондону, но официального мира между Голландией и островами Силли заключено так не было.</p><p>Это подвешенное состояние продолжалось до 1986 года, пока председатель совета Силли и голландский посол не подписали мир. Фактически, за 335 лет враждующие стороны не произвели друг в друга ни одного выстрела. Формально, все эти годы между ними шла война.</p><h3>4.</h3><p><b>Война с казуарами</b><br/><img alt="Пять самых абсурдных войн в истории человечества" class="" src="https://s.zefirka.net/images/2022-08-08/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva-4.jpg"/><br/></p><p>В 1932 году в Австралии разгорелась ожесточенная война между правительственной армией и… птицами эму. Пернатые разбойники, некогда тысячами обитавшие на западе континента, мешали фермерам выращивать пшеницу. Они ломали заборы, а потом поедали и топтали посевы.</p><p>Жители обратились к властям за помощью. Власти прислали отряд из трёх солдат с двумя пулеметами Льюиса. Однако добиться успеха военнослужащие не смогли. Эму были невероятно пугливы и разбегались при первых выстрелах. Догнать их по пересеченной местности на грузовике также не удавалось.</p><p>Тогда правительство поручило фермерам решать проблему самостоятельно, а чтобы у них был стимул, придумало систему денежных поощрений за каждую подстреленную птицу. Всего за год было убито 60 тысяч пернатых, и вскоре проблема исчезла сама собой.</p><h3>5.</h3><p><b>Футбольная война</b><br/><img alt="Пять самых абсурдных войн в истории человечества" class="" src="https://s.zefirka.net/images/2022-08-08/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva-5.jpg"/><br/></p><p>Серьезный конфликт, произошедший в 1969 году между Сальвадором и Гондурасом. Латиноамериканские государства соседствуют друг с другом и исторически соперничают.</p><p>В злополучный год наметился чемпионат мира по футболу. В отборочном туре встретились команды Сальвадора и Гондураса. Всего было 3 матча. После каждого из них болельщики устраивали погромы друг против друга.</p><p>Когда команда Гондураса проиграла в решающем третьем матче, гонения на сальвадорцев в стране достигли апогея. Сальвадор решил защитить соотечественников и ввёл войска.</p><p>Война шла 6 дней. Потери, учитывая мирное население, составили более 5 тысяч человек. Противостояние было закончено под давлением ООН и для обеих сторон завершилось ничем.</p><h3>6.</h3><p><b>Американо-угандийская война</b><br/><img alt="Пять самых абсурдных войн в истории человечества" class="" src="https://s.zefirka.net/images/2022-08-08/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva/pyat-samyx-absurdnyx-vojn-v-istorii-chelovechestva-6.jpg"/><br/></p><p>Иди Амин</p><p>В 1975 году восточноафриканской Угандой правил Иди Амин – одиозный офицер, пришедший к власти после госпереворота. Деятель был самодуром, увлекался каннибализмом и поддерживал мировой терроризм. Европе, СССР, соседним странам и в особенности США его действия не одобряли. Тогда Иди Амин объявил Вашингтону войну.</p><p>Впрочем, уже на следующий день диктатор собрал конференцию и объявил, что война окончена безоговорочной победой Уганды. Белый дом африканский перформанс просто проигнорировал.</p>'
    )
    print('https://telegra.ph/{}'.format(response['path']))  # распечатываем адрес страницы
    a = 'https://telegra.ph/{}'.format(response['path'])  # распечатываем адрес страницы
    # bot.send_message(534738342, a)
    # bot.send_message(1145437985, a)


def parse_site():
    try:
        html = urlopen(URL_2)
        get_site_content(html)
    except Exception as e:
        print(e)
        print("error site parse")
    threading.Timer(PARSE_DELAY, parse_site).start()


def parse_article(link):
    try:
        html = urlopen(link)
        get_article_content(html)
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
