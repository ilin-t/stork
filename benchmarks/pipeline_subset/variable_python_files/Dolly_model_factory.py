from typing import Union
from torch import nn
from models.bag_of_words import BagOfWords
from models.resnet import resnet18
from models.inception import inception3
from models.vision_transformer import VisionTransformer, vision_transformer
from dotenv import load_dotenv
from utils.model_utils import split_model_file_name, get_model_info, AVAILABLE_MODELS
from utils.time_utils import datetime_to_str, str_to_datetime
import os
from datetime import datetime
import torch
import pandas as pd
from typing import Union

load_dotenv()

DATA_FOLDER = os.getenv("DATA_FOLDER_PATH")
MODEL_FOLDER = os.path.join(DATA_FOLDER, "models")
MODEL_DF = pd.read_csv(os.path.join(DATA_FOLDER, "models.csv"))

def get_model_class(name: str, num_of_classes: int, **kwargs) -> Union[nn.Module, BagOfWords]:

  if name not in AVAILABLE_MODELS:
    raise ValueError(f"Model type not supported, available models: {AVAILABLE_MODELS}")

  # Names are defined in the class constructor function in the model declarations
  if name == 'resnet18':
    return resnet18(num_classes=num_of_classes)
  elif name == 'vision_transformer':
    return vision_transformer(num_classes=num_of_classes, **kwargs)
  elif name == 'inception_v3':
    return inception3(num_classes=num_of_classes)
  elif name == 'bag_of_words':
    return BagOfWords(DATA_FOLDER, num_classes=num_of_classes)


def get_trained_model_by_id(id: str) -> nn.Module:
  models = os.listdir(MODEL_FOLDER)

  # Filter models that don't contain the id
  filtered_models = [model for model in models if id in model]

  if len(filtered_models) == 0:
    raise ValueError(f"Could not find model with id {id}")
  elif len(filtered_models) > 1:
    raise ValueError(f"Found multiple models with id {id}")

  model_file_name = filtered_models[0]
  id, model_name, timestamp = split_model_file_name(model_file_name)
  model_weight_path = os.path.join(MODEL_FOLDER, model_file_name)

  model_info = get_model_info(id)
  num_classes = model_info['num_classes'].item()

  model_class = get_model_class(model_name, num_of_classes=num_classes)
  model_class.load_state_dict(torch.load(model_weight_path))
  model_class.eval()

  return model_class


def get_trained_model(name: str, latest: bool = True, timestamp: str = None) -> nn.Module:

  if name not in AVAILABLE_MODELS:
    raise ValueError(f"Model type not supported, available models: {AVAILABLE_MODELS}")

  if not latest and not timestamp:
    raise ValueError("Either latest flag or timestamp must be passed as an argument")

  models = os.listdir(MODEL_FOLDER)

  # Filter models that don't contain the name
  filtered_models = [model for model in models if name in models]

  if len(filtered_models) == 0:
    raise ValueError(f"Could not find a model with name {name}")

  if latest:
    # datetime.min is always smaller than any other datetime
    model_id = None
    latest_model, latest_timestamp = None, datetime.min
    for model in filtered_models:
      id, model_name, timestamp = split_model_file_name(model)

      if timestamp > latest_timestamp:
        model_id = id
        latest_model = model
        latest_timestamp = timestamp

    model_weight_path = os.path.join(MODEL_FOLDER, latest_model)

  else:

    model_id = None
    timestamp_model = None

    for model in filtered_models:
      id, model_name, timestamp_str = split_model_file_name(model, return_as_str=True)
      if timestamp == timestamp_str:
        model_id = id
        timestamp_model = model


    if not timestamp_model:
      raise ValueError(f"Could not find a model with name {name} and timestamp {timestamp}")

    model_weight_path = os.path.join(MODEL_FOLDER, timestamp_model)

  model_info = get_model_info(model_id)
  num_classes = model_info['num_classes'].item()

  model_class = get_model_class(name, num_of_classes=num_classes)
  model_class.load_state_dict(torch.load(model_weight_path))
  model_class.eval()

  return model_class
