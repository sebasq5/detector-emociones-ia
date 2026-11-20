from datetime import datetime
import logging
import time

import streamlit as st

from src.charts import distribution_chart, probability_chart
from src.model_loader import MODEL_PATH, ModelError, load_model
from src.predictor import predict
from src.utils import EMOTIONS, clean_texts, csv_bytes, percentage, read_csv, results_table

LOGGER = logging.getLogger(__name__)
EXAMPLES = {
    "Alegría": "Hoy estoy muy feliz porque aprobé mi examen.",
    "Tristeza": "Me siento triste porque extraño a mi familia.",
    "Amor": "Te quiero muchísimo.",
    "Ira": "Estoy furioso por lo que ocurrió.",
    "Miedo": "Tengo miedo de que algo malo suceda.",
    "Sorpresa": "No puedo creer la sorpresa que me dieron.",
}

STYLE = """
<style>
.block-container {max-width: 76rem; padding-top: 3.8rem;}
.detector-header {
  background: #162540; border: 1px solid #344b72; border-radius: 18px;
  padding: clamp(1.25rem, 4vw, 2.75rem); margin-bottom: .75rem;
}
.detector-header h1 {
  font-size: clamp(2rem, 5vw, 3.5rem); line-height: 1.06;
  letter-spacing: -.055em; margin: 0 0 .65rem; padding: 0; color: #f0f4ff;
}
.detector-header p {color: #c8d6ed; margin: 0; max-width: 52ch;}
.emotion-spectrum {display:flex; gap: 5px; width: min(100%, 16rem); margin-bottom: 1rem;}
.emotion-spectrum span {height: 5px; flex: 1; border-radius: 8px;}
.emotion-result {
  border-left: 5px solid var(--emotion); background: #1a2842;
  padding: 1.15rem 1.4rem; border-radius: 0 14px 14px 0;
}
.emotion-result strong {display: block; color: var(--emotion); font-size: 1.9rem;}
.emotion-result p {margin: .35rem 0 0;}
</style>
"""


def reset_phrase():
    st.session_state.phrase = ""
    st.session_state.example = None
    st.session_state.pop("single_result", None)


def apply_example():
    example = st.session_state.example
    if example:
        st.session_state.phrase = EXAMPLES[example]
        st.session_state.pop("single_result", None)


def analyze(resource, texts, source):
    if resource is None:
        st.error("Completa los archivos del modelo local para analizar textos.")
        return None
    progress_bar = st.progress(0, text="Preparando el análisis…") if len(texts) > 1 else None

    def update(done, total):
        progress_bar.progress(done / total, text=f"Textos procesados {done} de {total}")

    started = time.perf_counter()
    try:
        with st.spinner("Analizando con el modelo del equipo…"):
            results = predict(resource, texts, update if progress_bar is not None else None)
    except Exception:
        LOGGER.exception("Error durante la inferencia del modelo local")
        st.error("El modelo no pudo completar el análisis. Intenta con menos textos o revisa los archivos del modelo.")
        return None
    finally:
        if progress_bar is not None:
            progress_bar.empty()

    timestamp = datetime.now().astimezone().isoformat(timespec="seconds")
    st.session_state.history.extend(
        {**result, "source": source, "timestamp": timestamp} for result in results
    )
    return results, time.perf_counter() - started


def table_config():
    return {
        f"{label} (%)": st.column_config.NumberColumn(format="%.2f")
        for label in ("Confianza", *EMOTIONS)
    }


def show_distribution(results):
    st.plotly_chart(distribution_chart(results), config={"displaylogo": False})


def single_tab(resource, threshold):
    st.subheader("Analiza una frase")
    with st.container(border=True):
        st.selectbox(
            "Ejemplos rápidos", list(EXAMPLES), index=None,
            format_func=lambda emotion: f"{EMOTIONS[emotion][0]} {EXAMPLES[emotion]}",
            placeholder="Elige un ejemplo", key="example", on_change=apply_example,
        )
        phrase = st.text_area(
            "Frase en español", key="phrase", height=130,
            placeholder="Por ejemplo, «Me hizo muy feliz volver a verte».",
            help="El modelo analiza hasta su límite de tokens. El resto del texto se conserva en el historial.",
        )
        if st.button("Analizar emoción", type="primary", key="analyze_single"):
            st.session_state.pop("single_result", None)
            texts, _ = clean_texts([phrase])
            if not texts:
                st.warning("Escribe una frase antes de analizar.")
            else:
                analysis = analyze(resource, texts, "Una frase")
                if analysis:
                    st.session_state.single_result = (analysis[0][0], analysis[1])

    if "single_result" not in st.session_state:
        return
    result, elapsed = st.session_state.single_result
    emotion = result["emotion"]
    emoji, color = EMOTIONS[emotion]
    confidence = result["confidence"]
    st.html(f"""
        <div class="emotion-result" style="--emotion:{color}">
            <div>Emoción detectada</div>
            <strong>{emoji} {emotion}</strong>
            <p>Confianza del modelo <b>{percentage(confidence)}</b></p>
        </div>
    """)
    st.text(result["text"])
    st.caption(f"Tiempo de procesamiento · {elapsed:.2f} s")
    if confidence * 100 < threshold:
        st.warning(f"La confianza está por debajo del umbral de {threshold} %.")
    st.subheader("Probabilidad por emoción")
    st.plotly_chart(probability_chart(result), config={"displaylogo": False})
    st.button("Analizar otra frase", on_click=reset_phrase)


def batch_tab(resource, threshold):
    st.subheader("Analiza varios textos")
    method = st.radio("Método de entrada", ["Una frase por línea", "Archivo CSV"], horizontal=True)
    with st.container(border=True):
        if method == "Una frase por línea":
            raw = st.text_area("Textos en español", height=180, placeholder="Escribe una frase por línea.")
            values = raw.splitlines()
            ready = True
        else:
            values = []
            ready = False
            uploaded = st.file_uploader("Archivo CSV", type=["csv"], help="Usa UTF-8 y nombres de columna en la primera fila.")
            if uploaded is not None:
                try:
                    data = read_csv(uploaded.getvalue())
                except ValueError as exc:
                    st.error(str(exc))
                else:
                    st.dataframe(data.head(10), hide_index=True)
                    column = st.selectbox("Columna de textos", list(data.columns), index=None)
                    if column in data.columns:
                        values = data[column]
                        ready = True
                    elif column is not None:
                        st.error("Selecciona una columna que exista en el CSV.")
        if st.button("Analizar todos", type="primary", disabled=not ready):
            st.session_state.pop("batch_result", None)
            texts, skipped = clean_texts(values)
            if not texts:
                st.warning("Añade al menos una frase con contenido.")
            else:
                source = "CSV" if method == "Archivo CSV" else "Varios textos"
                analysis = analyze(resource, texts, source)
                if analysis:
                    st.session_state.batch_result = (*analysis, skipped, source)

    if "batch_result" not in st.session_state:
        return
    results, elapsed, skipped, source = st.session_state.batch_result
    st.subheader("Resultados del último lote")
    st.caption(f"{source} · {len(results)} textos procesados · {elapsed:.2f} s")
    if skipped:
        st.info(f"Entradas vacías omitidas: {skipped}.")
    low = sum(result["confidence"] * 100 < threshold for result in results)
    if low:
        st.warning(f"{low} de {len(results)} textos tienen confianza inferior al {threshold} %.")
    table = results_table(results)
    st.dataframe(table, hide_index=True, column_config=table_config())
    st.download_button("Descargar resultados en CSV", csv_bytes(table), "resultados_emociones.csv",
                       "text/csv", on_click="ignore")
    st.subheader("Distribución de emociones")
    show_distribution(results)


def finish_clear_history(confirm):
    if confirm:
        st.session_state.history.clear()
    st.session_state.confirm_clear_history = False


def history_tab(threshold):
    st.subheader("Historial de la sesión")
    history = st.session_state.history
    if not history:
        st.info("Los análisis de esta sesión aparecerán aquí.")
        return
    results = history[::-1]
    table = results_table(results)
    table.insert(0, "Fecha y hora", [result["timestamp"] for result in results])
    table.insert(1, "Origen", [result["source"] for result in results])
    st.metric("Textos analizados", len(results))
    low = sum(result["confidence"] * 100 < threshold for result in results)
    if low:
        st.caption(f"Textos por debajo del umbral actual de {threshold} %: {low}.")
    st.dataframe(table, hide_index=True, column_config=table_config())
    st.download_button("Descargar historial en CSV", csv_bytes(table), "historial_emociones.csv",
                       "text/csv", on_click="ignore")
    if st.button("Limpiar historial"):
        st.session_state.confirm_clear_history = True
    if st.session_state.get("confirm_clear_history", False):
        with st.container(border=True):
            st.warning("Se eliminarán todos los análisis guardados en esta sesión.")
            cancel, confirm = st.columns(2)
            cancel.button("Cancelar", on_click=finish_clear_history, args=(False,))
            confirm.button("Sí, limpiar historial", type="primary",
                           on_click=finish_clear_history, args=(True,))
    st.subheader("Distribución en la sesión")
    show_distribution(results)


def main():
    st.set_page_config(page_title="Detector de Emociones IA", page_icon="💬", layout="wide")
    st.session_state.setdefault("history", [])
    spectrum = "".join(f'<span style="background:{color}"></span>' for _, color in EMOTIONS.values())
    st.html(STYLE + f"""
        <header class="detector-header">
            <div class="emotion-spectrum" aria-hidden="true">{spectrum}</div>
            <h1>Detector de Emociones IA</h1>
            <p>Analiza frases en español y consulta la probabilidad que el modelo asigna a cada emoción.</p>
        </header>
    """)
    with st.sidebar:
        st.header("Modelo")
        resource = None
        try:
            with st.spinner("Comprobando el modelo local…", show_time=False):
                resource = load_model(str(MODEL_PATH))
        except ModelError as exc:
            model_issue = str(exc)
        except ImportError:
            model_issue = "Instala las dependencias de requirements.txt para cargar el modelo."
        except Exception:
            LOGGER.exception("Error al cargar el modelo local")
            model_issue = "Ocurrió un error al cargar el modelo local. Revisa los archivos y las dependencias."
        st.write(f"**Modelo** · {resource.name if resource else MODEL_PATH.name}")
        st.write("**Idioma** · Español")
        st.write("**Emociones** · 6")
        device = {"cuda": "GPU", "cpu": "CPU"}[resource.device] if resource else "Pendiente de carga"
        st.write(f"**Dispositivo** · {device}")
        st.divider()
        st.header("Configuración")
        threshold = st.slider("Umbral de confianza (%)", 0, 100, 70)
        st.caption("El umbral controla cuándo aparecen las advertencias. Las probabilidades del modelo se conservan.")
        st.divider()
        st.header("Proyecto")
        st.caption("Aplicación académica de clasificación de emociones con el modelo entrenado por el equipo.")
        st.caption("Python · Streamlit · PyTorch · Transformers")
    if resource is None:
        st.warning(model_issue + " La carpeta debe incluir config.json, los pesos y los archivos del tokenizador.")
    single, batch, history = st.tabs(["Una frase", "Varios textos", "Historial"])
    with single:
        single_tab(resource, threshold)
    with batch:
        batch_tab(resource, threshold)
    with history:
        history_tab(threshold)


if __name__ == "__main__":
    main()
