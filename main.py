from flask import Flask, jsonify, request, render_template
from litellm import completion
import json
from power_levels import getCharacterAtlas, getCharacterObjFromText

app = Flask(__name__)

# set the context
chat_history = []
campaignObj = {}
systemInstruction = "You are an AI assistant who takes in summaries from dungeons and dragons sessions and act as a database queried with natural language. The land this campaign is in is homebrewed and called Ensonya. \n\n"
rundown = ''
characterAtlas = getCharacterAtlas()

# load in the campaign
with open('static/public/ensonya_story_sessions.json', 'r', encoding="utf-8") as file:
    campaignObj = json.load(file)
    for sesh in campaignObj:
        for chapter in sesh['chapters']:
            rundown += f"{chapter['title']}: {chapter['content']}\n\n"

chat_history.append({"role":"system","content":systemInstruction})
chat_history.append({"role":"user","content":rundown})
chat_history.append({"role":"assistant","content":"Thank you for providing the chapters of your campaign. Ask me anything about them!"})
            
# helpers
def getCharacterObjFromText_main(message):
    return getCharacterObjFromText(message)



# end helpers

# load html
@app.route('/')
def index():
    return render_template('index.html')

# chat history call
@app.route('/api/getChatHistory', methods=['GET'])
def get_chat_history():
    return jsonify({"history":chat_history})

# analyitcs from a given response capture
def captureAnalytics(response):
    return { "prompt_tokens":response['usage']['prompt_tokens'], "completion_tokens":response['usage']['completion_tokens'] }

# normal chat call with history
@app.route('/api/sendMessage', methods=['POST'])
def send_message():
    data = request.get_json()
    userMsg = data.get('message')
    currChatHistory = data.get('history')
    embeddings = getCharacterObjFromText_main(userMsg)

    # Process the message (in this example, just echoing)
    processed_message = {"role": "user", "content": userMsg}
    currChatHistory.append(processed_message)

    # Call the completion function with chat history
    response = completion(model="ollama_chat/mistrallite", api_base="http://localhost:11434", messages=currChatHistory)
    analytics = captureAnalytics(response)
    processed_message = {"role": "bot", "content": response.choices[0].message}
    
    return jsonify({"message":processed_message, "analytics":analytics, "history":currChatHistory, "embeddings":embeddings})

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False, port=5000)
