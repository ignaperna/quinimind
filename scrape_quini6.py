import cloudscraper # <--- CAMBIO IMPORTANTE
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
    print(f"⚡ Iniciando scraping de {URL} con Cloudscraper...")
    
    try:
        # Creamos un scraper que simula ser un navegador Chrome real
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'desktop': True
            }
        )

        # Headers adicionales para parecer aún más humanos
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
            'Referer': 'https://www.google.com/',
            'Upgrade-Insecure-Requests': '1'
        }

        response = scraper.get(URL, headers=headers)
        
        # Verificar si nos bloquearon (Status 403)
        if response.status_code == 403:
            print("❌ Error 403: El servidor nos detectó como bot. Intentando bypass...")
            # A veces reintentar ayuda, pero si persiste es bloqueo de IP de GitHub
            raise Exception("Bloqueo 403 persistente.")
            
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # 1. Extraer Fecha y Nro de Sorteo
        texto_general = soup.get_text()
        
        match_id = re.search(r'Sorteo N°\s*(\d+)', texto_general, re.IGNORECASE)
        sorteo_id = int(match_id.group(1)) if match_id else 0
        
        match_date = re.search(r'(\d{2}/\d{2}/\d{4})', texto_general)
        sorteo_date = match_date.group(1) if match_date else datetime.now().strftime("%d/%m/%Y")

        print(f"📅 Detectado: Sorteo {sorteo_id} del {sorteo_date}")

        # 2. Extraer Números por Modalidad
        modes_data = {
            "tradicional": [],
            "laSegunda": [],
            "revancha": [],
            "siempreSale": []
        }

        keywords = {
            "TRADICIONAL": "tradicional",
            "LA SEGUNDA": "laSegunda",
            "REVANCHA": "revancha",
            "SIEMPRE SALE": "siempreSale"
        }
        
        all_text_nodes = soup.find_all(text=True)
        
        for key_text, json_key in keywords.items():
            for node in all_text_nodes:
                if key_text in node.upper():
                    parent = node.parent.parent 
                    numeros_encontrados = []
                    container = parent.find_next_sibling() or parent
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
                    
                    if len(numeros_encontrados) < 6:
                         tables = soup.find_all('table')
                         for table in tables:
                             if key_text in table.get_text().upper():
                                 nums = re.findall(r'\\b\d{2}\\b', table.get_text())
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

    except Exception as e:
        print(f"❌ Error crítico: {e}")
        exit(1)

if __name__ == "__main__":
    run_scraper()
