from cogdl.oag import oagbert
from backend.utils.singleton import SingletonMeta
from backend.utils.logger import AppLogger
import torch

logger = AppLogger().get_logger()

class OAGBertModel(metaclass=SingletonMeta):
    _model = None
    _device = None

    def __init__(self):
        _, self._model = oagbert("oagbert-v2-sim")
        self._device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self._model.to(self._device)
        logger.info(f"OAG-Bert model initialized on device: {self._device}")

    def get_model(self):
        return self._device, self._model