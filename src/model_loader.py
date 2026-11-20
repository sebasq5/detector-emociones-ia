from dataclasses import dataclass, field
import json
from pathlib import Path
from threading import Lock
import unicodedata
from typing import Any

import streamlit as st

from src.utils import EMOTIONS

MODEL_PATH = Path(__file__).resolve().parents[1] / "modelo_emociones_es"
ALIASES = {
    "sadness": "Tristeza", "joy": "Alegría", "love": "Amor",
    "anger": "Ira", "fear": "Miedo", "surprise": "Sorpresa",
}


class ModelError(RuntimeError):
    pass


@dataclass(frozen=True)
class EmotionModel:
    model: Any
    tokenizer: Any
    device: str
    labels: tuple[str, ...]
    max_length: int
    name: str
    tokenizer_lock: Any = field(default_factory=Lock, repr=False)


def normalize(label):
    return "".join(
        char for char in unicodedata.normalize("NFD", label.strip().casefold())
        if not unicodedata.combining(char)
    )


def ordered_labels(config):
    try:
        aliases = ALIASES | {normalize(label): label for label in EMOTIONS}
        labels = []
        inverse = {int(index): aliases[normalize(label)] for label, index in
                   (config.label2id or {}).items() if normalize(label) in aliases}
        for index in range(len(EMOTIONS)):
            raw_label = config.id2label[index]
            emotion = aliases.get(normalize(raw_label))
            if emotion is None and normalize(raw_label) == f"label_{index}":
                emotion = inverse.get(index)
            if emotion is None or inverse.get(index, emotion) != emotion:
                raise ValueError
            if raw_label in (config.label2id or {}) and int(config.label2id[raw_label]) != index:
                raise ValueError
            labels.append(emotion)
        if config.num_labels != len(EMOTIONS) or set(labels) != set(EMOTIONS):
            raise ValueError
        return tuple(labels)
    except (AttributeError, KeyError, TypeError, ValueError) as exc:
        raise ModelError(
            "El modelo debe declarar las seis emociones y sus índices correctos en id2label "
            "o label2id de config.json. Comprueba el orden usado durante el entrenamiento."
        ) from exc


@st.cache_resource(show_spinner=False)
def load_model(path):
    directory = Path(path)
    if not directory.is_dir():
        raise ModelError("Coloca la carpeta modelo_emociones_es/ junto a app.py.")
    if not (directory / "config.json").is_file() or not any(
        (directory / name).is_file()
        for name in ("model.safetensors", "pytorch_model.bin",
                     "model.safetensors.index.json", "pytorch_model.bin.index.json")
    ):
        raise ModelError("Copia config.json y todos los archivos de pesos exportados en modelo_emociones_es/.")

    import torch
    from transformers import AutoConfig, AutoModelForSequenceClassification, AutoTokenizer

    try:
        config = AutoConfig.from_pretrained(directory, local_files_only=True)
    except Exception as exc:
        raise ModelError("No se pudo leer config.json del modelo local. Revisa la exportación.") from exc
    labels = ordered_labels(config)
    if config.problem_type == "multi_label_classification":
        raise ModelError("Se requiere el modelo de clasificación de una sola emoción por frase.")
    try:
        tokenizer = AutoTokenizer.from_pretrained(directory, local_files_only=True)
        if tokenizer.pad_token_id is None:
            raise ValueError("El tokenizador no define padding.")
    except Exception as exc:
        raise ModelError("No se pudo cargar el tokenizador. Copia todos sus archivos exportados en la carpeta del modelo.") from exc
    device = "cuda" if torch.cuda.is_available() else "cpu"
    try:
        model, loading = AutoModelForSequenceClassification.from_pretrained(
            directory, config=config, local_files_only=True, output_loading_info=True
        )
        if any(loading.get(key) for key in ("missing_keys", "mismatched_keys", "error_msgs")):
            raise ValueError("Los pesos no cubren todos los parámetros del modelo.")
        model.to(device)
        model.eval()
    except Exception as exc:
        raise ModelError("No se pudieron cargar los pesos. Revisa que la exportación esté completa y sea compatible con PyTorch.") from exc
    limits = [512, tokenizer.model_max_length, getattr(config, "max_position_embeddings", None)]
    metadata_path = directory / "metadata_entrenamiento.json"
    if metadata_path.is_file():
        try:
            training_limit = json.loads(metadata_path.read_text(encoding="utf-8"))["max_length"]
            if type(training_limit) is not int or training_limit < 3:
                raise ValueError("max_length debe ser un entero mayor o igual a 3.")
        except (OSError, KeyError, TypeError, ValueError) as exc:
            raise ModelError("Revisa max_length en metadata_entrenamiento.json.") from exc
        limits.append(training_limit)
    max_length = min(limit for limit in limits if isinstance(limit, int) and limit > 0)
    return EmotionModel(model, tokenizer, device, labels, max_length, directory.name)
