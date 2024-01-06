import os
import logging
import grpc

import emotion_speech_service_pb2
import emotion_speech_service_pb2_grpc
from pipeline import EmotionalSpeechRecognition
from concurrent import futures

emotion_speech_interface = os.environ.get('EMOTION_SPEECH_SERVER_INTERFACE', '0.0.0.0')
emotion_speech_port = int(os.environ.get('EMOTION_SPEECH_SERVER_PORT', 5002))

class EmotionSpeechServiceServicer(emotion_speech_service_pb2_grpc.EmotionSpeechServiceServicer):
    
    def __init__(self):
        self.recognizer = EmotionalSpeechRecognition()
        

    def RecognizeEmotion(self, request, context):
        result = self.recognizer(request.audio)
        return emotion_speech_service_pb2.EmotionResponse(emotion=result)
    
    
def serve():
    logging.info("Server starting ...")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=32))
    emotion_speech_service_pb2_grpc.add_EmotionSpeechServiceServicer_to_server(
        EmotionSpeechServiceServicer(),
        server
    )
    server.add_insecure_port('{}:{}'.format(emotion_speech_interface, emotion_speech_port))
    server.start()
    logging.info(f"Started server on {emotion_speech_interface}:{emotion_speech_port}")
    server.wait_for_termination()
    

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    serve()