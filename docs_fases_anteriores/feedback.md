Bloqueantes (antes de entregar)

1. Criterio 8: el k=2 con pgr_dijkstra nunca se ha ejecutado.

ruta_dijkstra.geojson es de las 22:36 de ayer y no contiene ningún campo k=2. Hay que correr python3 main.py en Docker y confirmar que funciona.
La ruta k=2 queda guardada dentro de properties.linea_k2. Así ni Leaflet ni QGIS la dibujan. Debe ser un Feature aparte con "k": 2.
La diapositiva 10 usa IDs de aristas inventados ("42, 45, 68, 89…"). Hay que poner la salida real.
El factor de penalización es ×10 en SQL y ×4 en Python, JavaScript y la diapositiva 9. Por eso el "Dijkstra k=2" que compara el sitio no es el mismo que calcula pgRouting. Hay que dejar un solo factor.
Conviene agregar una frase que diga que el costo sigue siendo solo distancia y que la penalización existe únicamente para forzar una alternativa distinta. Así se anticipa la objeción "basándose únicamente en la distancia". 2. Bug: la opción "k = 2" del sitio no dibuja nada nuevo.
El HTML usa value="2", pero app.js:484 compara contra 'k2'. Solo funciona "Mostrar ambas". Si el profesor elige k=2 para revisar los criterios 8 y 9, no ve la ruta. Se arregla cambiando 'k2' por '2' en las líneas 484 y 498.

3. La diapositiva 14 no dice que sus números son con el incendio simulado.
   Con los valores por defecto del sitio (sin incendio simulado), el profesor verá ΔR entre −0,2 y +1,4 p.p., no +87 a +95. Lo comprobé:

Escenario Puchuncaví Ventanas Quintero
Base (datos reales) +1,4 +1,1 +0,9
Incendio simulado activo +87,4 +92,0 +0,9
Hay que mostrar ambos escenarios en la diapositiva y rotular la tabla. Además, el resultado del escenario base es honesto y defendible: hoy no hay amenazas activas cerca de la red.

Importantes (son las preguntas de la defensa) 4. El radio de 180 m está "calibrado" para obtener el resultado.
ruteo_resiliente.py:26-28 dice textualmente que el radio se eligió para que la ruta resiliente "encuentre el bypass". Además, el propio modelo FIRMS del proyecto usa 2.000 m.

Hay que reescribir el comentario y la diapositiva 6 ("radio calibrado").
Conviene agregar una línea en las conclusiones: con radios de 450 m o más, el norte de la red queda desconectado. Eso es un cuello de botella estructural de la red, un hallazgo de resiliencia que suma puntos en vez de restarlos. 5. Los valores λ son supuestos, no una calibración.
λ_incendio = 5,0/km determina por completo la magnitud de ΔR. Recomiendo llamarlos "supuestos" y agregar una tabla de sensibilidad de 3 filas (ya la calculé, para Puchuncaví):

λ_incendio R Dijkstra R Resiliente ΔR
0,5 65,6% 88,6% +23,0
1,0 44,5% 88,6% +44,1
5,0 1,2% 88,6% +87,4
La conclusión (el algoritmo resiliente domina) se mantiene para todos los valores. Ese es el argumento científico.

6. Criterio 5.2: viento y lluvia se modelan en la diapositiva 6 pero no tienen peso.
   Los n-fallas son 4, pero solo 2 tienen λ. Agregar dos términos para las celdas activas (exceeds) en Python y JavaScript es un cambio de pocas líneas, aunque hoy estén en 0.

7. Afirmaciones exageradas que hay que quitar o corregir:

Diapositiva 11: "87,5% de aristas disimilares" es el valor de Loncura. Para Puchuncaví es 89,8%.
Diapositiva 14, conclusión 3: "garantiza… cumplimiento estricto de DAN 151" es falso. La ruta resiliente sigue volando 436 m sobre manzanas densas, porque DAN 151 está modelada como penalización y no como prohibición.
Diapositiva 13: "< 5 ms" nunca se midió.
Diapositiva 6: "> 400 °C" no tiene fuente.
Diapositiva 12: falta explicitar los supuestos: fallas independientes entre aristas, y que la arista completa se considera expuesta si toca la zona.
Menores
ALCANCES_FASE2.md está desactualizado: menciona "Yen KSP" y se declara "Parcial" en el punto 1. Si se entrega, conviene actualizarlo.
tests/verificar.py no verifica el k=2. Bastan 2 chequeos: que k=2 sea distinta de k=1 y que su longitud sea mayor o igual.
Las salidas del ruteo resiliente no registran si el incendio simulado estaba activo ni qué λ se usaron. Hay que agregar escenario y parametros. Además, rutas_comparativas.geojson usa un bloque metadata, mientras el resto del proyecto usa etl.
La diapositiva 2 dice python:3.12-slim, pero el Dockerfile usa 3.12.15-slim.
Entrega: todo sigue sin commit, el remoto es GitHub y la URL de GitLab en la diapositiva 1 está incompleta. Hay que excluir agent.md, feedback.md, entrega_2.md y CONTINUAR REDES.txt.
Orden sugerido
Arreglar el bug de k=2, separar k=2 en su propio Feature y unificar el factor de penalización (código pequeño).
Ejecutar main.py y tests/verificar.py en Docker, y pegar los IDs reales en la diapositiva 10.
Ajustar las diapositivas 6, 11, 12, 13 y 14 (los dos escenarios, la sensibilidad, sin exageraciones) y agregar λ de viento y lluvia.
Hacer commit, limpiar y subir a GitLab UDP.
