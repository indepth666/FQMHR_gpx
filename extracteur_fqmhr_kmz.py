import requests
import re

MAP_PAGE_URL = "https://www.fqmhr.qc.ca/content/map/map.html?v2023"
OUTPUT_FILE = "kmz_urls.txt"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/113.0.0.0 Safari/537.36"
}

def extract_kmz_from_map_page():
    print(f"🌐 Téléchargement de la page : {MAP_PAGE_URL}")
    try:
        response = requests.get(MAP_PAGE_URL, headers=HEADERS)
        response.raise_for_status()
    except Exception as e:
        print(f"❌ Erreur : {e}")
        return []

    content = response.text

    # Recherche de toutes les URL contenant un fichier KMZ (ex. dans les KmlOverlayService)
    matches = re.findall(r'https:\/\/www\.fqmhr\.qc\.ca\/content\/map\/kmz2025\/[^"]+?\.kmz', content)
    unique_links = sorted(set(matches))

    with open(OUTPUT_FILE, "w") as f:
        for link in unique_links:
            f.write(link + "\n")

    print(f"✅ {len(unique_links)} lien(s) KMZ trouvés et sauvegardés dans {OUTPUT_FILE}")
    return unique_links

if __name__ == "__main__":
    extract_kmz_from_map_page()
