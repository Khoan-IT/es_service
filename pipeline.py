import torch
import numpy as np

from torch import nn
from omegaconf import OmegaConf
from io import BytesIO
from transformers import Wav2Vec2FeatureExtractor
from tqdm import tqdm

from architecture import SiameseNetworkForSpeechClassification



class EmotionalSpeechRecognition():

    def __init__(self):
        self.args = self.get_config()

        if self.args.common.use_cuda:
            self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        else:
            self.device = torch.device('cpu')

        self.model = self.get_model()
        self.feature_extractor = Wav2Vec2FeatureExtractor.from_pretrained(self.args.model.model_name_or_path)
        self.classes = list(self.args.model.classes)


    def get_config(self):
        return OmegaConf.load("./config.yaml")


    def get_model(self):
        model = SiameseNetworkForSpeechClassification.from_pretrained(self.args.model.model_name_or_path, self.args)
        return model.eval().to(device=self.device)


    def preprocess(self, audio_array):
        # audio has type of array
        audio_input = self.feature_extractor(
                audio_array, sampling_rate=self.feature_extractor.sampling_rate, return_tensors='pt'
            )['input_values'] 
        return audio_input.to(self.device)


    def __call__(self, audio):
        audio_array = np.frombuffer(audio, dtype='float32')
        audio_input = self.preprocess(audio_array)

        logits = self.model(audio_input).logits
        print(logits)
        emo_idx = torch.argmax(logits).cpu().detach().numpy()
        print("Emotion of speech: {}".format(self.classes[emo_idx]))
        return self.classes[emo_idx]



if __name__=='__main__':
    model = EmotionalSpeechRecognition()
    csv_path = '../ESD-W2V2/data/ESD/valid.csv'
    datas = []
    with open(csv_path, 'r') as cf:
        cf.readline()
        lines = cf.readlines()
        for line in lines:
            path, label = line.strip().split(',')
            path = path.replace('./','../ESD-W2V2/')
            datas.append((path, label))

    count = 0
    for data in datas:
        with open(data[0], 'rb') as f:
            byio = f.read()
        byio = BytesIO(byio)
        label = model(byio)

        if label == data[1]:
            count += 1
    
    print(count)