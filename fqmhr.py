import argparse
import shutil
import zipfile
from pathlib import Path
import re

import requests
from lxml import etree

MAP_PAGE_URL = "https://www.fqmhr.qc.ca/content/map/map.html?v2023"
KMZ_URL_PATTERN = re.compile(
    r'https://www\.fqmhr\.qc\.ca/content/map/kmz\d{4}/[^"]+?\.kmz'
)
KMZ_LIST = Path("kmz_urls.txt")
DOWNLOADS_DIR = Path("downloads")
CONVERTED_DIR = Path("converted")
KML_NAMESPACE = {"kml": "http://www.opengis.net/kml/2.2"}
GPX_NAMESPACE = "http://www.topografix.com/GPX/1/1"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/113.0.0.0 Safari/537.36",
}


def ensure_output_directories() -> None:
    DOWNLOADS_DIR.mkdir(exist_ok=True)
    CONVERTED_DIR.mkdir(exist_ok=True)


def fetch_map_page() -> str | None:
    print(f"Chargement de la page FQMHR: {MAP_PAGE_URL}")
    try:
        response = requests.get(MAP_PAGE_URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
    except requests.RequestException as exc:
        print(f"Erreur de connexion: {exc}")
        return None

    return response.text


def extract_kmz_links(content: str) -> list[str]:
    return sorted(set(KMZ_URL_PATTERN.findall(content)))


def save_links(links: list[str], output_file: Path = KMZ_LIST) -> bool:
    try:
        output_file.write_text(
            "\n".join(links) + ("\n" if links else ""),
            encoding="utf-8",
        )
    except OSError as exc:
        print(f"Erreur d'écriture: {exc}")
        return False

    return True


def download_kmz(url: str) -> Path:
    path = DOWNLOADS_DIR / Path(url).name
    if path.exists():
        print(f"Fichier déjà présent, téléchargement ignoré: {path.name}")
        return path

    print(f"Téléchargement: {path.name}")
    try:
        response = requests.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        path.write_bytes(response.content)
    except requests.RequestException as exc:
        print(f"Erreur de téléchargement pour {path.name}: {exc}")
        raise

    return path


def extract_kml(kmz_path: Path) -> Path | None:
    try:
        with zipfile.ZipFile(kmz_path, "r") as zip_ref:
            for archived_name in zip_ref.namelist():
                if archived_name.endswith(".kml"):
                    kml_path = DOWNLOADS_DIR / f"{kmz_path.stem}.kml"
                    with zip_ref.open(archived_name) as source, kml_path.open("wb") as target:
                        target.write(source.read())
                    return kml_path
    except zipfile.BadZipFile as exc:
        print(f"Archive KMZ invalide: {kmz_path} ({exc})")
    except OSError as exc:
        print(f"Erreur d'E/S sur {kmz_path}: {exc}")

    return None


def iter_valid_coordinates(raw_coordinates: str):
    for coord in raw_coordinates.strip().split():
        try:
            lon, lat, *_ = coord.split(",")
            float(lat)
            float(lon)
        except (ValueError, IndexError):
            print(f"Coordonnée ignorée car invalide: {coord}")
            continue
        yield lat, lon


def convert_kml_to_gpx(kml_path: Path) -> Path | None:
    print(f"Conversion: {kml_path.name}")
    parser = etree.XMLParser(recover=True)
    try:
        tree = etree.parse(kml_path, parser=parser)
    except etree.XMLSyntaxError as exc:
        print(f"Erreur de syntaxe XML: {exc}")
        return None
    except OSError as exc:
        print(f"Erreur de lecture fichier: {exc}")
        return None

    gpx = etree.Element(
        "gpx",
        {
            "version": "1.1",
            "creator": "FQMHR Converter",
            "xmlns": GPX_NAMESPACE,
        },
    )
    has_track = False

    for placemark in tree.xpath("//kml:Placemark", namespaces=KML_NAMESPACE):
        name = placemark.find("kml:name", KML_NAMESPACE)
        coordinates = placemark.find(".//kml:coordinates", KML_NAMESPACE)
        if coordinates is None or not coordinates.text:
            continue

        trk = etree.SubElement(gpx, "trk")
        trkname = etree.SubElement(trk, "name")
        trkname.text = name.text if name is not None else "Sans nom"
        trkseg = etree.SubElement(trk, "trkseg")

        point_count = 0
        for lat, lon in iter_valid_coordinates(coordinates.text):
            etree.SubElement(trkseg, "trkpt", lat=lat, lon=lon)
            point_count += 1

        if point_count == 0:
            gpx.remove(trk)
            continue

        has_track = True

    if not has_track:
        print(f"Aucun tracé exploitable trouvé dans {kml_path.name}")
        return None

    out_path = CONVERTED_DIR / f"fqmhr_{kml_path.stem}.gpx"
    try:
        out_path.write_bytes(
            etree.tostring(gpx, pretty_print=True, xml_declaration=True, encoding="UTF-8")
        )
        print(f"GPX écrit: {out_path}")
    except OSError as exc:
        print(f"Erreur d'écriture GPX: {exc}")
        return None
    finally:
        try:
            kml_path.unlink()
        except OSError:
            pass

    return out_path


def run() -> int:
    ensure_output_directories()

    content = fetch_map_page()
    if content is None:
        return 1

    urls = extract_kmz_links(content)
    if not save_links(urls):
        return 1

    if not urls:
        print("Aucun lien KMZ trouvé sur la page.")
        return 1

    print(f"{len(urls)} fichier(s) KMZ trouvé(s).")
    print("Début du traitement.")

    success_count = 0
    for index, url in enumerate(urls, start=1):
        file_name = Path(url).name
        print(f"[{index}/{len(urls)}] {file_name}")
        try:
            kmz = download_kmz(url)
            kml = extract_kml(kmz)
            if kml is None:
                print(f"Aucun fichier KML trouvé dans {kmz.name}")
                continue
            if convert_kml_to_gpx(kml) is not None:
                success_count += 1
        except Exception as exc:
            print(f"Échec du traitement pour {file_name}: {exc}")

    print(f"Traitement terminé: {success_count}/{len(urls)} fichier(s) converti(s).")
    return 0 if success_count else 1


def clean() -> int:
    for path in (KMZ_LIST, DOWNLOADS_DIR, CONVERTED_DIR):
        if not path.exists():
            continue
        if path.is_dir():
            shutil.rmtree(path)
        else:
            path.unlink()
        print(f"Supprimé: {path}")
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extrait les cartes KMZ FQMHR et les convertit en GPX."
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Supprime les fichiers générés au lieu de lancer l'extraction.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.clean:
        return clean()
    return run()


if __name__ == "__main__":
    raise SystemExit(main())
