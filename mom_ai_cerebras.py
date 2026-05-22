import requests
from flask import Flask, request, jsonify, render_template_string
import threading
import webbrowser

# Cerebras API設定
API_KEY = "csk-59rn25jrthn68rfr868j44d262jhr4tfvf5xd3kmkjcy3wyx"
API_URL = "https://api.cerebras.ai/v1/chat/completions"

app = Flask(__name__)

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>お母さんAIアシスタント - Cerebras版</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }
        .header {
            background: #e91e63;
            color: white;
            padding: 20px;
            text-align: center;
        }
        .header h1 { font-size: 28px; margin-bottom: 5px; }
        .header p { font-size: 14px; opacity: 0.9; }
        .share-info {
            background: #4caf50;
            color: white;
            padding: 10px;
            text-align: center;
            font-size: 12px;
            cursor: pointer;
        }
        .share-info:hover { background: #45a049; }
        .chat-area {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #fafafa;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
            animation: fadeIn 0.3s ease;
        }
        .user-message { justify-content: flex-end; }
        .ai-message { justify-content: flex-start; }
        .bubble {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 20px;
            word-wrap: break-word;
            white-space: pre-wrap;
        }
        .user-message .bubble {
            background: #e91e63;
            color: white;
            border-bottom-right-radius: 5px;
        }
        .ai-message .bubble {
            background: #f1f1f1;
            color: #333;
            border-bottom-left-radius: 5px;
        }
        .input-area {
            padding: 20px;
            background: white;
            border-top: 1px solid #eee;
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 12px;
            border: 1px solid #ddd;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        .input-area input:focus { border-color: #e91e63; }
        .input-area button {
            padding: 12px 24px;
            background: #e91e63;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
        }
        .input-area button:hover { background: #c2185b; }
        .examples {
            padding: 15px 20px;
            background: #f8f8f8;
            border-top: 1px solid #eee;
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
        }
        .example-btn {
            background: #f0f0f0;
            padding: 6px 12px;
            border-radius: 20px;
            font-size: 12px;
            cursor: pointer;
            transition: background 0.2s;
        }
        .example-btn:hover { background: #e0e0e0; }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .typing { color: #999; font-style: italic; padding: 10px; }
        .badge {
            display: inline-block;
            background: #4caf50;
            color: white;
            font-size: 10px;
            padding: 2px 8px;
            border-radius: 10px;
            margin-left: 10px;
            vertical-align: middle;
        }
        .toast {
            position: fixed;
            bottom: 20px;
            left: 50%;
            transform: translateX(-50%);
            background: #333;
            color: white;
            padding: 10px 20px;
            border-radius: 30px;
            font-size: 14px;
            z-index: 1000;
            opacity: 0;
            transition: opacity 0.3s;
            pointer-events: none;
        }
        .toast.show { opacity: 1; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>👵 お母さんAIアシスタント <span class="badge">Cerebras AI</span></h1>
            <p>料理・健康・家計・子育ての相談に乗ります（無料・高速）</p>
        </div>
        <div class="share-info" id="shareInfo" onclick="copyURL()">
            🔗 URLをコピーして共有する
        </div>
        
        <div class="chat-area" id="chatArea">
            <div class="message ai-message">
                <div class="bubble">こんにちは！😊<br>Cerebras AIアシスタントです。<br>料理、健康、家計、子育て、どんなことでも相談してくださいね！<br><br>✨ 無料で高速応答 ✨</div>
            </div>
        </div>
        
        <div class="examples">
            <span class="example-btn" onclick="sendExample('冷蔵庫にあるもので作れる簡単レシピを教えて')">🍳 簡単レシピ</span>
            <span class="example-btn" onclick="sendExample('風邪をひいたときの家庭でのケアを教えて')">💊 健康ケア</span>
            <span class="example-btn" onclick="sendExample('食費を節約するコツを教えて')">💰 節約術</span>
            <span class="example-btn" onclick="sendExample('子供のやる気を引き出す方法を教えて')">👶 子育て</span>
            <span class="example-btn" onclick="sendExample('疲れたときにおすすめのリラックス方法は')">😌 リラックス</span>
            <span class="example-btn" onclick="sendExample('簡単なストレッチを教えて')">🧘 ストレッチ</span>
        </div>
        
        <div class="input-area">
            <input type="text" id="messageInput" placeholder="メッセージを入力..." onkeypress="if(event.keyCode==13) sendMessage()">
            <button onclick="sendMessage()">送信</button>
            <button onclick="clearChat()" style="background:#999;">クリア</button>
        </div>
    </div>
    <div id="toast" class="toast">URLをコピーしました</div>

    <script>
        let currentURL = window.location.href;
        
        function copyURL() {
            navigator.clipboard.writeText(currentURL).then(function() {
                const toast = document.getElementById('toast');
                toast.classList.add('show');
                setTimeout(() => toast.classList.remove('show'), 2000);
            });
        }
        
        async function sendMessage() {
            const input = document.getElementById('messageInput');
            const message = input.value.trim();
            if (!message) return;
            
            addMessage(message, 'user');
            input.value = '';
            showTyping();
            
            try {
                const response = await fetch('/chat', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ message: message })
                });
                const data = await response.json();
                hideTyping();
                addMessage(data.response, 'ai');
            } catch (error) {
                hideTyping();
                addMessage('申し訳ありません。エラーが発生しました。', 'ai');
            }
        }
        
        function sendExample(text) {
            document.getElementById('messageInput').value = text;
            sendMessage();
        }
        
        function addMessage(text, sender) {
            const chatArea = document.getElementById('chatArea');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${sender}-message`;
            messageDiv.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
            chatArea.appendChild(messageDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }
        
        function showTyping() {
            const chatArea = document.getElementById('chatArea');
            const typingDiv = document.createElement('div');
            typingDiv.id = 'typingIndicator';
            typingDiv.className = 'message ai-message';
            typingDiv.innerHTML = '<div class="bubble typing">✨ Cerebras AIが考え中... (無料・高速)</div>';
            chatArea.appendChild(typingDiv);
            chatArea.scrollTop = chatArea.scrollHeight;
        }
        
        function hideTyping() {
            const typing = document.getElementById('typingIndicator');
            if (typing) typing.remove();
        }
        
        function clearChat() {
            const chatArea = document.getElementById('chatArea');
            chatArea.innerHTML = '<div class="message ai-message"><div class="bubble">こんにちは！😊<br>Cerebras AIアシスタントです。<br>料理、健康、家計、子育て、どんなことでも相談してくださいね！<br><br>✨ 無料で高速応答 ✨</div></div>';
        }
        
        function escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        }
    </script>
</body>
</html>
'''

def call_cerebras_api(user_message):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "llama3.1-8b",
        "messages": [
            {"role": "system", "content": "あなたは優しいお母さんアシスタントです。料理、健康、家計、子育ての相談に乗ります。親しみやすく温かい口調で、具体的で実用的なアドバイスをしてください。日本語で簡潔に答えてください。絵文字を適度に使って可愛らしく。"},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 500,
        "temperature": 0.7
    }
    
    try:
        response = requests.post(API_URL, headers=headers, json=data, timeout=30)
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content']
        else:
            return f"APIエラー: {response.status_code}"
    except Exception as e:
        return f"エラーが発生しました: {str(e)}"

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        user_message = data.get('message', '')
        if not user_message:
            return jsonify({"response": "メッセージを入力してください。"})
        reply = call_cerebras_api(user_message)
        return jsonify({"response": reply})
    except Exception as e:
        return jsonify({"response": f"エラー: {str(e)}"})

if __name__ == '__main__':
    print("=" * 60)
    print("👵 お母さんAIアシスタント - Cerebras版")
    print("=" * 60)
    
    # ngrokで公開URLを作成
    try:
        # ngrok認証トークンを設定（必要に応じて）
        # ngrok.set_auth_token("あなたのトークン")
        
        public_url = ngrok.connect(5000)
        print(f"✨ 共有URL: {public_url}")
        print("📱 このURLを家族や友達に送って共有できます")
        print("=" * 60)
        
        # ブラウザで開く
        webbrowser.open("http://localhost:5000")
        webbrowser.open(str(public_url))
        
    except Exception as e:
        print("⚠️ ngrokの起動に失敗しました。ローカルでのみ動作します。")
        print(f"エラー: {e}")
        webbrowser.open("http://localhost:5000")
    
    print("🌐 ローカルURL: http://localhost:5000")
    print("=" * 60)
    print("Ctrl+C で終了します")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
