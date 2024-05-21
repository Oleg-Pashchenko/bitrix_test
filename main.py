import asyncio

from fast_bitrix24 import Bitrix
import dotenv
import os

import db

dotenv.load_dotenv()
webhook = os.getenv('BITRIX_WEBHOOK')

bitrix = Bitrix(webhook, verbose=False)


async def get_dialog(dialog_id):
    return await bitrix.call(method='im.dialog.get', items={
        'DIALOG_ID': f'chat{dialog_id}'
    })


async def get_calls():
    resp = await bitrix.get_all(method='crm.activity.list', params={
        'OWNER_TYPE_ID': 2,
        'OWNER_ID': 1
    })
    print(resp)


async def read_messages(dialog_id):
    response = await bitrix.get_all(method='im.dialog.messages.get',
                                    params={
                                        'DIALOG_ID': f'chat{dialog_id}', 'LIMIT': 50
                                    })
    messages = response['messages']
    while True:
        lst_id = response['messages'][-1]['id']
        response = await bitrix.get_all(method='im.dialog.messages.get',
                                        params={
                                            'DIALOG_ID': f'chat{dialog_id}', 'LIMIT': 50,
                                            'LAST_ID': lst_id
                                        })
        messages += response['messages']
        if len(response['messages']) == 0:
            break
        new_lst_id = response['messages'][-1]['id']
        if new_lst_id == lst_id:
            break

    return messages


async def read_chats():
    answers = []
    for chat_id in range(52000, 0, -1):
        try:
            dialog = await get_dialog(chat_id)
            if dialog['type'] == 'lines':
                chat_name, guest_name = dialog['name'], dialog['readed_list'][0]['user_name']

                messages_data = await read_messages(chat_id)

                messages_arr = []
                for message in messages_data:
                    is_incoming = dialog['readed_list'][0]['user_id'] == message['author_id']
                    if 'Ответ оператора (telegram_personal)' in message['text']:
                        is_incoming = False
                    message['text'] = message['text'].replace('Ответ оператора (telegram_personal)', '')
                    message = {'chat_name': chat_name, 'guest_name': guest_name, 'chat_id': chat_id,
                               'date': message['date'], 'text': message['text'],
                               'is_incoming': is_incoming}
                    messages_arr.append(message)
                answers.append(messages_arr)
                db.save(chat_name, guest_name, messages_arr)
        except:
            pass

    return None


async def main():
    await read_chats()
    # await get_calls()


if __name__ == '__main__':
    asyncio.run(main())
