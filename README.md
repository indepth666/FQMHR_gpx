# FQMHR vers GPX

Un seul script, un seul usage: récupérer les KMZ de la FQMHR et sortir des GPX.

## Installation

```bash
pip install -r requirements.txt
```

## Utilisation

Lancer tout le pipeline :

```bash
python fqmhr.py
```

Nettoyer les fichiers générés :

```bash
python fqmhr.py --clean
```

## Fichiers générés

- `kmz_urls.txt`
- `downloads/`
- `converted/`

## Source

Les cartes sont récupérées depuis :
https://www.fqmhr.qc.ca/content/map/map.html?v2023
