# Detector de Emociones IA

Aplicación académica que clasifica textos en español con un modelo BETO ajustado por el equipo. El objetivo es integrar un clasificador supervisado en una interfaz interactiva y examinar su comportamiento con frases claras, ambiguas y difíciles.

## Arquitectura y tecnologías

| Componente | Responsabilidad |
|---|---|
| `app.py` · Streamlit | Entrada individual, lotes, CSV, umbral e historial por sesión |
| `src/model_loader.py` · Transformers y PyTorch | Carga local, validación de etiquetas y caché del modelo. Usa CUDA cuando está disponible y CPU en los demás casos |
| `src/predictor.py` · PyTorch | Tokenización con truncamiento, inferencia por lotes y softmax de seis clases |
| `src/utils.py` y `src/charts.py` · pandas y Plotly | Preparación de CSV, tablas y gráficos |

El modelo parte de `dccuchile/bert-base-spanish-wwm-cased` y asigna una sola clase entre **tristeza, alegría, amor, ira, miedo y sorpresa**. El texto se procesa localmente. La interfaz conserva la frase completa aunque la inferencia use como máximo 64 tokens, según los metadatos de entrenamiento.

## Dataset y resultados

Según `modelo_emociones_es/metadata_entrenamiento.json`, el equipo ajustó BETO en Google Colab con la porción `emotion` en español de `ma2za/many_emotions`. Esa porción contiene texto traducido del inglés. Los metadatos registran la semilla 123 y 12.000 frases repartidas en 8.400 de entrenamiento, 1.800 de validación y 1.800 de prueba. Los pasos de preparación adicionales y los términos de la fuente original están pendientes de confirmación.

| Métrica en las 1.800 frases de prueba | Valor registrado |
|---|---:|
| Exactitud | 92,33 % |
| Precisión macro | 89,78 % |
| Sensibilidad macro | 90,72 % |
| F1 macro | 90,23 % |

Las cifras proceden de los metadatos locales del entrenamiento. La verificación de esta entrega ejecuta inferencias sobre ejemplos concretos.

## Instalación y ejecución

Se verificó el entorno con Python 3.13, Streamlit 1.67.0, PyTorch 2.15.0 y Transformers 4.57.6. Reserva alrededor de 420 MiB para los pesos, además del espacio de las dependencias.

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Coloca la exportación del equipo junto a `app.py`, con esta estructura:

```text
modelo_emociones_es/
├── config.json
├── model.safetensors
├── tokenizer.json
├── tokenizer_config.json
└── metadata_entrenamiento.json
```

La carpeta se excluye de Git. Obtén la exportación del equipo por el canal acordado para la entrega. Incluye los metadatos para conservar el límite de inferencia del proyecto.

```bash
python -m streamlit run app.py
```

## Uso

- **Una frase.** Escribe «Hoy recibí una noticia maravillosa.» o selecciona un ejemplo rápido. Pulsa **Analizar emoción** para ver la clase, la confianza y las seis probabilidades ordenadas.
- **Varios textos.** Introduce una frase por línea o sube un CSV UTF-8 de hasta 10 MB con encabezado. Se aceptan coma, punto y coma o tabulador. Selecciona la columna de texto y pulsa **Analizar todos**. La app omite entradas vacías, muestra la distribución de clases y permite descargar los resultados.
- **Historial.** Consulta los análisis de la sesión, descarga el CSV o vacía el historial con confirmación.
- **Umbral.** Ajusta el nivel que activa las advertencias de confianza. La app conserva la clasificación y las probabilidades originales.

## Pruebas

```bash
python -m pip install pytest
python -m compileall -q app.py src
python -m pytest -q
```

Las pruebas unitarias cubren CSV y gráficos. Las pruebas de integración requieren la exportación local de BETO y comprueban las seis clases, las probabilidades, el procesamiento por lotes, el truncamiento y el flujo de sesión en Streamlit. La ejecución local pasó 8 pruebas y 13 subpruebas.

## Limitaciones

El clasificador siempre elige entre seis clases, incluso ante textos neutros o emociones fuera del conjunto. La confianza es la probabilidad asignada por el modelo y puede ser alta en predicciones discutibles. La verificación observó dificultades con sarcasmo, negaciones y frases cuyo sentido depende del contexto. Las métricas del corpus traducido tienen un alcance limitado para español ecuatoriano. Los textos largos se truncan para la inferencia. [Resultados y casos difíciles](docs/resultados_modelo.md)

## Declaración de uso de inteligencia artificial

El equipo ajustó BETO en Google Colab para clasificar emociones. La aplicación usa esa exportación local para realizar sus predicciones. ChatGPT y Codex se utilizaron como herramientas de apoyo durante la revisión del código, los ajustes de programación, la escritura y ejecución de pruebas y la preparación de la documentación de entrega. Durante esta revisión se conservaron los pesos entrenados por el equipo.

## Capturas de la aplicación

Capturas tomadas en Chrome con la app local y el modelo BETO cargado.

| Vista | Captura |
|---|---|
| Pantalla principal | [Inicio](capturas/01-pantalla-principal.png) |
| Análisis individual | [Resultado](capturas/02-analisis-individual.png) |
| Probabilidades | [Gráfico de seis clases](capturas/03-probabilidades.png) |
| Varios textos | [Tabla y distribución](capturas/04-varios-textos.png) |
| Historial | [Registros de la sesión](capturas/05-historial.png) |

[Guion de defensa](docs/guion_defensa.md) · [Lista de entrega](docs/checklist_entrega.md)
