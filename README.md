# CheckIt.AI - Fake News Killer

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Project P12](https://img.shields.io/badge/projet-P12-Formation_IA-orange)

## 📋 Description du projet

Projet d'extraction de données multimodales (texte + images) depuis diverses sources web pour alimenter un détecteur de Fake News. L'objectif est d'industrialiser l'acquisition de données avec un pipeline ETL complet orchestré par Apache Airflow.

Ce projet fait partie de la formation IA et constitue le Projet 12 (P12) du parcours de formation.

## 🛡️ Badges et Métriques

### Qualité du code
- **Version Python**: Python 3.10+ avec Pixi
- **Base de données**: SQLite intégrée
- **Classification**: Opinion vs Désinformation

### Métriques du pipeline
- **Sources configurées**: 5 RSS + 3 APIs + BeautifulSoup
- **Extraction**: RSS ✅, Reddit ✅, NewsAPI.ai ✅, BeautifulSoup ✅, Selenium ⚠️
- **Total articles par exécution**: ~125
- **Multimodalité**: ~80% des articles contiennent une image
- **Classification Opinion/Désinformation**: ✅ Implémenté

---

## 🏗️ Environnement requis pour la démo

### Minimal (pour valider le core)

```yaml
# Configuration minimale du pod de démo
environment:
  python: "3.10"
  package_manager: pixi
  
# Dépendances requises (dans pixi.toml)
dependencies:
  - python = "3.10.*"
  - beautifulsoup4
  - requests
  - lxml
  - pyyaml
  - pandas
  - streamlit
  - airflow
  - selenium
```

### Complet (pour valider tout)

```yaml
# Configuration complète pour validation totale
environment:
  python: "3.10"
  package_manager: pixi
  database: sqlite3  # Inclus dans Python

# Packages supplémentaires
dependencies:
  - python = "3.10.*"
  - beautifulsoup4 = "*"
  - selenium = "*"
  - requests = "*"
  - lxml = "*"
  - pyyaml = "*"
  - airflow = "*"
  - streamlit = "*"
  - pandas = "*"
  - pytest = "*"
  - ruff = "*"

# Optionnel: Chrome pour Selenium
# Installé séparément si disponible
```

### Commandes de validation

```bash
# 1. Installation des dépendances
cd /mnt/prod
pixi install

# 2. Vérification Python
pixi run python --version

# 3. Test extraction RSS
pixi run python -c "from src.extraction.rss_fetcher import RSSFetcher; print(RSSFetcher().fetch_all(limit_per_feed=2))"

# 4. Test pipeline complet
pixi run python src/extraction/main.py

# 5. Test transformation + classification + DB
pixi run python -c "
from src.transformation.pipeline import TransformationPipeline
p = TransformationPipeline(use_db=True)
# Transformer les données extraites
"

# 6. Test Dashboard
pixi run streamlit run dashboard/app.py --server.headless true
```

---

## 🎯 Fonctionnalités principales

| Fonctionnalité | Status | Fichier |
|----------------|--------|---------|
| Extraction RSS (5 sources) | ✅ | `src/extraction/rss_fetcher.py` |
| Extraction API (NewsAPI, Reddit, HackerNews) | ✅ | `src/extraction/api_client.py` |
| Scraping BeautifulSoup | ✅ | `src/extraction/scraper_bs4.py` |
| Scraping Selenium | ⚠️ | `src/extraction/scraper_selenium.py` |
| Nettoyage/Normalisation | ✅ | `src/transformation/cleaner.py` |
| Classification Opinion/Désinformation | ✅ | `src/transformation/classifier.py` |
| Base de données SQLite | ✅ | `src/transformation/database.py` |
| Pipeline ETL | ✅ | `src/transformation/pipeline.py` |
| MCD Mermaid | ✅ | `src/models/schema.mmd` |
| DAG Airflow | ✅ | `dags/fakenews_pipeline.py` |
| Dashboard Streamlit | ✅ | `dashboard/app.py` |

---

## 📁 Structure du projet

```
checkit-ai/
├── docs/
│   ├── exploration_sources.md      # Livrable 1
│   ├── selenium_guide.md            # Guide Selenium
│   ├── soutenance_slides.md          # Slides présentation
│   ├── soutenance_notes.md           # Notes orateur
│   └── soutenance_qa.md             # Q&R préparation
├── src/
│   ├── extraction/
│   │   ├── api_client.py            # APIs (Reddit, NewsAPI.ai, HackerNews)
│   │   ├── rss_fetcher.py           # Flux RSS
│   │   ├── scraper_bs4.py           # BeautifulSoup
│   │   ├── scraper_selenium.py      # Selenium
│   │   └── main.py                   # CLI extraction
│   ├── transformation/
│   │   ├── cleaner.py               # Nettoyage données
│   │   ├── classifier.py            # Classification Opinion/Désinformation
│   │   ├── database.py              # Base SQLite
│   │   └── pipeline.py              # Pipeline ETL complet
│   └── models/
│       └── schema.mmd               # MCD Mermaid
├── dags/
│   └── fakenews_pipeline.py         # DAG Airflow
├── dashboard/
│   ├── app.py                       # Dashboard Streamlit
│   └── requirements.txt
├── data/
│   ├── raw/                          # Données brutes
│   ├── processed/                   # Données transformées
│   └── fakenews.db                  # Base SQLite
├── pixi.toml
└── README.md
```

---

## 🚀 Utilisation

### Extraction de données
```bash
# Extraire depuis toutes les sources
pixi run python src/extraction/main.py

# Avec scraping BeautifulSoup
pixi run python src/extraction/main.py --scraping
```

### Transformation ETL
```bash
# Transformer + classifier + sauvegarder en DB
pixi run python src/transformation/pipeline.py --file extracted_*.json
```

### Dashboard
```bash
pixi run streamlit run dashboard/app.py
```

---

## 📊 Livrables (5/5)

1. **Rapport exploration** - `docs/exploration_sources.md`
2. **Scripts extraction** - `src/extraction/`
3. **Pipeline + MCD** - `src/transformation/` + `src/models/`
4. **DAG Airflow** - `dags/fakenews_pipeline.py`
5. **Dashboard** - `dashboard/app.py`

---

## 🔧 Dépannage Selenium

Si Selenium échoue (Chrome non installé), le code fonctionne quand même avec BeautifulSoup.

Pour activer Selenium localement, voir `docs/selenium_guide.md`.

---

## ✅ Validation complète

Pour valider que tout fonctionne :

```bash
# Test 1: Extraction
pixi run python src/extraction/main.py

# Test 2: Transformation avec DB
pixi run python -c "
from src.transformation.pipeline import TransformationPipeline
from src.transformation.database import DatabaseManager
p = TransformationPipeline(use_db=True)
d = DatabaseManager()
print(d.get_statistics())
"

# Test 3: Classification
pixi run python -c "
from src.transformation.classifier import ContentClassifier
c = ContentClassifier()
print(c.classify({'title': 'Test', 'description': 'Test', 'source': 'le_monde', 'content': ''}))
"

# Test 4: Dashboard
timeout 5 pixi run streamlit run dashboard/app.py --server.headless true
```

---

## 📄 Licence

MIT License