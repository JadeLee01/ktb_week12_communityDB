# ai.py

from typing import Dict

import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModelForSequenceClassification

MODEL_NAME = "unitary/toxic-bert"
TOXIC_THRESHOLD = 0.7

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)
model.eval()


def check_toxicity(text: str) -> Dict[str, float | str | bool]:

    text = (text or "").strip()
    if not text:
        return {"label": "non_toxic", "score": 0.0, "isToxic": False}

    enc = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=256,
    )

    with torch.no_grad():
        outputs = model(**enc)
        logits = outputs.logits
        probs = F.softmax(logits, dim=-1)[0]

    score, idx = torch.max(probs, dim=0)
    score = float(score.item())
    idx = int(idx.item())

    label = model.config.id2label.get(idx, str(idx))

    is_toxic = bool(score >= TOXIC_THRESHOLD and "tox" in label.lower())

    return {
        "label": label,
        "score": score,
        "isToxic": is_toxic,
    }
