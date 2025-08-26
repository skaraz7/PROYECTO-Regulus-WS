import sys, re
from typing import List, Dict

def _precio_num(txt:str) -> float:
    if not txt:
        return 1e12
    m = re.search(r'(\d+[.,]?\d*)', txt.replace(',', '.'))
    return float(m.group(1)) if m else 1e12

resultados: List[Dict] = []
producto = sys.argv[1] if len(sys.argv) > 1 else "arroz"

# Metro
try:
    from metro import buscar_metro
    resultados.extend(buscar_metro(producto, max_items=10))
except Exception as e:
    print("Metro falló:", e)

# Plaza Vea
try:
    from plazavea import buscar_plazavea
    resultados.extend(buscar_plazavea(producto, max_items=10))
except Exception as e:
    print("Plaza Vea falló:", e)

# Tottus
try:
    from tottus import buscar_tottus
    resultados.extend(buscar_tottus(producto, max_items=10))
except Exception as e:
    print("Tottus falló:", e)

resultados = [r for r in resultados if r.get("precio")]
resultados.sort(key=lambda r: _precio_num(r.get("precio","")))
for r in resultados:
    print(f'{r.get("tienda")} – {r.get("nombre")} – {r.get("precio")} – {r.get("link")}')
if not resultados:
    print("Sin resultados por ahora.")