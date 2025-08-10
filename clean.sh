#!/bin/bash

echo "🧹 Nettoyage des fichiers générés..."

# Supprimer le fichier des URLs
if [ -f "kmz_urls.txt" ]; then
    rm "kmz_urls.txt"
    echo "✅ kmz_urls.txt supprimé"
fi

# Supprimer le dossier downloads et tout son contenu
if [ -d "downloads" ]; then
    rm -rf "downloads"
    echo "✅ Dossier downloads/ supprimé"
fi

# Supprimer le dossier converted et tout son contenu
if [ -d "converted" ]; then
    rm -rf "converted"
    echo "✅ Dossier converted/ supprimé"
fi

# Optionnel : supprimer aussi le dossier de sauvegarde fqmhr_gpx
read -p "🤔 Supprimer aussi le dossier fqmhr_gpx/ ? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if [ -d "fqmhr_gpx" ]; then
        rm -rf "fqmhr_gpx"
        echo "✅ Dossier fqmhr_gpx/ supprimé"
    fi
fi

echo "🎯 Nettoyage terminé !"
echo ""
echo "📋 Pour regénérer les fichiers :"
echo "   python extracteur_fqmhr_kmz.py && python kmz_to_gpx.py"