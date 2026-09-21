import math
import json

def utm_to_latlon(easting, northing, zone=19, northern=False):
    a = 6378137.0
    f = 1 / 298.257223563
    b = a * (1 - f)
    e = math.sqrt(1 - (b / a) ** 2)
    e_prime_sq = (e ** 2) / (1 - e ** 2)
    k0 = 0.9996
    
    x = easting - 500000.0
    y = northing if northern else northing - 10000000.0
    
    m = y / k0
    mu = m / (a * (1 - e**2 / 4 - 3 * e**4 / 64 - 5 * e**6 / 256))
    
    e1 = (1 - math.sqrt(1 - e**2)) / (1 + math.sqrt(1 - e**2))
    j1 = 3 * e1 / 2 - 27 * e1**3 / 32
    j2 = 21 * e1**2 / 16 - 55 * e1**4 / 32
    j3 = 151 * e1**3 / 96
    j4 = 1097 * e1**4 / 512
    
    fp = mu + j1 * math.sin(2 * mu) + j2 * math.sin(4 * mu) + j3 * math.sin(6 * mu) + j4 * math.sin(8 * mu)
    
    c1 = e_prime_sq * math.cos(fp)**2
    t1 = math.tan(fp)**2
    r1 = a * (1 - e**2) / (1 - e**2 * math.sin(fp)**2)**1.5
    n1 = a / math.sqrt(1 - e**2 * math.sin(fp)**2)
    d = x / (n1 * k0)
    
    lat = fp - (n1 * math.tan(fp) / r1) * (d**2 / 2 - (5 + 3 * t1 + 10 * c1 - 4 * c1**2 - 9 * e_prime_sq) * d**4 / 24 + (61 + 90 * t1 + 298 * c1 + 45 * t1**2 - 252 * e_prime_sq - 3 * c1**2) * d**6 / 720)
    lon = (d - (1 + 2 * t1 + c1) * d**3 / 6 + (5 - 2 * c1 + 28 * t1 - 3 * c1**2 + 8 * e_prime_sq + 24 * t1**2) * d**5 / 120) / math.cos(fp)
    
    lon_origin = (zone - 1) * 6 - 180 + 3
    lon_deg = lon_origin + math.degrees(lon)
    lat_deg = math.degrees(lat)
    return round(lat_deg, 6), round(lon_deg, 6)

# Datos de las 9 estaciones desde coordenadas_UTM_zonas.txt
raw_stations = [
    {
        "id": "sinca_puchuncavi",
        "name": "Estación Puchuncaví",
        "easting": 274379,
        "northing": 6377331,
        "elevation": 95,
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 1
    },
    {
        "id": "sinca_campiche",
        "name": "Estación Campiche",
        "easting": 270343,
        "northing": 6375300,
        "elevation": 30,
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 2
    },
    {
        "id": "sinca_ventanas",
        "name": "Estación Ventanas",
        "easting": 267547,
        "northing": 6374609, # Corregido de 6474609 a 6374609 (typo 100km norte en original)
        "elevation": 12,
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 3
    },
    {
        "id": "sinca_la_greda",
        "name": "Estación La Greda",
        "easting": 268185,
        "northing": 6373910,
        "elevation": 35,
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 3
    },
    {
        "id": "sinca_los_maitenes",
        "name": "Estación Los Maitenes",
        "easting": 270073,
        "northing": 6372171,
        "elevation": 45,
        "pollutants": ["SO2", "PM10"],
        "priority": 2
    },
    {
        "id": "sinca_quintero",
        "name": "Estación Quintero",
        "easting": 262528,
        "northing": 6371108, # Corregido de 63711087 (8 dígitos) a 6371108
        "elevation": 18,
        "pollutants": ["SO2", "PM10", "PM2.5", "O3"],
        "priority": 2
    },
    {
        "id": "sinca_centro_quintero",
        "name": "Estación Centro Quintero",
        "easting": 262853,
        "northing": 6369407,
        "elevation": 22,
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 3
    },
    {
        "id": "sinca_loncura",
        "name": "Estación Loncura",
        "easting": 266226,
        "northing": 6368689,
        "elevation": 15,
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 2
    },
    {
        "id": "sinca_sur",
        "name": "Estación Sur",
        "easting": 267461,
        "northing": 6368037,
        "elevation": 25,
        "pollutants": ["SO2", "PM10", "PM2.5"],
        "priority": 2
    }
]

features = []

# 1. Base principal de despacho y RTH: Aeródromo de Quintero (SCER)
features.append({
    "type": "Feature",
    "properties": {
        "id": "base_scer",
        "name": "Aeródromo de Quintero (SCER)",
        "type": "base",
        "role": "Base de Despacho Principal y Retorno Seguro (RTH)",
        "elevation_msnm": 28,
        "is_dispatch": True,
        "sensors": []
    },
    "geometry": {
        "type": "Point",
        "coordinates": [-71.517300, -32.784200, 28]
    }
})

# 2. Las 9 Estaciones SINCA convertidas desde UTM
for st in raw_stations:
    lat, lon = utm_to_latlon(st["easting"], st["northing"], 19, False)
    features.append({
        "type": "Feature",
        "properties": {
            "id": st["id"],
            "name": st["name"],
            "type": "station",
            "role": "Monitoreo Calidad del Aire (SINCA / MMA)",
            "utm_easting": st["easting"],
            "utm_northing": st["northing"],
            "elevation_msnm": st["elevation"],
            "pollutants": st["pollutants"],
            "priority": st["priority"]
        },
        "geometry": {
            "type": "Point",
            "coordinates": [lon, lat, st["elevation"]]
        }
    })

geojson_obj = {
    "type": "FeatureCollection",
    "name": "Nodos_SINCA_y_Base_Quintero",
    "crs": {
        "type": "name",
        "properties": {
            "name": "urn:ogc:def:crs:OGC:1.3:CRS84"
        }
    },
    "features": features
}

output_path = r'c:\Users\Benjamin\Desktop\ruteo_redes\public\data\nodes.geojson'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(geojson_obj, f, indent=2, ensure_ascii=False)

print(f"GeoJSON generado exitosamente con {len(features)} nodos en {output_path}")
