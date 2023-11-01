from cogdl.oag import oagbert
from backend.utils.singleton import SingletonMeta
import torch

class OAGBertModel(metaclass=SingletonMeta):
    _model = None
    _device = None

    def __init__(self):
        _, self._model = oagbert("oagbert-v2")
        self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._model.to(self._device)

    def get_model(self):
        return self._device, self._model