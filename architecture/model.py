import torch
import torch.nn as nn

from torch.nn import CrossEntropyLoss
from transformers.models.wav2vec2.modeling_wav2vec2 import (
    Wav2Vec2PreTrainedModel,
    Wav2Vec2Model
)

from architecture.modeling_output import (
    SpeechClassifierOutput,
    SiameseNetworkOutput,
    HeadClassifierOutput
)


class Wav2Vec2ClassificationHead(nn.Module):
    """Head for wav2vec2 classification task."""

    def __init__(self, args):
        super().__init__()
        self.a_fc1 = nn.Linear(args.classifier.hidden_size, 1)
        self.a_fc2 = nn.Linear(1, 1)
        self.sigmoid = nn.Sigmoid()
        self.relu = nn.ReLU()
        self.softmax = nn.Softmax(dim=1)
        self.dropout = nn.Dropout(args.classifier.final_dropout)
        self.hidden_proj = nn.Linear(args.classifier.hidden_size, args.classifier.proj_size)
        self.out_proj = nn.Linear(args.classifier.proj_size, args.classifier.num_labels)
    

    def forward(self, features):
        # features -> (B, T, 768)
        v = self.sigmoid(self.a_fc1(features))
        alphas = self.softmax(self.a_fc2(v).squeeze(dim=-1))
        res_att = (alphas.unsqueeze(2) * features).sum(dim=1)

        x = res_att
        x = self.dropout(self.relu(self.hidden_proj(x)))
        x = self.out_proj(x)

        return HeadClassifierOutput(
            logits=x,
            attention=res_att,
        )


class SiameseNetworkForSpeechClassification(Wav2Vec2PreTrainedModel):
    def __init__(self, config, args):
        super(SiameseNetworkForSpeechClassification, self).__init__(config)
        self.num_labels = args.classifier.num_labels
        self.config = config
        self.wav2vec2 = Wav2Vec2Model(config)
        self.classifier = Wav2Vec2ClassificationHead(args)


    def forward(
        self,
        input_values,
        attention_mask=None,
        output_attentions=None,
        output_hidden_states=None,
        return_dict=None,
        labels=None,
    ):
        outputs = self.wav2vec2(
                input_values,
                attention_mask=attention_mask,
                output_attentions=output_attentions,
                output_hidden_states=output_hidden_states,
                return_dict=return_dict,
            )

        hidden_states = outputs.last_hidden_state
        
        head_output = self.classifier(hidden_states)
        logits = head_output.logits
        
        return SpeechClassifierOutput(logits=logits)