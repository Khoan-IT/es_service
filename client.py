import os
import grpc
import emotion_speech_service_pb2
import emotion_speech_service_pb2_grpc
import soundfile as sf

MONITOR_SERVER_INTERFACE = os.environ.get('HOST', '0.0.0.0')
MONITOR_SERVER_PORT = int(os.environ.get('PORT', 5002))

CHANNEL_IP = f"{MONITOR_SERVER_INTERFACE}:{MONITOR_SERVER_PORT}"

def main():
    channel = grpc.insecure_channel(f'[::]:{MONITOR_SERVER_PORT}')
    stub = emotion_speech_service_pb2_grpc.EmotionSpeechServiceStub(channel)
        
    data, _ = sf.read('/home/duckhoan/Documents/Code/VLSP-TTS/ESD-W2V2/data/ESD/0001/Angry/0001_000388.wav')

    result = stub.RecognizeEmotion(emotion_speech_service_pb2.AudioRequest(audio=data.tobytes()))
    print(result.emotion)
    
if __name__ == "__main__":
    main()