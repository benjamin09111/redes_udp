"""
benchmark_utm_vs_haversine.py
Benchmark cuantitativo para documentar en el Paper:
Compara el tiempo de cómputo (CT) de 100.000 cálculos de distancia euclidiana UTM 19S
versus la fórmula esférica tradicional de Haversine.
"""

import time
import math
import random

def haversine(c1, c2):
    lon1, lat1, alt1 = c1
    lon2, lat2, alt2 = c2
    R = 6371000.0
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return math.sqrt((R * c)**2 + (alt2 - alt1)**2)

def cartesian_utm(u1, u2):
    dx = u2[0] - u1[0]
    dy = u2[1] - u1[1]
    dz = u2[2] - u1[2]
    return math.sqrt(dx*dx + dy*dy + dz*dz)

# Generar 100.000 pares aleatorios en la Bahía de Quintero
N = 100000
geo_pairs = []
utm_pairs = []

for _ in range(N):
    lat1, lon1, alt1 = random.uniform(-32.82, -32.68), random.uniform(-71.55, -71.40), random.uniform(10, 100)
    lat2, lon2, alt2 = random.uniform(-32.82, -32.68), random.uniform(-71.55, -71.40), random.uniform(10, 100)
    geo_pairs.append(((lon1, lat1, alt1), (lon2, lat2, alt2)))
    
    # Simular UTM aprox en metros
    x1, y1, z1 = lon1 * 92000, lat1 * 111000, alt1
    x2, y2, z2 = lon2 * 92000, lat2 * 111000, alt2
    utm_pairs.append(((x1, y1, z1), (x2, y2, z2)))

print(f"--- Benchmark Científico ({N:,} cálculos de distancia 3D) ---")

t0 = time.perf_counter()
for p in geo_pairs:
    d = haversine(p[0], p[1])
t_haversine = time.perf_counter() - t0
print(f"1. Haversine (Esférico angular): {t_haversine:.4f} segundos")

t0 = time.perf_counter()
for p in utm_pairs:
    d = cartesian_utm(p[0], p[1])
t_utm = time.perf_counter() - t0
print(f"2. Cartesiano UTM 19S (Métrico):   {t_utm:.4f} segundos")

speedup = t_haversine / t_utm
print(f"-> Aceleración computacional (Speedup): {speedup:.2f}x más rápido en CPU")
