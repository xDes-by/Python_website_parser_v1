import time
import schedule as schedule
import config
from banana_parse import Image, bot, datetime, my_sql_util

TIME_PUBLISH = [
    '08:00', '08:20', '08:40',
    '09:00', '09:20', '09:40',
    '10:00', '10:20', '10:40',
    '11:00', '11:20', '11:40',
    '12:00', '12:20', '12:40',
    '13:00', '13:20', '13:40',
    '14:00', '14:20', '14:40',
    '15:00', '15:20', '15:40',
    '16:00', '16:20', '16:40',
    '17:00', '17:20', '17:40',
    '18:00', '18:20', '18:40',
    '19:00', '19:20', '19:40',
    '20:00', '20:20', '20:40',
    '21:00', '21:20', '21:40',
]

def job():
    for i in my_sql_util.table_get_all():
        if not i[10] and i[11] and datetime.now() > datetime.strptime(i[9], "%Y-%m-%d %H:%M:%S"):
            print(f"Публикую новость № {i[2]}")
            article_cron_publish(i)


def article_cron_publish(i):
    try:
        if i[3] == 'small_article':
            img = Image.open(i[4])
            bot.send_photo(config.CHANEL_ID, img, caption=f'🍳 *{i[7]}*\n\n{i[8]}', parse_mode='Markdown')
        elif i[3] == 'video_article' and i[11]:
            bot.send_message(config.CHANEL_ID, f'[🍳]({i[5]}) {i[7]}', parse_mode='Markdown')
        elif i[3] == 'big_article' and i[11]:
            bot.send_message(config.CHANEL_ID, f'[🍳]({i[6]}) {i[7]}', parse_mode='Markdown')
        find_data = {'article_number': i[2]}
        update_data = {'published': True}
        my_sql_util.table_update('my_sql_banana', find_data, update_data)
    except Exception as e:
        print(e)


def reset():
    global TIME_PUBLISH
    TIME_PUBLISH = [
        '08:00', '08:20', '08:40',
        '09:00', '09:20', '09:40',
        '10:00', '10:20', '10:40',
        '11:00', '11:20', '11:40',
        '12:00', '12:20', '12:40',
        '13:00', '13:20', '13:40',
        '14:00', '14:20', '14:40',
        '15:00', '15:20', '15:40',
        '16:00', '16:20', '16:40',
        '17:00', '17:20', '17:40',
        '18:00', '18:20', '18:40',
        '19:00', '19:20', '19:40',
        '20:00', '20:20', '20:40',
        '21:00', '21:20', '21:40',
        '22:00', '22:20', '22:40',
    ]


schedule.every(10).seconds.do(job)
schedule.every().day.at("00:00").do(reset)


def start_cron():
    while True:
        schedule.run_pending()
        time.sleep(1)
