# Resultados del Ruteo Resiliente y Evaluación de Métricas

El servidor local está activo en el puerto 8000:
👉 http://localhost:8000/sitio_web/

## Comparativa Cuantitativa Exacta (Aeródromo SCER $\rightarrow$ Estaciones SINCA)

| Estación Destino | Distancia Dijkstra ($k=1$) | Resiliencia Conjunto Dijkstra | Distancia Resiliente ($k=1$) | Resiliencia Conjunto Resiliente | Diferencial ($\Delta \mathcal{R}$) | Fuego en Dijkstra | Fuego en Resiliente |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Campiche** | 9,53 km | 1,3% | 11,56 km | 91,6% | **+90,3 p.p.** | 2 aristas | 0 aristas |
| **La Greda** | 6,71 km | 1,5% | 8,74 km | 96,2% | **+94,7 p.p.** | 2 aristas | 0 aristas |
| **Puchuncaví** | 14,41 km | 1,2% | 16,46 km | 88,6% | **+87,4 p.p.** | 2 aristas | 0 aristas |
| **Ventanas** | 7,80 km | 1,3% | 9,97 km | 93,3% | **+92,0 p.p.** | 2 aristas | 0 aristas |
| **Quintero** | 2,35 km | 98,2% | 2,87 km | 99,1% | **+0,9 p.p.** | 0 aristas | 0 aristas |
| **Centro Quintero** | 1,69 km | 99,5% | 1,74 km | 99,6% | **+0,1 p.p.** | 0 aristas | 0 aristas |
| **Loncura** | 2,35 km | 99,8% | 2,35 km | 99,7% | **-0,1 p.p.** | 0 aristas | 0 aristas |
| **Sur** | 3,74 km | 99,8% | 3,74 km | 99,6% | **-0,2 p.p.** | 0 aristas | 0 aristas |

## Respaldo Metodológico
- **Paper:** Kosior, M., Przystałka, P., & Panfil, W. (2024). *Adaptive Path Planning for UAV-Based Pollution Sampling*. Applied Sciences, 14(24), 12065.
- **Algoritmo de K-caminos disimilares:** Akgün, V., Erkut, E., & Batta, R. (2000). *On finding dissimilar paths*. European Journal of Operational Research, 121(2), 232–246.
- **Métrica estocástica exacta:** $\mathcal{R}(\Pi_1, \Pi_2) = S(E_C) \times [1 - (1 - S(E_1))(1 - S(E_2))]$.
