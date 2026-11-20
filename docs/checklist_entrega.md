# Lista de verificación de entrega

Los puntajes son los máximos de la rúbrica. La calificación corresponde al profesor.

| Criterio | Puntaje | Implementado | Probado | Pendiente | Evidencia |
|---|---:|---|---|---|---|
| Funcionalidad principal | 12,5 | Análisis de frases en español con emoción y confianza | BETO real, ejemplos rápidos, entrada vacía y advertencia por umbral | — | [Análisis individual](../capturas/02-analisis-individual.png), [integración](../tests/test_integration.py) |
| Visualización de probabilidades | 7,5 | Barras ordenadas de las seis clases | Seis valores, suma cercana al 100 % y orden descendente | — | [Probabilidades](../capturas/03-probabilidades.png), [pruebas](../tests/test_unit.py) |
| Uso correcto del modelo y Streamlit | 7,5 | Modelo local en caché, selección de dispositivo, lotes y truncamiento | CPU, arranque del servidor y sesión real en Chrome | GPU sin verificar en este entorno | [Integración](../tests/test_integration.py), [inicio](../capturas/01-pantalla-principal.png) |
| Dos funcionalidades adicionales | 7,5 | Lotes, importación y exportación CSV, historial y umbral | Chrome verificó lote de seis frases, selección de columna, omisión de una fila, ambas descargas, persistencia y limpieza con confirmación | — | [Varios textos](../capturas/04-varios-textos.png), [historial](../capturas/05-historial.png) |
| Repositorio y documentación | 7,5 | README, capturas, pruebas, declaración de IA y reglas de exclusión | Ensayo de inclusión en un índice temporal. Los pesos, el entorno y los archivos sensibles previstos quedan excluidos | Preparar el repositorio Git definitivo y publicar con autorización. Confirmar la preparación del corpus y los términos de la fuente original | [README](../README.md), [declaración de IA](../README.md#declaración-de-uso-de-inteligencia-artificial), [.gitignore](../.gitignore) |
| Video, defensa y análisis de errores | 7,5 | Guion de 2 min 50 s y registro de casos difíciles | Inferencias reales y comparación con las observaciones previas | Asignar participaciones, ensayar, grabar y compartir el video | [Guion](guion_defensa.md), [resultados](resultados_modelo.md) |
| **Total** | **50** | | | | |

## Antes de enviar al aula virtual

- Revisar las capturas y ensayar la defensa con la app abierta.
- Confirmar cómo podrá acceder el profesor al modelo. Los pesos se entregan por el canal que acuerde el equipo.
- Publicar el repositorio con autorización y verificar el acceso del profesor.
- Grabar el video, verificar sus permisos de acceso y entregar los enlaces del repositorio y del video en el aula virtual.
