from flask import Flask, request, jsonify
import openai
from ibm_watson import SpeechToTextV1, TextToSpeechV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from dotenv import load_dotenv
import os

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# Obtener las claves API desde las variables de entorno
openai.api_key = os.getenv("OPENAI_API_KEY")
ibm_watson_api_key = os.getenv("IBM_WATSON_API_KEY")
ibm_watson_url = os.getenv("IBM_WATSON_URL")

# Configuración de IBM Watson Speech-to-Text
stt_authenticator = IAMAuthenticator(ibm_watson_api_key)
speech_to_text = SpeechToTextV1(authenticator=stt_authenticator)
speech_to_text.set_service_url(ibm_watson_url)

# Configuración de IBM Watson Text-to-Speech
tts_authenticator = IAMAuthenticator(ibm_watson_api_key)
text_to_speech = TextToSpeechV1(authenticator=tts_authenticator)
text_to_speech.set_service_url(ibm_watson_url)

app = Flask(__name__)

@app.route('/speech-to-text', methods=['POST'])
def speech_to_text_route():
    audio_file = request.files['audio']
    response = speech_to_text.recognize(
        audio=audio_file,
        content_type='audio/wav'
    ).get_result()
    transcript = response['results'][0]['alternatives'][0]['transcript']
    return jsonify({'transcript': transcript})

@app.route('/ask-gpt3', methods=['POST'])
def ask_gpt3():
    data = request.get_json()
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=data['prompt'],
        max_tokens=150
    )
    return jsonify({'response': response.choices[0].text.strip()})

@app.route('/text-to-speech', methods=['POST'])
def text_to_speech_route():
    data = request.get_json()
    response = text_to_speech.synthesize(
        text=data['text'],
        voice='en-US_AllisonV3Voice',
        accept='audio/wav'
    ).get_result()
    audio_content = response.content
    return audio_content, 200, {'Content-Type': 'audio/wav'}

if __name__ == '__main__':
    app.run(debug=True)
