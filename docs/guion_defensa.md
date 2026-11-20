# Guion de defensa · 2 min 50 s

Asignen cada bloque antes de grabar y dejen la app abierta con BETO cargado. Preparen el lote de seis frases y un CSV con una fila vacía para la demostración.

### 0:00–0:20 · Presentación · [Participación por asignar]

Hola. Nuestro proyecto es Detector de Emociones IA. Le damos una frase en español y el sistema estima si expresa tristeza, alegría, amor, ira, miedo o sorpresa. Queríamos mostrar cómo funciona un clasificador de texto y qué pasa cuando una frase se presta a varias interpretaciones.

### 0:20–0:45 · Modelo y entrenamiento · [Participación por asignar]

Usamos BETO, un modelo de lenguaje en español que el equipo ajustó en Google Colab. Trabajamos con doce mil frases de un corpus traducido. Reservamos mil ochocientas para la prueba final. Al abrir la app, Streamlit carga el modelo local y lo mantiene en caché para usarlo en los siguientes análisis.

### 0:45–1:30 · Demostración · [Participación por asignar]

[Abrir «Una frase» y analizar un ejemplo.] Voy a escribir «Hoy recibí una noticia maravillosa». El modelo elige alegría y le asigna cerca del 99,7 %. En el gráfico podemos ver las seis probabilidades, de mayor a menor. Si subimos el umbral a 100 %, aparece una advertencia. La emoción y los porcentajes siguen siendo los mismos. Ese control sirve para saber cuándo vale la pena revisar una predicción.

### 1:30–1:55 · Funciones adicionales · [Participación por asignar]

[Mostrar el lote y pasar al historial.] También podemos analizar varias frases juntas o subir un CSV y escoger su columna de texto. La tabla muestra cada predicción y el gráfico resume qué emociones aparecieron. Los resultados quedan en el historial de la sesión y se pueden descargar en CSV.

### 1:55–2:25 · Análisis de errores · [Participación por asignar]

En el ejemplo sarcástico se daña una computadora antes de la entrega. El modelo predijo alegría con 95,28 %, aunque el contexto sugiere frustración. En «No estoy triste ni tengo miedo», eligió tristeza con 87,32 %, pese a que la frase la descarta y habla de agotamiento. También probamos la cancelación de una entrega. El modelo eligió ira, una lectura posible entre varias.

### 2:25–2:50 · Resultados y cierre · [Participación por asignar]

En la prueba del entrenamiento obtuvimos 92,33 % de exactitud y 90,23 % de F1 macro. Esas cifras corresponden al corpus traducido. Los ejemplos de la demo muestran por qué conviene leer la frase completa, incluso cuando el modelo da una confianza alta. El README incluye las pruebas, las limitaciones y la declaración del apoyo de ChatGPT y Codex. Gracias.
