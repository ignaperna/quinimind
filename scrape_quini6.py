import requests
from bs4 import BeautifulSoup
import json
import os
import re
from datetime import datetime

# URL objetivo
URL = "https://www.quini-6-resultados.com.ar/"

def limpiar_numero(texto):
    """Extrae solo los dígitos de un texto"""
    return int(re.sub(r'\D', '', texto))

def run_scraper():
    print(f"⚡ Iniciando scraping de {URL}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Extraer Fecha y Nro de Sorteo
        # Buscamos textos como "Sorteo Nro 3330" y la fecha
        texto_general = soup.get_text()
        
        # Intentar buscar el ID del sorteo con Regex
        match_id = re.search(r'Sorteo N°\s*(\d+)', texto_general, re.IGNORECASE)
        sorteo_id = int(match_id.group(1)) if match_id else 0
        
        # Intentar buscar fecha (formato dd/mm/aaaa)
        match_date = re.search(r'(\d{2}/\d{2}/\d{4})', texto_general)
        sorteo_date = match_date.group(1) if match_date else datetime.now().strftime("%d/%m/%Y")

        print(f"📅 Detectado: Sorteo {sorteo_id} del {sorteo_date}")

        # 2. Extraer Números por Modalidad
        # La estrategia es buscar las tablas o secciones por palabras clave
        modes_data = {
            "tradicional": [],
            "laSegunda": [],
            "revancha": [],
            "siempreSale": []
        }

        # Mapeo de textos en la web a nuestras claves del JSON
        keywords = {
            "TRADICIONAL": "tradicional",
            "LA SEGUNDA": "laSegunda",
            "REVANCHA": "revancha",
            "SIEMPRE SALE": "siempreSale"
        }
        
        # Buscamos todas las tablas que contengan bolas
        # Nota: Esto depende de la estructura HTML específica. 
        # Buscaremos celdas que parezcan números de bolas (clases comunes o estructura)
        # Una estrategia genérica robusta: Buscar el título y luego los números siguientes.
        
        all_text_nodes = soup.find_all(text=True)
        
        for key_text, json_key in keywords.items():
            # Buscar el nodo de texto que contiene el nombre del sorteo
            for node in all_text_nodes:
                if key_text in node.upper():
                    # Encontrado el título, buscamos números cercanos en el DOM
                    # Generalmente están en un contenedor padre o tabla siguiente
                    parent = node.parent.parent # Subir niveles para encontrar el contenedor
                    
                    # Buscar elementos que contengan números (td o div con clases de bolas)
                    # En quini-6-resultados suelen estar en tablas
                    numeros_encontrados = []
                    
                    # Iteramos elementos siguientes para encontrar números
                    # (Esta lógica busca números de 2 dígitos típicos de sorteos)
                    container = parent.find_next_sibling() or parent
                    
                    # Extraer todos los números del contenedor cercano
                    textos_numeros = container.find_all(string=re.compile(r'^\d{2}$'))
                    
                    for num_str in textos_numeros:
                        try:
                            val = int(num_str.strip())
                            if 0 <= val <= 45 and val not in numeros_encontrados:
                                numeros_encontrados.append(val)
                        except:
                            continue
                            
                        if len(numeros_encontrados) == 6:
                            break
                    
                    # Si no encontramos 6, intentamos un método de respaldo (tablas)
                    if len(numeros_encontrados) < 6:
                         tables = soup.find_all('table')
                         for table in tables:
                             if key_text in table.get_text().upper():
                                 nums = re.findall(r'\\b\d{2}\\b', table.get_text())
                                 # Filtramos y tomamos los primeros 6 únicos
                                 uniques = []
                                 for n in nums:
                                     ni = int(n)
                                     if ni not in uniques and ni <= 45:
                                         uniques.append(ni)
                                 numeros_encontrados = uniques[:6]

                    modes_data[json_key] = sorted(numeros_encontrados)
                    break

        # 3. Construir JSON Final
        final_data = {
            "id": sorteo_id,
            "date": sorteo_date,
            "modes": modes_data
        }

        # 4. Guardar en public/data.json
        # ADJUSTED PATH FOR PROJECT STRUCTURE
        output_dir = os.path.join("quinimind-frontend", "public")
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            
        output_path = os.path.join(output_dir, "data.json")
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_data, f, indent=2)
            
        print(f"✅ Datos guardados exitosamente en: {output_path}")
        print(json.dumps(final_data, indent=2))

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        exit(1)

if __name__ == "__main__":
    run_scraper()
