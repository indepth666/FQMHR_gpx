import os
import zipfile
import requests
from lxml import etree

# Dossiers de sortie
os.makedirs("downloads", exist_ok=True)
os.makedirs("converted", exist_ok=True)

KMZ_LIST = "kmz_urls.txt"

def download_kmz(url):
    name = os.path.basename(url)
    path = os.path.join("downloads", name)
    print(f"📥 Téléchargement : {name}")
    r = requests.get(url)
    with open(path, "wb") as f:
        f.write(r.content)
    return path

def extract_kml(kmz_path):
    with zipfile.ZipFile(kmz_path, 'r') as zip_ref:
        for file in zip_ref.namelist():
            if file.endswith('.kml'):
                kml_name = os.path.splitext(os.path.basename(kmz_path))[0] + ".kml"
                kml_path = os.path.join("downloads", kml_name)
                with zip_ref.open(file) as source, open(kml_path, "wb") as target:
                    target.write(source.read())
                return kml_path
    return None

def convert_kml_to_gpx(kml_path):
    print(f"🔄 Conversion : {kml_path}")
    parser = etree.XMLParser(recover=True)
    try:
        tree = etree.parse(kml_path, parser=parser)
    except Exception as e:
        print(f"❌ Erreur XML : {e}")
        return

    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    gpx = etree.Element("gpx", version="1.1", creator="FQMHR Converter")

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
                    lon, lat, *_ = coord.split(",")
                    etree.SubElement(trkseg, "trkpt", lat=lat, lon=lon)
                except:
                    continue

    base_name = os.path.splitext(os.path.basename(kml_path))[0]
    out_path = os.path.join("converted", "fqmhr_" + base_name + ".gpx")
    with open(out_path, "wb") as f:
        f.write(etree.tostring(gpx, pretty_print=True, xml_declaration=True, encoding="UTF-8"))
    print(f"✅ Export GPX : {out_path}")

def process_all_kmz():
    with open(KMZ_LIST, "r") as f:
        urls = [line.strip() for line in f if line.strip()]

    for url in urls:
        try:
            kmz = download_kmz(url)
            kml = extract_kml(kmz)
            if kml:
                convert_kml_to_gpx(kml)
            else:
                print(f"⚠️ Aucun .kml trouvé dans {kmz}")
        except Exception as e:
            print(f"❌ Erreur avec {url} : {e}")

if __name__ == "__main__":
    process_all_kmz()
