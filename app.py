from flask import Flask, render_template, request
import requests
import json

app = Flask(__name__)

def send_discord_message(webhook_url, message, username=None, embed=None, file=None):
    data = {
        "content": message
    }
    if username:
        data["username"] = username

    if embed:
        data["embeds"] = [embed]

    headers = {
        "Content-Type": "application/json"
    }
    
    if file:
        with open(file, 'rb') as f:
            files = {'file': f}
            response = requests.post(webhook_url, data=json.dumps(data), headers=headers, files=files)
    else:
        response = requests.post(webhook_url, data=json.dumps(data), headers=headers)
    
    return response.status_code

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/send', methods=['POST'])
def send():
    webhook_url = request.form['webhook_url']
    message = request.form['message']
    username = request.form.get('username')
    
    # Обработка загруженного файла
    file = request.files.get('file')
    file_path = None
    if file:
        file_path = f"./{file.filename}"
        file.save(file_path)

    # Создание embed
    embed = {}
    embed_title = request.form.get('embed_title')
    embed_description = request.form.get('embed_description')
    embed_color = request.form.get('embed_color')

    if embed_title or embed_description or embed_color:
        embed['title'] = embed_title if embed_title else None
        embed['description'] = embed_description if embed_description else None
        if embed_color:
            # Преобразование цвета из шестнадцатеричного формата в десятичный
            embed['color'] = int(embed_color.lstrip('#'), 16)

    status_code = send_discord_message(webhook_url, message, username, embed if embed else None, file_path)
    
    if file_path:
        import os
        os.remove(file_path)  # Удаляем файл после отправки
    
    if status_code == 204:
        return "Сообщение успешно отправлено!"
    else:
        return f"Не удалось отправить сообщение. Код ответа: {status_code}"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)