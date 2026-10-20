-- ============================================================================
-- Generación de k rutas distintas (k >= 2) con pgRouting (pgr_dijkstra)
-- Basadas ÚNICAMENTE en la distancia física en km (cost = length_m)
-- ============================================================================

-- OPCIÓN A: Generación directa con pgr_KSP (Algoritmo de Yen nativo en pgRouting)
-- Genera simultáneamente k=1 y k=2 basadas exclusivamente en la longitud geométrica
SELECT path_id AS k_ruta,
       count(*) FILTER (WHERE edge <> -1) AS total_tramos,
       round(sum(cost)::numeric, 1)       AS longitud_total_m,
       round((sum(cost) / 1000.0)::numeric, 2) AS longitud_total_km
FROM pgr_ksp(
    'SELECT id, source, target, length_m AS cost, length_m AS reverse_cost FROM infra_edge',
    (SELECT id FROM infra_node WHERE code = 'base_scer'),
    (SELECT id FROM infra_node WHERE code = 'sinca_puchuncavi'),
    2,
    directed := true
)
GROUP BY path_id
ORDER BY path_id;


-- OPCIÓN B: Generación secuencial mediante pgr_dijkstra con penalización de aristas (Akgün et al., 2000)

-- 1. Obtener la ruta k=1 con pgr_dijkstra
SELECT d.seq,
       d.node,
       d.edge,
       COALESCE(e.length_m, 0) AS longitud_tramo_m,
       d.agg_cost              AS distancia_acumulada_m,
       n.name                  AS nombre_vertice
FROM pgr_dijkstra(
    'SELECT id, source, target, length_m AS cost, length_m AS reverse_cost FROM infra_edge',
    (SELECT id FROM infra_node WHERE code = 'base_scer'),
    (SELECT id FROM infra_node WHERE code = 'sinca_puchuncavi'),
    directed := true
) AS d
LEFT JOIN infra_edge e ON e.id = d.edge
JOIN infra_node n ON n.id = d.node
ORDER BY d.seq;

-- 2. Para calcular k=2 con pgr_dijkstra:
-- Se obtienen los IDs reales de las 22 aristas de k=1 y se penalizan por un factor x4.0:
-- Aristas reales k=1 a Puchuncaví: 3, 490, 573, 69, 71, 623, 622, 618, 616, 617, 24, 22, 584, 158, 159, 633, 574, 149, 147, 251, 253, 9
--
SELECT d.seq, d.node, d.edge, e.length_m, d.agg_cost
FROM pgr_dijkstra(
    'SELECT id, source, target,
            CASE WHEN id IN (3, 490, 573, 69, 71, 623, 622, 618, 616, 617, 24, 22, 584, 158, 159, 633, 574, 149, 147, 251, 253, 9)
                 THEN cost * 4.0 ELSE cost END AS cost,
            CASE WHEN id IN (3, 490, 573, 69, 71, 623, 622, 618, 616, 617, 24, 22, 584, 158, 159, 633, 574, 149, 147, 251, 253, 9)
                 THEN reverse_cost * 4.0 ELSE reverse_cost END AS reverse_cost
     FROM infra_edge',
    (SELECT id FROM infra_node WHERE code = 'base_scer'),
    (SELECT id FROM infra_node WHERE code = 'sinca_puchuncavi'),
    directed := true
) AS d LEFT JOIN infra_edge e ON e.id = d.edge;
