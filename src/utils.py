import csv
import io

import pandas as pd

EMOTIONS = {
    "Tristeza": ("😢", "#82aeff"),
    "Alegría": ("😊", "#ffd166"),
    "Amor": ("❤️", "#ff91bf"),
    "Ira": ("😡", "#ff836f"),
    "Miedo": ("😨", "#be9bff"),
    "Sorpresa": ("😲", "#67e0be"),
}


def percentage(value):
    return f"{value:.1%}".replace(".", ",")


def read_csv(content):
    if not content.strip():
        raise ValueError("El archivo CSV está vacío.")
    try:
        decoded = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ValueError("Guarda el CSV con codificación UTF-8 y vuelve a subirlo.") from exc
    if not decoded.strip():
        raise ValueError("El archivo CSV está vacío.")
    if "\x00" in decoded:
        raise ValueError("El archivo contiene caracteres inválidos para un CSV.")

    try:
        header_line = next(line for line in decoded.splitlines() if line.strip())
        try:
            delimiter = csv.Sniffer().sniff(header_line, delimiters=",;\t").delimiter
        except csv.Error:
            delimiter = ","
        reader = csv.reader(io.StringIO(decoded, newline=""), delimiter=delimiter, strict=True)
        header = [name.strip() for name in next(row for row in reader if row)]
        if not all(header) or len(set(header)) != len(header):
            raise ValueError("La primera fila debe tener nombres de columnas únicos y no vacíos.")
        rows = []
        for row in reader:
            if not row or (len(row) == 1 and not row[0].strip()):
                rows.append([""] * len(header))
            elif len(row) != len(header):
                raise ValueError(f"La fila que termina en la línea {reader.line_num} tiene un número incorrecto de columnas.")
            else:
                rows.append(row)
    except (csv.Error, StopIteration) as exc:
        raise ValueError("El archivo CSV tiene un formato inválido. Revisa los separadores y las comillas.") from exc
    if not rows:
        raise ValueError("El CSV tiene encabezados, pero no contiene filas de datos.")
    return pd.DataFrame(rows, columns=header)


def clean_texts(values):
    texts = [value.strip() if isinstance(value, str) else "" for value in values]
    valid = [value for value in texts if value]
    return valid, len(texts) - len(valid)


def results_table(results):
    return pd.DataFrame([
        {
            "Texto": result["text"],
            "Emoción": result["emotion"],
            "Confianza (%)": result["confidence"] * 100,
            **{f"{emotion} (%)": result["probabilities"][emotion] * 100 for emotion in EMOTIONS},
        }
        for result in results
    ])


def csv_bytes(table):
    export = table.copy()
    # Evita que una frase se ejecute como fórmula al abrir el CSV en una hoja de cálculo.
    export["Texto"] = export["Texto"].map(
        lambda value: "'" + value if value.lstrip().startswith(("=", "+", "-", "@")) else value
    )
    return export.to_csv(index=False).encode("utf-8-sig")
