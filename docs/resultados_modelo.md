# Inferencias reales con BETO

Verificación local en CPU, con 64 tokens como máximo y probabilidades obtenidas por softmax. Los porcentajes se redondean a dos decimales. Son ejemplos de funcionamiento y análisis de errores.

| Frase | Clase predicha | Confianza |
|---|---|---:|
| Hoy recibí una noticia maravillosa. | Alegría | 99,68 % |
| No puedo dejar de pensar en cuánto te quiero. | Amor | 99,60 % |
| Me molesta que nadie respete las reglas. | Ira | 99,17 % |
| Tengo temor de perder mi trabajo. | Miedo | 99,59 % |
| Jamás imaginé encontrarme contigo aquí. | Alegría | 43,95 % |
| Me siento solo desde que te fuiste. | Tristeza | 99,66 % |
| ¡Qué sorpresa! No esperaba verte aquí. | Sorpresa | 95,29 % |

«Jamás imaginé encontrarme contigo aquí» admite sorpresa y alegría según la situación. Con el umbral predeterminado del 70 %, la aplicación advierte sobre la baja confianza.

| Caso y frase | Observación anterior | Inferencia actual |
|---|---|---|
| Sarcasmo. «Qué maravilla, se dañó mi computadora justo cinco minutos antes de entregar el proyecto. ¡Excelente día!» | Alegría, 95,3 % | Alegría, 95,28 % |
| Negación. «No estoy triste ni tengo miedo, simplemente estoy agotado después de una semana de exámenes» | Tristeza, 87,3 % | Tristeza, 87,32 % |
| Contexto ambiguo. «Después de pasar toda la noche haciendo mi proyecto, el profesor nos dijo que había cancelado la entrega» | Ira, 95,6 % | Ira, 95,58 % |

Las tres predicciones coinciden con las observaciones anteriores al redondear a un decimal.

- En el caso de sarcasmo, la avería antes de la entrega sugiere frustración. Las expresiones positivas forman parte de la ironía y la clasificación como Alegría resulta poco plausible.
- En la negación, la frase descarta tristeza y miedo y expresa agotamiento, una categoría fuera de las seis disponibles. La clase elegida resulta cuestionable.
- En la cancelación, la ira es una lectura plausible. La frase también admite alivio, decepción o sorpresa según las circunstancias.

Una confianza alta puede coexistir con una interpretación equivocada. El corpus traducido también limita lo que puede concluirse sobre el desempeño en español ecuatoriano.
