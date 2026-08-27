import logging
import sys
import cloudscraper # <--- CAMBIO IMPORTANTE
from bs4 import BeautifulSoup
import json
import os
import re
import requests

# URL objetivo
URL = "https://www.quini-6-resultados.com.ar/"

logger = logging.getLogger(__name__)


class ScraperError(Exception):
    pass


def limpiar_numero(texto):
    """Extrae solo los dígitos de un texto"""
    return int(re.sub(r'\D', '', texto))


def run_scraper():
    logger.info(f"⚡ Iniciando scraping de {URL} con Cloudscraper...")

    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'es-ES,es;q=0.9,en;q=0.8',
        'Referer': 'https://www.google.com/',
        'Upgrade-Insecure-Requests': '1'
    }

    try:
        response = scraper.get(URL, headers=headers, timeout=30)
        if response.status_code == 403:
            logger.error("❌ Error 403: El servidor nos detectó como bot. Intentando bypass...")
            raise ScraperError("Bloqueo 403 persistente.")
        response.raise_for_status()
    except requests.RequestException as e:
        raise ScraperError(f"Error de red al obtener los resultados: {e}") from e

    soup = BeautifulSoup(response.content, 'html.parser')

    # 1. Extraer Fecha y Nro de Sorteo
    texto_general = soup.get_text()
    validation_errors = []

    match_id = re.search(r'(?:Sorteo N°|Nro\. Sorteo:)\s*(\d+)', texto_general, re.IGNORECASE)
    if match_id:
        sorteo_id = int(match_id.group(1))
    else:
        sorteo_id = None
        validation_errors.append("No se encontró el identificador del sorteo")

    match_date = re.search(r'(\d{2}/\d{2}/\d{4})', texto_general)
    if match_date:
        sorteo_date = match_date.group(1)
    else:
        sorteo_date = None
        validation_errors.append("No se encontró la fecha del sorteo")

    if match_id and match_date:
        logger.info(f"📅 Detectado: Sorteo {sorteo_id} del {sorteo_date}")

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

    # Strategy: Find the keyword (usually in strong/b/h3), then scan next elements/strings for numbers.
    # Numbers might be dash separated "05 - 10 - ..." or individual in text pointers.

    for key_text, json_key in keywords.items():
        target_node = soup.find(string=re.compile(re.escape(key_text), re.IGNORECASE))
        numeros_encontrados = []

        if target_node:
            current_element = target_node
            steps = 0
            max_steps = 50

            for element in current_element.next_elements:
                steps += 1
                if steps > max_steps:
                    break

                if isinstance(element, str):
                    txt = element.strip()
                    if not txt:
                        continue

                    if '-' in txt:
                        parts = txt.split('-')
                        for p in parts:
                            p_clean = p.strip()
                            if re.match(r'^\d{1,2}$', p_clean):
                                val = int(p_clean)
                                if val <= 45 and val not in numeros_encontrados:
                                    numeros_encontrados.append(val)
                    elif re.match(r'^\d{1,2}$', txt):
                        val = int(txt)
                        if val <= 45 and val not in numeros_encontrados:
                            numeros_encontrados.append(val)

                if len(numeros_encontrados) >= 6:
                    break

        modes_data[json_key] = sorted(numeros_encontrados[:6])
        if target_node:
            logger.info(f"   -> {key_text}: {modes_data[json_key]}")
        else:
            logger.warning(f"⚠️ No se encontró la etiqueta para {key_text}")

        if len(modes_data[json_key]) != 6:
            validation_errors.append(
                f"{key_text}: se encontraron {len(modes_data[json_key])} números, se esperaban 6"
            )

    if validation_errors:
        raise ScraperError("Errores de validación: " + "; ".join(validation_errors))

    final_data = {
        "id": sorteo_id,
        "date": sorteo_date,
        "modes": modes_data
    }

    output_dir = os.path.join("quinimind-frontend", "public")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_path = os.path.join(output_dir, "data.json")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(final_data, f, indent=2)

    logger.info(f"✅ Datos guardados exitosamente en: {output_path}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        run_scraper()
    except ScraperError:
        logger.exception("❌ Error crítico durante el scraping")
        sys.exit(1)
