import os
import re
import json
from flask import Flask, request, jsonify

from scraper.metro import buscar_metro
from scraper.plazavea import buscar_plazavea
from scraper.tottus import buscar_tottus

app = Flask(__name__)

class AsistenteIA:
    def interpretar_consulta(self, consulta):
        consulta_lower = consulta.lower()
        
        # Detectar tienda específica
        tienda_detectada = None
        if 'metro' in consulta_lower:
            tienda_detectada = 'metro'
        elif any(palabra in consulta_lower for palabra in ['plaza vea', 'plazavea', 'plaza']):
            tienda_detectada = 'plazavea'
        elif 'tottus' in consulta_lower:
            tienda_detectada = 'tottus'
        
        # Detectar tipo de consulta
        if any(palabra in consulta_lower for palabra in ['barato', 'menor precio', 'más barato', 'economico', 'menor']):
            tipo_consulta = 'precio_minimo'
        elif any(palabra in consulta_lower for palabra in ['caro', 'mayor precio', 'más caro', 'premium', 'mayor']):
            tipo_consulta = 'precio_maximo'
        elif any(palabra in consulta_lower for palabra in ['comparar', 'comparacion', 'vs', 'versus', 'donde']):
            tipo_consulta = 'comparacion'
        else:
            tipo_consulta = 'busqueda_general'
        
        # Extraer producto
        palabras_clave = self._extraer_producto(consulta_lower)
        
        return {
            'producto_keywords': palabras_clave,
            'tienda': tienda_detectada,
            'tipo': tipo_consulta,
            'consulta_original': consulta
        }
    
    def _extraer_producto(self, consulta):
        palabras_ignorar = {
            'el', 'la', 'los', 'las', 'un', 'una', 'de', 'del', 'en', 'con', 'por', 'para',
            'que', 'cual', 'cuales', 'donde', 'como', 'cuando', 'precio', 'precios',
            'barato', 'baratos', 'caro', 'caros', 'mejor', 'mejores', 'mas', 'menos',
            'comparar', 'comparacion', 'buscar', 'encontrar', 'quiero', 'necesito',
            'metro', 'plaza', 'vea', 'tottus', 'tienda', 'tiendas', 'supermercado'
        }
        
        palabras = re.findall(r'\b\w+\b', consulta)
        palabras_filtradas = [p for p in palabras if p not in palabras_ignorar and len(p) > 2]
        
        return palabras_filtradas
    
    def procesar_resultados(self, resultados, tipo_consulta):
        if not resultados:
            return []
        
        # Filtrar productos con precio válido
        productos_validos = [r for r in resultados if r.get('precio')]
        
        if tipo_consulta == 'precio_minimo':
            return sorted(productos_validos, key=lambda x: precio_num(x.get('precio', '')))[:5]
        elif tipo_consulta == 'precio_maximo':
            return sorted(productos_validos, key=lambda x: precio_num(x.get('precio', '')), reverse=True)[:5]
        elif tipo_consulta == 'comparacion':
            # Mejor de cada tienda
            por_tienda = {}
            for prod in productos_validos:
                tienda = prod['tienda']
                precio_actual = precio_num(prod.get('precio', ''))
                if tienda not in por_tienda or precio_actual < precio_num(por_tienda[tienda].get('precio', '')):
                    por_tienda[tienda] = prod
            return list(por_tienda.values())
        else:
            return productos_validos[:10]

asistente = AsistenteIA()

def precio_num(txt):
    if not txt: return float("inf")
    m = re.search(r'(\d+[.,]?\d*)', txt.replace(',', '.'))
    return float(m.group(1)) if m else float("inf")

@app.route("/health")
def health():
    return "ok", 200

@app.route("/")
def home():
    return jsonify({
        "message": "API Completa - Supermercados Peru",
        "endpoints": {
            "/health": "Health check",
            "/scrape": "Buscar productos directamente - GET params: product, stores, max",
            "/chat": "Consultas en lenguaje natural - POST {message, max}"
        },
        "examples": {
            "scrape": "/scrape?product=arroz&stores=metro,plazavea&max=5",
            "chat": 'POST /chat {"message": "arroz más barato", "max": 5}'
        }
    })

@app.route("/scrape")
def scrape():
    producto = request.args.get("product", "arroz")
    stores = request.args.get("stores", "metro,plazavea,tottus").split(",")
    max_items = int(request.args.get("max", "10"))

    resultados = []
    
    try:
        errors = []
        
        # Metro
        if "metro" in stores:
            try:
                metro_results = buscar_metro(producto, max_items=max_items)
                resultados.extend(metro_results)
                print(f"DEBUG Metro: {len(metro_results)} productos para {producto}")
            except Exception as e:
                error_msg = f"Metro error: {str(e)}"
                print(error_msg)
                errors.append(error_msg)

        # Plaza Vea
        if "plazavea" in stores:
            try:
                pv_results = buscar_plazavea(producto, max_items=max_items)
                resultados.extend(pv_results)
                print(f"DEBUG Plaza Vea: {len(pv_results)} productos para {producto}")
            except Exception as e:
                error_msg = f"Plaza Vea error: {str(e)}"
                print(error_msg)
                errors.append(error_msg)

        # Tottus
        if "tottus" in stores:
            try:
                tottus_results = buscar_tottus(producto, max_items=max_items)
                resultados.extend(tottus_results)
                print(f"DEBUG Tottus: {len(tottus_results)} productos para {producto}")
            except Exception as e:
                error_msg = f"Tottus error: {str(e)}"
                print(error_msg)
                errors.append(error_msg)

        # Normalizar precios y ordenar
        resultados = [r for r in resultados if r.get("precio")]
        resultados.sort(key=lambda r: precio_num(r.get("precio","")))
        
        print(f"DEBUG: Total resultados={len(resultados)} para {producto} en {stores}")
        
        response = {
            "product": producto,
            "stores": stores,
            "count": len(resultados), 
            "items": resultados
        }
        
        if errors:
            response["errors"] = errors
            
        return jsonify(response)
        
    except Exception as e:
        print("ERROR GENERAL en scraper:", str(e))
        return jsonify({"error": str(e), "product": producto, "stores": stores}), 500

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    if not data or not data.get("message"):
        return jsonify({"error": "Mensaje requerido"}), 400
    
    consulta = data.get("message", "")
    max_items = int(data.get("max", "10"))
    
    # Interpretar consulta con IA
    interpretacion = asistente.interpretar_consulta(consulta)
    
    if not interpretacion['producto_keywords']:
        return jsonify({
            "message": consulta,
            "interpretation": "No pude identificar un producto en tu consulta",
            "response": "Intenta ser más específico, por ejemplo: 'arroz más barato' o 'comparar aceite'",
            "products": []
        })
    
    # Buscar productos
    producto_busqueda = ' '.join(interpretacion['producto_keywords'][:2])
    tienda_especifica = interpretacion['tienda']
    
    resultados = []
    stores_to_search = [tienda_especifica] if tienda_especifica else ['metro', 'plazavea', 'tottus']
    
    for store in stores_to_search:
        try:
            if store == 'metro':
                resultados.extend(buscar_metro(producto_busqueda, max_items=max_items))
            elif store == 'plazavea':
                resultados.extend(buscar_plazavea(producto_busqueda, max_items=max_items))
            elif store == 'tottus':
                resultados.extend(buscar_tottus(producto_busqueda, max_items=max_items))
        except Exception as e:
            app.logger.exception(f"Error en {store}")
    
    # Procesar resultados según tipo de consulta
    resultados_procesados = asistente.procesar_resultados(resultados, interpretacion['tipo'])
    
    # Generar respuesta contextual
    respuesta = generar_respuesta_contextual(interpretacion, resultados_procesados)
    
    return jsonify({
        "message": consulta,
        "interpretation": {
            "product": interpretacion['producto_keywords'],
            "store": interpretacion['tienda'],
            "query_type": interpretacion['tipo']
        },
        "response": respuesta,
        "count": len(resultados_procesados),
        "products": resultados_procesados
    })

def generar_respuesta_contextual(interpretacion, resultados):
    if not resultados:
        return f"No encontré productos de {' '.join(interpretacion['producto_keywords'])} en las tiendas."
    
    tipo = interpretacion['tipo']
    producto = ' '.join(interpretacion['producto_keywords'])
    
    if tipo == 'precio_minimo':
        mejor = resultados[0]
        return f"El {producto} más barato es: {mejor['nombre']} por {mejor['precio']} en {mejor['tienda']}"
    elif tipo == 'precio_maximo':
        caro = resultados[0]
        return f"El {producto} más caro es: {caro['nombre']} por {caro['precio']} en {caro['tienda']}"
    elif tipo == 'comparacion':
        tiendas = [r['tienda'] for r in resultados]
        return f"Comparación de {producto} en {len(tiendas)} tiendas. Mejor precio: {resultados[0]['precio']} en {resultados[0]['tienda']}"
    else:
        return f"Encontré {len(resultados)} productos de {producto}. Precios desde {resultados[0]['precio']}"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)