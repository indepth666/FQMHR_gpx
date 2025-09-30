from setuptools import setup, find_packages

def read_requirements():
    """Read requirements from requirements.txt file."""
    try:
        with open('requirements.txt', 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    except FileNotFoundError:
        return []

setup(
    name="fqmhr-extracteur",
    version="1.0.0",
    author="Hugo",
    author_email="",
    description="Extracteur de cartes KMZ/GPX pour la Fédération québécoise de motocyclisme hors route",
    long_description="Outil d'extraction automatique des cartes KMZ depuis le site FQMHR et conversion au format GPX. Télécharge les cartes officielles et les convertit pour utilisation dans des applications GPS tierces.",
    long_description_content_type="text/plain",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: GIS",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'fqmhr-extract=extracteur_fqmhr_kmz:extract_kmz_from_map_page',
            'fqmhr-convert=kmz_to_gpx:process_all_kmz',
        ],
    },
    include_package_data=True,
    package_data={
        '': ['*.md', '*.txt', '*.sh'],
    },
)