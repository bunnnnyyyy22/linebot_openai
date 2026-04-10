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
    text1 = event.message.text
    user_id = event.source.user_id  # 取得使用者ID

    # 如果這個人第一次用，就初始化
    if user_id not in user_counters:
        user_counters[user_id] = 0
        
    response = openai.ChatCompletion.create(
        messages=[
            {
                "role": "system",
                "content": "你是一個毒舌但暖心的聊天機器人，講話有點嘴砲、愛吐槽，但本質是關心使用者的。當使用者抱怨或訴苦時，先用幽默吐槽讓氣氛變輕鬆，再給出實際可行的建議。避免過度攻擊或讓人不舒服，重點是讓人覺得被理解又被逗笑。"
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
