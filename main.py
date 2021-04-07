import json
import logging

from flask import Flask, request

app = Flask(__name__)

logging.basicConfig(level=logging.DEBUG)

sessionStorage = {}

animals = {
    'слон': {
        'to_buy': 'слона',
        'url': "https://market.yandex.ru/search?text=слон"
    },
    'кролик': {
        'to_buy': 'кролика',
        'url': "https://market.yandex.ru/search?text=кролик"
    }
}


@app.route('/post', methods=['POST'])
def main():
    logging.info(f'Request: {request.json!r}')
    print(request.json)
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }

    if handle_dialog(request.json, response, 'слон'):
        handle_dialog(request.json, response, 'кролик')

    logging.info(f'Response:  {response!r}')

    return json.dumps(response)


def handle_dialog(req, res, animal='слон', end_session=True):
    user_id = req['session']['user_id']

    if req['session']['new']:
        sessionStorage[user_id] = {
            'suggests': [
                "Не хочу.",
                "Не буду.",
                "Отстань!",
            ]
        }
        res['response']['text'] = f'Привет! Купи {animals[animal]["to_buy"]}!'
        res['response']['buttons'] = get_suggests(user_id, animal)
        return

    original_command = req['request']['original_utterance'].lower()

    if original_command in [
        'ладно',
        'куплю',
        'покупаю',
        'хорошо'
    ] or 'покупаю' in original_command or 'куплю' in original_command:
        res['response']['text'] = f'{animals[animal]["to_buy"].capitalize()} можно найти на Яндекс.Маркете!'
        res['response']['end_session'] = end_session
        return True

    # Если нет, то убеждаем его купить слона!
    res['response']['text'] = \
        f"Все говорят '{req['request']['original_utterance']}', а ты купи {animals[animal]['to_buy']}!"
    res['response']['buttons'] = get_suggests(user_id, animal)


def get_suggests(user_id, animal):
    session = sessionStorage[user_id]
    suggests = [
        {'title': suggest, 'hide': True}
        for suggest in session['suggests'][:2]
    ]

    session['suggests'] = session['suggests'][1:]
    sessionStorage[user_id] = session

    if len(suggests) < 2:
        suggests.append({
            "title": "Ладно",
            "url": animals[animal]['url'],
            "hide": True
        })

    return suggests


if __name__ == '__main__':
    app.run()
