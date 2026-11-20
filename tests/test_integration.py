import unittest

from streamlit.testing.v1 import AppTest

from src.model_loader import MODEL_PATH, load_model
from src.predictor import predict
from src.utils import EMOTIONS

EXAMPLES = [
    ("Hoy recibí una noticia maravillosa.", "Alegría"),
    ("No puedo dejar de pensar en cuánto te quiero.", "Amor"),
    ("Me molesta que nadie respete las reglas.", "Ira"),
    ("Tengo temor de perder mi trabajo.", "Miedo"),
    ("¡Qué sorpresa! No esperaba verte aquí.", "Sorpresa"),
    ("Me siento solo desde que te fuiste.", "Tristeza"),
]


class BetoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.resource = load_model(str(MODEL_PATH))

    def test_local_model_and_multiple_batches(self):
        self.assertEqual(self.resource.labels, tuple(EMOTIONS))
        self.assertEqual(self.resource.max_length, 64)
        examples = EXAMPLES * 6
        updates = []
        results = predict(
            self.resource, [text for text, _ in examples],
            lambda done, total: updates.append((done, total)),
        )
        self.assertEqual(updates[-1], (len(examples), len(examples)))
        self.assertGreater(len(updates), 1)
        for result, (text, expected) in zip(results, examples, strict=True):
            self.assertEqual(result["text"], text)
            self.assertEqual(result["emotion"], expected)
            scores = result["probabilities"]
            self.assertEqual(set(scores), set(EMOTIONS))
            self.assertAlmostEqual(sum(scores.values()), 1, places=6)
            self.assertEqual(result["confidence"], max(scores.values()))

    def test_invalid_inputs(self):
        for values in ([], [" "], [None], "hola"):
            with self.subTest(values=values), self.assertRaises(ValueError):
                predict(self.resource, values)

    def test_long_text_truncates_but_preserves_original(self):
        prefix = "Me siento muy feliz por mi familia. " * 90
        texts = [prefix + "alegría", prefix + "miedo"]
        first, second = predict(self.resource, texts)
        self.assertEqual([first["text"], second["text"]], texts)
        self.assertEqual(first["probabilities"], second["probabilities"])

    def test_streamlit_history_and_threshold(self):
        app = AppTest.from_file(MODEL_PATH.parent / "app.py", default_timeout=60).run()
        self.assertFalse(app.exception)
        self.assertIn("Los análisis de esta sesión aparecerán aquí.", [item.value for item in app.info])
        app.button(key="analyze_single").click().run()
        self.assertIn("Escribe una frase antes de analizar.", [item.value for item in app.warning])
        self.assertFalse(app.session_state.history)
        app.selectbox(key="example").select("Alegría").run()
        self.assertIn("aprobé mi examen", app.text_area(key="phrase").value)
        app.button(key="analyze_single").click().run()
        self.assertFalse(app.exception)
        self.assertEqual(len(app.session_state.history), 1)
        self.assertEqual(app.session_state.history[0]["emotion"], "Alegría")
        app.slider[0].set_value(100).run()
        self.assertIn("La confianza está por debajo del umbral de 100 %.", [item.value for item in app.warning])
        self.assertEqual(len(app.session_state.history), 1)
        next(button for button in app.button if button.label == "Limpiar historial").click().run()
        self.assertEqual(len(app.session_state.history), 1)
        next(button for button in app.button if button.label == "Sí, limpiar historial").click().run()
        self.assertFalse(app.session_state.history)
        self.assertFalse(app.exception)
