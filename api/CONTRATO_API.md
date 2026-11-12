# Contrato de la API — Fase 3 (Mitad A → Mitad B)

Backend listo y probado (`python3 tests/test_fase3.py`). Este documento es todo lo que el
frontend necesita saber.

## Cómo levantarlo

```bash
pip install -r requirements.txt
uvicorn api.servidor:app --port 8000        # desde la raíz del repo
# http://localhost:8000/sitio_web/   (sitio)   |   http://localhost:8000/docs  (Swagger automático)
```

**Para Docker** (pendiente, lo hace quien tenga la Mitad B): en `docker-compose.yml` reemplazar el
servicio `web` por

```yaml
  web:
    image: uav-ruteo:local
    working_dir: /app
    command: uvicorn api.servidor:app --host 0.0.0.0 --port 8000
    environment:
      DB_HOST: db
      DB_PORT: "5432"
      DB_NAME: uav
      DB_USER: uav
      DB_PASSWORD: uav
      RUTEO_BACKEND: python        # "pgrouting" ejecuta pgr_dijkstra en la BD (sin probar)
    depends_on:
      db:
        condition: service_healthy
    volumes:
      - ./:/app:ro
    ports:
      - "8000:8000"
```
y reconstruir la imagen (`docker compose build`) porque cambió `requirements.txt`.

## Endpoints

| Método | Ruta | Para qué |
|---|---|---|
| GET | `/api/destinos` | Origen por defecto y los 8 destinos (`id`, `code`, `name`, `lon`, `lat`) → dropdown |
| GET | `/api/capas` | Capas de amenaza activables (`id` + descripción) → checkboxes |
| GET | `/api/rutas` | Corre las 4 técnicas → GeoJSON + métricas → mapa y leyenda |
| GET | `/api/simulacion` | Una realización Monte Carlo → botón "Simular fallas" |

### `GET /api/rutas`

| Parámetro | Default | Notas |
|---|---|---|
| `destino` **o** `destino_id` | — (obligatorio uno) | `destino` es el código, ej. `sinca_quintero` |
| `origen_id` | `base_scer` | |
| `autonomia_max` | 10500 | metros; restricción dura solo en el MILP |
| `beta` | 1000 | aversión al riesgo |
| `capas` | todas menos `contingencia` | coma-separadas: `incendio,sismo,viento,lluvia,niebla,humedad,densidad,c2` |
| `contingencia` | false | `true` = incendio en Planta de Asfaltos |
| `mc_n` | 0 | si > 0 agrega `supervivencia_mc_pct` por técnica |
| `seed` | — | para `mc_n` reproducible |
| `backend` | `python` | o `pgrouting` |

Respuesta (GeoJSON `FeatureCollection` con campos extra):

```jsonc
{
  "type": "FeatureCollection",
  "features": [                       // una LineString por camino (Akgün aporta 2)
    { "type": "Feature",
      "geometry": { "type": "LineString", "coordinates": [[lon, lat], ...] },
      "properties": { "tecnica": "milp_exacto", "nombre": "...", "color": "#2ca02c",
                      "rol": "principal",            // "alternativa" = 2.º camino de Akgün
                      "longitud_km": 8.692, "computo_ms": 84.2, "resiliencia_R": 0.2331,
                      "mejor_resiliencia": false, "viable": true,
                      "nodos": [...], "aristas": [...] } }
  ],
  "mejor_resiliencia": "metaheuristica_akgun",       // null si ninguna ruta es viable
  "tecnicas": {                                      // para la LEYENDA (sin geometrías)
    "milp_exacto": { "nombre": "...", "color": "#2ca02c", "estado": "ok",
                     "longitud_km": 8.69, "computo_ms": 84.2, "resiliencia_R": 0.233,
                     "supervivencia_mc_pct": 22.4,   // solo si mc_n > 0
                     "viable": true, "cumple_autonomia": true, "bloqueos_en_ruta": 0,
                     "backend": "HiGHS", "pct_densas": 12.0, "pct_sin_c2": 3.1 },
    "metaheuristica_akgun": { ..., "solape_pct": 64.7, "diversidad_pct": 96.6, "n_caminos": 2 }
  },
  "capas_activas": ["c2", "densidad", ...], "parametros": {...}, "modelo_ms": 1021.3
}
```

`estado` de cada técnica: `ok` · `sin_ruta` (destino bloqueado/inalcanzable) · `infactible`
(MILP: `motivo = autonomia_insuficiente`) · `error`. Si no es `ok`, la técnica no trae
`features` ni métricas: mostrar "Sin ruta" en la leyenda.

Las 4 técnicas son `dijkstra_distancia`, `milp_exacto`, `dijkstra_multicriterio`,
`metaheuristica_akgun`. **Los 4 checkboxes de rutas** = mostrar/ocultar los `features` con
esa `properties.tecnica` (no hace falta volver a llamar a la API).

### `GET /api/simulacion`

Mismos parámetros de consulta que `/api/rutas` (sin `mc_n`) más `seed` (si falta, se sortea y se
devuelve). Para cada nodo y arista se sortea `u ∈ [0,100)`; **falla si `u < p_falla·100`**.

```jsonc
{ "type": "FeatureCollection",
  "features": [ // SOLO lo que falló: pintar en rojo
    { "geometry": {"type": "LineString", ...},
      "properties": {"tipo": "arista", "id": 41, "p_falla": 0.34, "u": 12.7, "bloqueada": false} },
    { "geometry": {"type": "Point", ...},
      "properties": {"tipo": "nodo", "id": 9, "p_falla": 1.0, "u": 55.0, "bloqueado": true} } ],
  "seed": 5, "n_aristas_caidas": 213, "n_nodos_caidos": 86,
  "tecnicas": { "milp_exacto": {"sobrevive": false, "texto": "Falló", "estado": "ok"},
                "dijkstra_multicriterio": {"sobrevive": null, "texto": "Sin ruta", "estado": "sin_ruta"} } }
```
Una técnica de 2 caminos (Akgün) "Sobrevivió" si **al menos uno** de sus caminos sobrevive.
Hay que llamar con **los mismos parámetros** que se usaron en `/api/rutas` (se reutiliza el caché).

## Qué decide quién (cosas que NO están en el código)

- **Niebla:** con los datos actuales bloquea 198 aristas y 71 nodos → Campiche y Puchuncaví
  quedan sin ruta (salvo en el Dijkstra base, que ignora bloqueos y devuelve R = 0).
  Desactivar la capa `niebla` los habilita. Decisión del equipo antes de llenar la Tabla 7.
- En el **escenario base T1, T2 y T3 dan casi la misma ruta** (no hay amenazas sobre ella);
  difieren con la contingencia. Es un resultado válido, pero el paper no debería esperar filas distintas.
- Recompensa de muestreo R(e) = 0 en todo el grafo (ninguna estación SINCA está en alerta).
