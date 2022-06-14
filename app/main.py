import os
import base64

from datetime import datetime
from google.cloud import storage
from google.cloud import speech
from pydub import AudioSegment

from flask import Flask, request, jsonify
app = Flask(__name__)
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'gc-creds.json'
gsBucket = 'iot-audio'

#上傳檔案到 Google Cloud Storage
def upload_blob(bucket_name, source_file_name, destination_blob_name):

    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)

    blob.upload_from_filename(source_file_name)

    print(
        f"File {source_file_name} uploaded to {destination_blob_name}."
    )

#轉換 base64 內容 to wav 格式檔案
def base64ToWav(data):
    now = datetime.now()
    file_name = now.strftime("%Y%m%d-%H%M%S")

    try:
        with open("audio/" + file_name + ".wav","wb") as f:
            f.write(base64.b64decode(data))
        return file_name
    except Exception as e:
        print(str(e))

#轉換 wav 檔案為 flac 檔案格式
#Web:AI 板的錄音檔的幀率為 11025 需改為 44100 否則無法辨識
def iotWavToFlac(file_name):
    sound = AudioSegment.from_wav("audio/"+file_name+".wav")
    sound = sound.set_frame_rate(44100)
    # 原本是雙聲道，需改為單聲道，節省檔案大小
    sound = sound.set_channels(1)
    # 統一輸出成 flac 音檔格式
    sound.export("audio/"+file_name+".flac", format="flac")

#識別語音並回傳文字 
def recogSpeech(file_name):
    # Instantiates a client
    client = speech.SpeechClient()

    # The name of the audio file to transcribe
    gcs_uri = "gs://" + gsBucket + "/" + file_name + ".flac"

    audio = speech.RecognitionAudio(uri=gcs_uri)

    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.FLAC,
        enable_automatic_punctuation= True,
        sample_rate_hertz=44100,
        enable_separate_recognition_per_channel = True,
        language_code="cmn-Hant-TW",
        model="default",
        audio_channel_count = 1,
    )

    # Detects speech in the audio file
    response = client.recognize(config=config, audio=audio)

    text = ''
    for result in response.results:
        text = result.alternatives[0].transcript
        print("聲音識別: {}".format(text))

    return text

@app.route('/')
def index():
  return "<h1>歡迎使用 Google 語音識別服務 API </h1>"

# 識別 Web:AI 板錄製的聲音
@app.route('/iot-wav', methods=['POST'])
def iotWav():
    '''
    json={'id': 'Web:AI 板的id之類', 'data': 'base64 encode string...'}
    '''
    try:
        file_name = base64ToWav(request.json['data'])
        iotWavToFlac(file_name)
        upload_blob('iot-audio', 'audio/'+file_name+'.flac', file_name+'.flac')
        text = recogSpeech(file_name)
        return jsonify({"success": True, "text":text}), 200
    except Exception as e:
        return f"An Error Occurred: {e}"
