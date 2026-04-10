from flask import Flask
app = Flask(__name__)

from flask import request, abort
from linebot import  LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import openai
import os

openai.api_key = os.getenv('OPENAI_API_KEY')
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler1 = WebhookHandler(os.getenv('CHANNEL_SECRET'))

# 每個使用者的計數器
user_counters = {}

@app.route('/callback', methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)
    try:
        handler1.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler1.add(MessageEvent, message=TextMessage)
def handle_message(event):
    global counter
    text1 = event.message.text
    user_id = event.source.user_id  # 取得使用者ID

    # 如果這個人第一次用，就初始化
    if user_id not in user_counters:
        user_counters[user_id] = 0
        
    response = openai.ChatCompletion.create(
        messages=[
            {
                "role": "system",
                "content": "你是一個專業的雲端工程師助理，個性活潑、回答精簡、會用生活化例子解釋技術問題，並且偶爾帶點幽默。"
            },
            {
                "role": "user",
                "content": text1
            }
        ],
        model="gpt-5-nano",
        temperature = 1,
    )
    try:
        ret = response['choices'][0]['message']['content'].strip()
        
        # 該使用者 +1
        user_counters[user_id] += 1

        count = user_counters[user_id]

        # 把次數加到回覆裡
        ret = f"{ret}\n\n（你已使用 {count} 次）"
    except:
        ret = '發生錯誤！'
    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=ret))

if __name__ == '__main__':
    app.run()
