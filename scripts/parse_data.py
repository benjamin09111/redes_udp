import struct
import math

dbf_path = r'c:\Users\Benjamin\Desktop\data_internet\aerodromos_todo_chile\Aeropuertos.dbf'
shp_path = r'c:\Users\Benjamin\Desktop\data_internet\aerodromos_todo_chile\Aeropuertos.shp'

with open(dbf_path, 'rb') as f:
    header = f.read(32)
    num_records, header_len, record_len = struct.unpack('<IHH', header[4:12])
    fields = []
    while True:
        b = f.read(1)
        if b == b'\r' or not b:
            break
        f_data = b + f.read(31)
        name = f_data[:11].replace(b'\x00', b'').decode('latin1').strip()
        f_type = chr(f_data[11])
        f_len = f_data[16]
        fields.append((name, f_type, f_len))
    
    f.seek(header_len)
    records = []
    for i in range(num_records):
        rec_data = f.read(record_len)
        if not rec_data:
            break
        offset = 1
        row = {}
        for name, f_type, f_len in fields:
            val = rec_data[offset:offset+f_len].decode('latin1', errors='replace').strip()
            row[name] = val
            offset += f_len
        records.append(row)

# Now read shp geometries (Point type 1)
# Header: 100 bytes
with open(shp_path, 'rb') as f:
    shp_header = f.read(100)
    # Read records
    for i, row in enumerate(records):
        rec_header = f.read(8)
        if not rec_header:
            break
        rec_num, content_len = struct.unpack('>II', rec_header)
        shape_type = struct.unpack('<I', f.read(4))[0]
        if shape_type == 1: # Point: double X, double Y
            x, y = struct.unpack('<dd', f.read(16))
            row['shp_x'] = x
            row['shp_y'] = y

print(f"Total aeródromos leídos: {len(records)}")
# Print all in Valparaíso or nearby
for i, r in enumerate(records):
    comuna = r.get('Comuna', '')
    aero = r.get('Aerodromo', '')
    oaci = r.get('cod_oaci', '')
    region = r.get('Region', '')
    
    # Check if in Region V or mentions Quintero, Viña, Rodelillo, Santo Domingo, etc.
    if any(k in f"{comuna} {aero} {region}".lower() for k in ['valpara', 'quintero', 'puchuncavi', 'viña', 'concón', 'concon', 'casablanca', 'san antonio']):
        print(f"[{i}] {oaci} | {aero} | {comuna} | {region} | coords: ({r.get('shp_x')}, {r.get('shp_y')})")
