
import requests
from bs4 import BeautifulSoup
import re
import time
from urllib.parse import urljoin
from database import guardar_sorteo

# Constants
BASE_URL = "https://www.quini-6-resultados.com.ar/"
MODALITIES = [
    "TRADICIONAL",
    "LA SEGUNDA",
    "REVANCHA",
    "SIEMPRE SALE"
]

def get_soup(url):
    """Fetches a URL and returns a BeautifulSoup object."""
    try:
        response = requests.get(url, timeout=15)
        response.raise_for_status()
        return BeautifulSoup(response.content, 'html.parser')
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def extract_draw_info(soup):
    """Extracts date and draw ID from the detail page header."""
    header = soup.find(string=lambda text: text and "Sorteo Nro." in text)
    if not header:
        return None, None
    
    header_text = header.strip()
    # Approx format: "Sorteo Nro. 3330 del dia domingo 14-12-2025"
    
    # Extract ID
    id_match = re.search(r"Sorteo Nro\.\s*(\d+)", header_text)
    draw_id = id_match.group(1) if id_match else None
    
    # Extract Date
    # Supports single digit days/months e.g. 7-12-2025
    date_match = re.search(r"(\d{1,2}-\d{1,2}-\d{4})", header_text)
    date = date_match.group(1) if date_match else None
    
    return draw_id, date

def extract_numbers(soup, modality_name):
    """Extracts winning numbers for a specific modality."""
    # Find the header for the modality (case insensitive partial match)
    header = soup.find(string=lambda text: text and modality_name in text.upper())
    
    if not header:
        print(f"  Warning: Modality '{modality_name}' header not found.")
        return None

    # The numbers are usually in a <p class="numeros"> tag following the header
    # We look for the next 'p' tag with class 'numeros'
    curr = header.parent # usually h3
    
    # Traverse siblings to find the numbers
    for _ in range(5): # Limit search depth
        curr = curr.find_next()
        if not curr:
            break
        if curr.name == 'p' and 'numeros' in curr.get('class', []):
            text = curr.get_text(strip=True)
            # Text is like "00 - 25 - 26 - 28 - 34 - 41"
            numbers = [n.strip() for n in text.split('-') if n.strip().isdigit()]
            if len(numbers) == 6:
                return numbers
            
    print(f"  Warning: Numbers for '{modality_name}' not found or invalid format.")
    return None


import json
import os

# ... existing code ...

def save_to_json(draw_data):
    """Saves the draw data to a JSON file for the React frontend."""
    # Define path to public folder
    # Assuming code is running from project root "QUINIMIND AI"
    # and frontend is in "quinimind-frontend"
    output_path = os.path.join("quinimind-frontend", "public", "data.json")
    
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(draw_data, f, indent=2)
        print(f"  Successfully saved JSON to {output_path}")
    except Exception as e:
        print(f"  Error saving JSON: {e}")

def main():
    print(f"Starting scrape of {BASE_URL}...")
    
    main_soup = get_soup(BASE_URL)
    if not main_soup:
        print("Failed to access main page. Aborting.")
        return

    # Find all links to previous draws
    links = []
    for a in main_soup.find_all('a', href=True):
        if "sorteo-" in a['href'] and ".htm" in a['href']:
            links.append(urljoin(BASE_URL, a['href']))
    
    links = sorted(list(set(links)), reverse=True)
    print(f"Found {len(links)} draw links.")
    
    # Process only the LATEST draw for the JSON file (index 0)
    # We will still iterate all to save to DB, but let's capture the first valid one for JSON
    latest_draw_json = None
    
    for i, link in enumerate(links):
        print(f"Processing ({i+1}/{len(links)}): {link}")
        
        soup = get_soup(link)
        if not soup:
            continue
            
        draw_id, date = extract_draw_info(soup)
        if not draw_id or not date:
            continue
            
        print(f"  Draw: {draw_id} | Date: {date}")
        
        # Structure for JSON: { id: 3330, date: "...", modes: { tradicional: [], ... } }
        current_draw_data = {
            "id": int(draw_id),
            "date": date,
            "modes": {}
        }
        
        for modal in MODALITIES:
            numbers = extract_numbers(soup, modal)
            if numbers:
                # Save to DB
                row = {
                    'fecha': date,
                    'sorteo_id': int(draw_id),
                    'modalidad': modal,
                    'n1': int(numbers[0]), 'n2': int(numbers[1]), 'n3': int(numbers[2]),
                    'n4': int(numbers[3]), 'n5': int(numbers[4]), 'n6': int(numbers[5])
                }
                guardar_sorteo(row)
                
                # Add to JSON structure
                key = "tradicional"
                if "SEGUNDA" in modal: key = "laSegunda"
                elif "REVANCHA" in modal: key = "revancha"
                elif "SIEMPRE" in modal: key = "siempreSale"
                
                current_draw_data["modes"][key] = [int(n) for n in numbers]
        
        # Save the FIRST valid draw found (latest) to JSON
        if latest_draw_json is None and current_draw_data["modes"]:
            latest_draw_json = current_draw_data
            save_to_json(latest_draw_json)
        
        time.sleep(0.5)

    print("Scraping completed.")

if __name__ == "__main__":
    main()

