
import requests
from bs4 import BeautifulSoup

url = "https://www.quini-6-resultados.com.ar/quini6/sorteo-3330-del-dia-14-12-2025.htm"
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Print the header containing the draw number and date
    header = soup.find(string=lambda text: text and "Sorteo Nro." in text)
    if header:
        print("Header found:", header.strip())
        print("Header parent tag:", header.parent.name)
        print("Header parent classes:", header.parent.get('class'))
    else:
        print("Header NOT found")

    # Inspect "Tradicional" section
    modality = soup.find(string=lambda text: text and "TRADICIONAL" in text.upper())
    if modality:
        print(f"\nModality 'TRADICIONAL' found in: {modality.parent.name}")
        # Print the next few elements to see where the numbers are
        curr = modality.parent
        for _ in range(3):
            curr = curr.find_next()
            if curr:
                print(f"Next element: {curr.name} | Class: {curr.get('class')} | Text: {curr.get_text(strip=True)[:50]}")
    else:
        print("Modality 'TRADICIONAL' NOT found")

except Exception as e:
    print(f"Error: {e}")
