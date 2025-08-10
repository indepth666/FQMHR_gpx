import os
import zipfile
import requests
from lxml import etree

# Constantes
KMZ_LIST = "kmz_urls.txt"
DOWNLOADS_DIR = "downloads"
CONVERTED_DIR = "converted"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/113.0.0.0 Safari/537.36"
}

# Dossiers de sortie
os.makedirs(DOWNLOADS_DIR, exist_ok=True)
os.makedirs(CONVERTED_DIR, exist_ok=True)

def download_kmz(url):
    name = os.path.basename(url)
    path = os.path.join(DOWNLOADS_DIR, name)
    
    # Vérifier si le fichier existe déjà
    if os.path.exists(path):
        print(f"⏭️ Fichier déjà présent : {name}")
        return path
        
    print(f"📥 Téléchargement : {name}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        r.raise_for_status()
        with open(path, "wb") as f:
            f.write(r.content)
        return path
    except requests.RequestException as e:
        print(f"❌ Erreur de téléchargement {name} : {e}")
        raise

def extract_kml(kmz_path):
    try:
        with zipfile.ZipFile(kmz_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.endswith('.kml'):
                    kml_name = os.path.splitext(os.path.basename(kmz_path))[0] + ".kml"
                    kml_path = os.path.join(DOWNLOADS_DIR, kml_name)
                    with zip_ref.open(file) as source, open(kml_path, "wb") as target:
                        target.write(source.read())
                    return kml_path
    except zipfile.BadZipFile as e:
        print(f"❌ Fichier ZIP corrompu {kmz_path} : {e}")
    except IOError as e:
        print(f"❌ Erreur d'E/S {kmz_path} : {e}")
    return None

def convert_kml_to_gpx(kml_path):
    print(f"🔄 Conversion : {kml_path}")
    parser = etree.XMLParser(recover=True)
    try:
        tree = etree.parse(kml_path, parser=parser)
    except etree.XMLSyntaxError as e:
        print(f"❌ Erreur de syntaxe XML : {e}")
        return
    except IOError as e:
        print(f"❌ Erreur de lecture fichier : {e}")
        return

    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    gpx_attrs = {
        "version": "1.1",
        "creator": "FQMHR Converter",
        "xmlns": "http://www.topografix.com/GPX/1/1"
    }
    gpx = etree.Element("gpx", gpx_attrs)

    for placemark in tree.xpath("//kml:Placemark", namespaces=ns):
        name = placemark.find("kml:name", ns)
        coords = placemark.find(".//kml:coordinates", ns)
        if coords is not None:
            trk = etree.SubElement(gpx, "trk")
            trkname = etree.SubElement(trk, "name")
            trkname.text = name.text if name is not None else "Sans nom"
            trkseg = etree.SubElement(trk, "trkseg")
            for coord in coords.text.strip().split():
                try:
                    parts = coord.split(",")
                    if len(parts) >= 2:
                        lon, lat = parts[0], parts[1]
                        # Valider les coordonnées
                        float(lat)
                        float(lon)
                        etree.SubElement(trkseg, "trkpt", lat=lat, lon=lon)
                except (ValueError, IndexError):
                    print(f"⚠️ Coordonnée invalide ignorée : {coord}")
                    continue

    base_name = os.path.splitext(os.path.basename(kml_path))[0]
    out_path = os.path.join(CONVERTED_DIR, "fqmhr_" + base_name + ".gpx")
    try:
        with open(out_path, "wb") as f:
            f.write(etree.tostring(gpx, pretty_print=True, xml_declaration=True, encoding="UTF-8"))
        print(f"✅ Export GPX : {out_path}")
        
        # Nettoyer le fichier KML temporaire
        try:
            os.remove(kml_path)
            print(f"🧹 Fichier temporaire supprimé : {kml_path}")
        except OSError:
            pass
    except IOError as e:
        print(f"❌ Erreur d'écriture GPX : {e}")

def process_all_kmz():
    # Vérifier que le fichier d'URLs existe
    if not os.path.exists(KMZ_LIST):
        print(f"❌ Fichier {KMZ_LIST} non trouvé. Exécutez d'abord extracteur_fqmhr_kmz.py")
        return
    
    try:
        with open(KMZ_LIST, "r", encoding="utf-8") as f:
            urls = [line.strip() for line in f if line.strip()]
    except IOError as e:
        print(f"❌ Erreur de lecture {KMZ_LIST} : {e}")
        return
        
    if not urls:
        print(f"⚠️ Aucune URL trouvée dans {KMZ_LIST}")
        return
    
    print(f"🚀 Traitement de {len(urls)} fichier(s) KMZ")

    for i, url in enumerate(urls, 1):
        print(f"[{i}/{len(urls)}] Traitement : {os.path.basename(url)}")
        try:
            kmz = download_kmz(url)
            kml = extract_kml(kmz)
            if kml:
                convert_kml_to_gpx(kml)
            else:
                print(f"⚠️ Aucun .kml trouvé dans {kmz}")
        except Exception as e:
            print(f"❌ Erreur avec {url} : {e}")
    
    print("✅ Traitement terminé")

if __name__ == "__main__":
    process_all_kmz()
