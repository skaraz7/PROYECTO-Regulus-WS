#!/usr/bin/env python3
"""Test de la API completa con ambos endpoints"""

import requests
import json

def test_api_completa():
    base_url = "http://localhost:10000"
    
    print("=== TESTING API COMPLETA ===")
    
    # Test endpoint /scrape
    print("\n1. Testing /scrape endpoint...")
    try:
        response = requests.get(f"{base_url}/scrape?product=arroz&stores=metro&max=3", timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ /scrape: {data['count']} productos encontrados")
            if data['items']:
                print(f"  Ejemplo: {data['items'][0]['nombre']} - {data['items'][0]['precio']}")
        else:
            print(f"✗ /scrape error: {response.status_code}")
    except Exception as e:
        print(f"✗ /scrape error: {e}")
    
    # Test endpoint /chat
    print("\n2. Testing /chat endpoint...")
    try:
        chat_data = {
            "message": "arroz más barato",
            "max": 3
        }
        response = requests.post(f"{base_url}/chat", json=chat_data, timeout=30)
        if response.status_code == 200:
            data = response.json()
            print(f"✓ /chat: {data['count']} productos encontrados")
            print(f"  Respuesta IA: {data['response']}")
            print(f"  Interpretación: {data['interpretation']}")
        else:
            print(f"✗ /chat error: {response.status_code}")
    except Exception as e:
        print(f"✗ /chat error: {e}")
    
    # Test diferentes tipos de consulta
    print("\n3. Testing diferentes consultas IA...")
    consultas = [
        "aceite más caro",
        "comparar leche en todas las tiendas",
        "detergente en Metro"
    ]
    
    for consulta in consultas:
        try:
            chat_data = {"message": consulta, "max": 2}
            response = requests.post(f"{base_url}/chat", json=chat_data, timeout=30)
            if response.status_code == 200:
                data = response.json()
                print(f"✓ '{consulta}': {data['count']} productos")
            else:
                print(f"✗ '{consulta}': error {response.status_code}")
        except Exception as e:
            print(f"✗ '{consulta}': {e}")
    
    print("\n=== TEST COMPLETADO ===")

if __name__ == "__main__":
    print("Asegúrate de que la API esté corriendo en localhost:10000")
    print("Ejecuta: python app.py")
    input("Presiona Enter cuando la API esté lista...")
    test_api_completa()