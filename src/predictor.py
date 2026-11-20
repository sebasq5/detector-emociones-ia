import math


def predict(resource, texts, progress=None):
    import torch

    if isinstance(texts, str) or not len(texts) or any(
        not isinstance(text, str) or not text.strip() for text in texts
    ):
        raise ValueError("Proporciona una secuencia de frases con contenido.")

    results = []
    batch_size = 32 if resource.device == "cuda" else 16
    with torch.inference_mode():
        for start in range(0, len(texts), batch_size):
            batch = texts[start:start + batch_size]
            # El tokenizador rápido configura padding y truncamiento en cada llamada.
            with resource.tokenizer_lock:
                inputs = resource.tokenizer(
                    batch, padding=True, truncation=True,
                    max_length=resource.max_length, return_tensors="pt",
                )
            inputs = inputs.to(resource.device)
            logits = resource.model(**inputs).logits
            if tuple(logits.shape) != (len(batch), len(resource.labels)):
                raise ValueError("El modelo devolvió una cantidad inesperada de predicciones.")
            scores = torch.softmax(logits.float(), dim=-1).cpu().tolist()
            for phrase, values in zip(batch, scores, strict=True):
                if not all(math.isfinite(value) for value in values):
                    raise ValueError("El modelo devolvió probabilidades no válidas.")
                probabilities = dict(zip(resource.labels, values, strict=True))
                winner = max(probabilities, key=probabilities.__getitem__)
                results.append({
                    "text": phrase, "emotion": winner,
                    "confidence": probabilities[winner], "probabilities": probabilities,
                })
            if progress:
                progress(len(results), len(texts))
    return results
