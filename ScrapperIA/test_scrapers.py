#!/usr/bin/env python3
"""Test rápido de los scrapers para verificar que funcionan"""

from scraper.metro import buscar_metro
from scraper.plazavea import buscar_plazavea
from scraper.tottus import buscar_tottus

def test_scrapers():
    print("=== TESTING SCRAPERS ===")
    
    # Test Metro
    print("\n1. Testing Metro...")
    try:
        resultados_metro = buscar_metro("arroz", max_items=3)
        print(f"Metro: {len(resultados_metro)} productos encontrados")
        if resultados_metro:
            print(f"Ejemplo: {resultados_metro[0]['nombre']} - {resultados_metro[0]['precio']}")
    except Exception as e:
        print(f"Error Metro: {e}")
    
    # Test Plaza Vea
    print("\n2. Testing Plaza Vea...")
    try:
        resultados_pv = buscar_plazavea("arroz", max_items=3)
        print(f"Plaza Vea: {len(resultados_pv)} productos encontrados")
        if resultados_pv:
            print(f"Ejemplo: {resultados_pv[0]['nombre']} - {resultados_pv[0]['precio']}")
    except Exception as e:
        print(f"Error Plaza Vea: {e}")
    
    # Test Tottus
    print("\n3. Testing Tottus...")
    try:
        resultados_tottus = buscar_tottus("arroz", max_items=3)
        print(f"Tottus: {len(resultados_tottus)} productos encontrados")
        if resultados_tottus:
            print(f"Ejemplo: {resultados_tottus[0]['nombre']} - {resultados_tottus[0]['precio']}")
    except Exception as e:
        print(f"Error Tottus: {e}")
    
    print("\n=== TEST COMPLETADO ===")

if __name__ == "__main__":
    test_scrapers()