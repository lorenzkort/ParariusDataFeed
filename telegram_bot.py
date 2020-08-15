import requests

def telegram_send_text(bot_message='Hey this is a text message', chat_id = '-264163246'):
    
    bot_token = '1365447297:AAErgVF73E2pLr5SSK5h4heliyf0EXYt7aw'
    send_text = 'https://api.telegram.org/bot' + bot_token + '/sendMessage?chat_id=' + chat_id + '&parse_mode=Markdown&text=' + bot_message
    response = requests.get(send_text)

    return response.json()

# https://api.telegram.org/bot1365447297:AAErgVF73E2pLr5SSK5h4heliyf0EXYt7aw/getUpdates