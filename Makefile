GRPC_SOURCES = emotion_speech_service_pb2.py emotion_speech_service_pb2_grpc.py

all: $(GRPC_SOURCES)

$(GRPC_SOURCES): emotion_speech_service.proto
	python -m grpc_tools.protoc -I. --python_out=. --grpc_python_out=. emotion_speech_service.proto

clean:
	rm $(GRPC_SOURCES)