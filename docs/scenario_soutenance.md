# SCÉNARIO DE SOUTENANCE - P12 CheckIt.AI
## Guide complet de présentation (~15-20 min)

---

## PRÉPARATION (AVANT LA SOUTENANCE)

### Checklist technique
- [ ] Ordonnanceur ouvert avec slides
- [ ] Terminal prêt avec les commandes
- [ ] Données de démo pré-générées dans `/mnt/prod/data/`
- [ ] Dashboard Streamlit lancé en arrière-plan

### Scripts à préparer
```bash
# Terminal 1 - Générer des données de démo
cd /mnt/prod && pixi run python src/extraction/main.py

# Terminal 2 - Dashboard (lancer avant la soutenance)
cd /mnt/prod && pixi run streamlit run dashboard/app.py --server.port 8501
```

---

## PHASE 1 : INTRODUCTION
**⏱️ Durée : 2-3 minutes**

---

### Slide 1 : Titre
**Temps : ~30 secondes**

> "Bonjour à toutes et à tous,
> 
> Je m'appelle [PRÉNOM] et je vais vous présenter le Projet 12 de la Formation IA : **CheckIt.AI**.
> 
> C'est un pipeline d'extraction de données multimodales pour un détecteur de Fake News."

**Transition :** "Laissez-moi vous expliquer le contexte..."

---

### Slide 2 : Contexte et enjeux
**Temps : ~1 minute**

> "Le contexte est simple : un détecteur de fake news a besoin de données d'entraînement.
> 
> **Le problème ?** Il faut des données variées, en grand volume, et de qualité.
> 
> **Ma mission ?** Industrialiser l'acquisition de ces données depuis le web.
> 
> La contrainte principale : les données doivent être **multimodales** — c'est-à-dire texte PLUS images."

**Transition :** "Pour cela, j'ai identifié plusieurs sources..."

---

### Slide 3 : Les 5 livrables
**Temps : ~1 minute**

> "Ce projet comprend **5 livrables obligatoires** :
> 
> 1. **Un rapport d'exploration** — J'ai identifié les meilleures sources de données
> 2. **Des scripts d'extraction** — 5 scripts Python (RSS, API, BeautifulSoup, Selenium)
> 3. **Un pipeline ETL** — Nettoyage, normalisation + modèle de données
> 4. **Un DAG Airflow** — L'orchestration qui automatise tout
> 5. **Un dashboard KPI** — Le monitoring avec Streamlit
> 
> Je vais vous présenter chaque livrable en détail."

**Transition :** "Commençons par le sourcing..."

---

## PHASE 2 : MISSION 1 - SOURCING & EXPLORATION
**⏱️ Durée : 3-4 minutes**

---

### Slide 4 : Sources identifiées
**Temps : ~2 minutes**

> "La première étape était d'identifier les sources de données adaptées.
> 
> J'ai évalué **3 approches** :
> 
> **1. Les APIs REST** — Les plus structurées (NewsAPI, Reddit, HackerNews)
>  Avantage : données JSON, images incluses
>  Inconvénient : nécessitent des clés API, quotas limités
> 
> **2. Les flux RSS** — Le choix optimal pour ce projet
>  Avantage : gratuits, illimités, fonctionne immédiatement
>  Inconvénient : certains sites ne proposent pas d'images
> 
> **3. Le scraping direct** — Pour les sites sans API ni RSS
>  Avantage : accès à n'importe quel site
>  Inconvénient : plus complexe, risque de blocage"

**Montrer le tableau des sources actives :**

| Source | Type | Status | Volume |
|--------|------|--------|--------|
| Le Figaro | RSS | ✅ | 10 articles |
| Le Monde | RSS | ✅ | 10 articles |
| 20 Minutes | RSS | ✅ | 10 articles |
| Euronews | RSS | ✅ | 10 articles |
| Reddit | API | ✅ | 30 posts |

**Transition :** "Maintenant, voyons comment j'ai implémenté l'extraction..."

---

### Slide 5 : Distinction Opinion vs Désinformation
**Temps : ~1 minute**

> "Un point éthique important : la distinction entre **opinion controversée** et **désinformation**.
> 
> Ce sont deux choses différentes :
> 
> - **Opinion** : Point de vue assumé, source identifiée, facts vérifiables
> - **Désinformation** : Tromperie délibérée, fausses données, source inconnue
> 
> Mon système de classification analyse ces indicateurs pour filtrer les contenus problématiques."

**Transition :** "Passons à la démo d'extraction..."

---

## PHASE 3 : MISSION 2 - INGÉNIERIE D'EXTRACTION
**⏱️ Durée : 4-5 minutes (AVEC DÉMO)**

---

### Slide 6 : Architecture d'extraction
**Temps : ~1 minute**

> "Voici comment fonctionne mon système d'extraction :
> 
> **4 scripts principaux :**
> 
> - `rss_fetcher.py` — Parse les flux RSS avec BeautifulSoup
> - `api_client.py` — Gère les appels REST (Reddit, NewsAPI, HackerNews)
> - `scraper_bs4.py` — Scraping HTML classique
> - `scraper_selenium.py` — Scraping JavaScript (cas complexes)
> 
> Tous utilisent try/except, timeout, et logs pour gérer les erreurs."

**Transition :** "Je vais vous montrer ça en action..."

---

### DÉMO 1 : Extraction RSS (Lancer dans le terminal)
**Temps : ~2 minutes**

> "Je lance l'extraction RSS depuis les 5 sources..."

```bash
cd /mnt/prod && pixi run python src/extraction/main.py
```

**Pendant l'exécution, commenter :**
> "Vous voyez : chaque source est traité séquentiellement, avec logs en temps réel.
> 
> Le système affiche : le nombre d'articles extraits par source, le temps d'exécution, et les erreurs éventuelles."

**Expliquer la sortie :**
> "Résultat : 50 articles extraits avec leurs images. Chaque article contient :
> - Titre, description, URL
> - Image (ou champ vide si pas d'image)
> - Source, date de publication"

**Transition :** "Ces données brutes doivent maintenant être nettoyées..."

---

### Slide 7 : Gestion des erreurs et robustesse
**Temps : ~1 minute**

> "Points techniques importants :
> 
> - **Timeout de 15 secondes** par requête —避免 les blocages
> - **User-Agent personnalisé** — Respècte les bonnes pratiques
> - **Fallback automatique** — Si une source échoue, on continue
> - **Logs détaillés** — Chaque erreur est logguée avec contexte"

---

## PHASE 4 : MISSION 3 - TRANSFORMATION & MODÉLISATION
**⏱️ Durée : 3-4 minutes**

---

### Slide 8 : Pipeline ETL
**Temps : ~2 minutes**

> "Une fois les données extraites, elles passent par un pipeline de transformation en 3 étapes :
> 
> **1. Nettoyage**
> - Suppression des balises HTML résiduelles
> - Suppression des URLs et caractères spéciaux
> - Normalisation du texte (minuscules, stop words)
> 
> **2. Validation**
> - Vérification du titre obligatoire
> - Détection du contenu multimodal (image présente)
> - Calcul du nombre de mots
> 
> **3. Classification**
> - Analyse Opinion vs Désinformation
> - Extraction des mots-clés
> - Marquage du type de contenu"

**Transition :** "Voici le schéma de données..."

---

### Slide 9 : Modèle Conceptuel de Données (Mermaid)
**Temps : ~1 minute**

> "J'ai conçu un modèle de données en Mermaid qui décrit la structure de la base.
> 
> **5 entités principales :**
> 
> - **ARTICLE** — Données principales (titre, contenu, image, source)
> - **SOURCE** — Provenance des données
> - **KEYWORD** — Mots-clés extraits par analyse
> - **EXTRACTION_LOG** — Historique des extractions
> - **METRICS** — KPIs calculés"

**Montrer le diagramme :**
```
ARTICLE ──a── KEYWORD
ARTICLE ──b── SOURCE
ARTICLE ──c── EXTRACTION_LOG
```

**Transition :** "Tout ce pipeline est orchestré automatiquement par Airflow..."

---

## PHASE 5 : MISSION 4 - ORCHESTRATION AIRFLOW
**⏱️ Durée : 4-5 minutes**

---

### Slide 10 : Le DAG Airflow
**Temps : ~2 minutes**

> "Le DAG Airflow est le cœur de l'automatisation.
> 
> Il s'exécute **2 fois par jour** (6h et 18h) automatiquement.
> 
> **Le flux est le suivant :**
> 
> 1. **extract_rss** — Récupère les articles des 5 flux RSS
> 2. **extract_reddit** — Récupère les posts de 3 subreddits
> 3. **merge_raw** — Fusionne toutes les données brutes
> 4. **transform** — Applique nettoyage + classification
> 5. **load** — Stocke en base de données
> 6. **calculate_kpis** — Génère les métriques"

**Montrer le diagramme du flux :**
```
[RSS]──┐
[RSS]──┤
[RSS]──┼──► [Merge] ─► [Transform] ─► [Load] ─► [KPIs]
[RSS]──┤
[Reddit]┘
```

**Points forts à mentionner :**
> "- **Exécution parallèle** : RSS et Reddit tournent en même temps
> - **Retry automatique** : 2 tentatives en cas d'erreur
> - **Logs complets** : chaque étape est logguée
> - **XCom** : transmission de données entre tâches"

**Transition :** "Voyons le monitoring..."

---

## PHASE 6 : MISSION 5 - MONITORING & QUALITÉ
**⏱️ Durée : 3-4 minutes (AVEC DÉMO)**

---

### Slide 11 : Dashboard Streamlit
**Temps : ~1 minute**

> "Le dashboard Streamlit permet de suivre les KPIs en temps réel.
> 
> **4 vues disponibles :**
> 
> 1. **KPIs** — Métriques clés avec graphiques
> 2. **Données brutes** — Visualisation des articles extraits
> 3. **Données transformées** — Articles nettoyés et classifiés
> 4. **Monitoring** — État du système et plan de suivi"

**Transition :** "Ouvrons le dashboard..."

---

### DÉMO 2 : Dashboard Streamlit
**Temps : ~2 minutes**

> "Voici le dashboard en fonctionnement..."

**Navigation dans le dashboard :**

1. **Page KPIs** — "Vous voyez : nombre d'articles extraits par source, taux de réussite, articles multimodaux..."

2. **Page Données transformées** — "Ici : articles nettoyés avec leur classification Opinion/Désinformation..."

3. **Page Monitoring** — "Le plan de monitoring avec les seuils d'alerte..."

**KPIs affichés :**
- Articles RSS : 50
- Posts Reddit : 30
- Multimodaux : 65/80
- Taux de validité : 95%

**Transition :** "Pour conclure..."

---

## PHASE 7 : CONCLUSION
**⏱️ Durée : 2-3 minutes**

---

### Slide 12 : Récapitulatif des livrables
**Temps : ~1 minute**

> "**Voici le récapitulatif des 5 livrables :**
> 
> | Livrable | Fichier | Status |
> |----------|---------|--------|
> | 1. Rapport exploration | `docs/exploration_sources.md` | ✅ |
> | 2. Scripts extraction | `src/extraction/*.py` | ✅ |
> | 3. Pipeline + MCD | `src/transformation/` + `schema.mmd` | ✅ |
> | 4. DAG Airflow | `dags/fakenews_pipeline.py` | ✅ |
> | 5. Dashboard | `dashboard/app.py` | ✅ |
> 
> **Tous les livrables sont produits et fonctionnels.**"

---

### Slide 13 : Compétences acquises
**Temps : ~1 minute**

> "Ce projet m'a permis de maîtriser :
> 
> - **Web Scraping** — BeautifulSoup, Selenium, parsing HTML/XML
> - **APIs REST** — Consumption et gestion des réponses
> - **Pipeline ETL** — Extraction, transformation, chargement
> - **Orchestration** — Apache Airflow et ses DAGs
> - **Modélisation** — Schéma conceptuel Mermaid
> - **Monitoring** — Dashboard Streamlit et KPIs
> - **Qualité de données** — Nettoyage, validation, classification"

---

### Slide 14 : Difficultés rencontrées
**Temps : ~30 secondes**

> "Les difficultés principales :
> 
> 1. **URL RSS 20 Minutes** — L'URL officielle donnait une erreur 404. J'ai dû inspecter le code source du site pour trouver la bonne URL.
> 
> 2. **Clés API** — NewsAPI et Reddit nécessitent des inscriptions. Le code est prêt, les clés ne sont juste pas livrées dans le cadre du projet.
> 
> 3. **Selenium** — Nécessite Chrome installé. Le code fonctionne avec BeautifulSoup en fallback."

---

### Slide 15 : Perspectives d'évolution
**Temps : ~30 secondes**

> "Pour aller plus loin :
> 
> - Intégrer les API complètes (avec clés)
> - Base de données PostgreSQL pour la persistance
> - Tests unitaires avec pytest
> - Déploiement sur le cloud (OKD/Kubernetes)
> - Amélioration du classifier avec du Machine Learning"

---

### Slide 16 : Fin
**Temps : ~30 secondes**

> "**Merci pour votre attention !**
> 
> Je suis prêt à répondre à vos questions."

---

## ANNEXE : QUESTIONS PROBABLES

### Q: Pourquoi RSS et pas API ?
> "RSS est gratuit, illimité, et fonctionne sans configuration. C'est le choix optimal pour un POC. Les APIs sont prêtes si besoin."

### Q: Comment gérez-vous les erreurs ?
> "Chaque script a try/except avec logging. Airflow gère les retries automatiquement avec un délai de 5 minutes."

### Q: Différence Opinion vs Désinformation ?
> "Opinion = source connue, intention assumée. Désinformation = délibérément trompeuse, fausses données, source non identifiée."

### Q: Le code est-il production-ready ?
> "Il est fonctionnel pour un POC. Pour la prod : il faudrait tests unitaires, base de données robuste, et monitoring avancé type Grafana."

### Q: Pourquoi Streamlit et pas autre chose ?
> "Streamlit est demandé explicitement dans les spécifications, et c'est l'outil le plus simple pour un dashboard Python intégré."

### Q: Comment ajouter une nouvelle source ?
> "C'est很简单 : ajouter une méthode dans api_client.py ou rss_fetcher.py, et l'appeler dans main.py. La modularité permet ça."

---

## TIMING TOTAL

| Phase | Durée |
|-------|-------|
| Introduction | 2-3 min |
| Mission 1 (Sourcing) | 3-4 min |
| Mission 2 (Extraction) + démo | 4-5 min |
| Mission 3 (Transformation) | 3-4 min |
| Mission 4 (Airflow) | 4-5 min |
| Mission 5 (Dashboard) + démo | 3-4 min |
| Conclusion | 2-3 min |
| **TOTAL** | **~18-25 min** |

---

## COMMANDES À GARDER SOUS LA MAIN

```bash
# Générer des données de démo
cd /mnt/prod && pixi run python src/extraction/main.py

# Transformer les données
cd /mnt/prod && pixi run python src/transformation/pipeline.py

# Lancer le dashboard
cd /mnt/prod && pixi run streamlit run dashboard/app.py --server.port 8501

# Tester une extraction spécifique
cd /mnt/prod && pixi run python -c "from src.extraction.rss_fetcher import RSSFetcher; f = RSSFetcher(); print(len(f.fetch_all(limit_per_feed=3)))"
```
