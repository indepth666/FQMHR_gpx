# Extracteur FQMHR KMZ vers GPX

Outil d'extraction et de conversion automatique des cartes KMZ de la Fédération québécoise de motocyclisme hors route (FQMHR) vers le format GPX.

## Description

Ce projet permet de télécharger automatiquement les cartes de sentiers de la FQMHR depuis le site officiel de la FQMHR et de les convertir au format GPX pour utilisation dans vos applications GPS favorites.

## Fonctionnalités

- Extraction automatique des URLs KMZ depuis le site FQMHR
- Téléchargement des fichiers KMZ
- Conversion des données KML vers le format GPX standard
- Traitement par lot de toutes les cartes disponibles
- Gestion d'erreurs robuste

## Installation

### Prérequis

- Python 3.6 ou supérieur
- pip (gestionnaire de paquets Python)

### Dépendances

Installez les dépendances requises :

```bash
pip install requests lxml
```

## Utilisation

### Processus complet

1. **Extraction des URLs** :
   ```bash
   python extracteur_fqmhr_kmz.py
   ```

2. **Téléchargement et conversion** :
   ```bash
   python kmz_to_gpx.py
   ```

3. **Exécution complète en une commande** :
   ```bash
   python extracteur_fqmhr_kmz.py && python kmz_to_gpx.py
   ```

## Structure du projet

```
fqmhr_extracteur/
├── extracteur_fqmhr_kmz.py    # Script d'extraction des URLs
├── kmz_to_gpx.py              # Script de conversion KMZ vers GPX
├── downloads/                 # Fichiers KMZ téléchargés
├── converted/                 # Fichiers GPX convertis
├── fqmhr_gpx/                 # Sauvegarde des fichiers GPX
└── kmz_urls.txt              # Liste des URLs extraites
```

## Formats supportés

- **Entrée** : Fichiers KMZ (Keyhole Markup Language Zipped)
- **Sortie** : Fichiers GPX (GPS Exchange Format) version 1.1

## Fonctionnement

1. Le script `extracteur_fqmhr_kmz.py` analyse la page web de la FQMHR
2. Il extrait automatiquement tous les liens vers les fichiers KMZ
3. Les URLs sont sauvegardées dans `kmz_urls.txt`
4. Le script `kmz_to_gpx.py` lit ce fichier et télécharge chaque KMZ
5. Chaque KMZ est décompressé pour extraire le fichier KML
6. Les données KML sont converties au format GPX standard
7. Les fichiers GPX sont sauvegardés avec le préfixe "fqmhr_"

## Source des données

Les cartes sont récupérées depuis la page officielle : https://www.fqmhr.qc.ca/content/map/map.html?v2023

## Gestion d'erreurs

- Chaque fichier est traité indépendamment
- Les erreurs de téléchargement sont affichées mais n'interrompent pas le processus
- Le parsing XML utilise un mode de récupération en cas d'erreur

## Licence

Ce projet est destiné à un usage personnel et éducatif. Respectez les conditions d'utilisation du site FQMHR.
