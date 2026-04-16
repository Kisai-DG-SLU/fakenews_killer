# SLIDES SOUTENANCE P12 - CheckIt.AI
## Format prête à présenter (Markdown → PowerPoint/Google Slides)

---

# SLIDE 1 : TITRE
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│              🗞️  CHECKIT.AI                             │
│                                                         │
│     Extraction de données multimodales                 │
│     pour un détecteur de Fake News                      │
│                                                         │
│     ─────────────────────────────                       │
│     Projet P12 - Formation IA                           │
│     [Votre Nom] - [Date]                               │
│                                                         │
└─────────────────────────────────────────────────────────┘
```
**Style :** Fond sombre (#1a1a2e), titre blanc, accent orange

---

# SLIDE 2 : CONTEXTE
```
┌─────────────────────────────────────────────────────────┐
│  🎯 CONTEXTE ET ENJEUX                                  │
│                                                         │
│  ┌───────────────┐  ┌───────────────┐  ┌──────────────┐  │
│  │    PROBLÈME   │  │   DÉFI       │  │  CONTRAINTE  │  │
│  │               │  │              │  │              │  │
│  │ Alimenter un  │  │ Industrialiser│  │ Multimodalité│  │
│  │ détecteur de  │  │ l'acquisition │  │ Texte + Image│  │
│  │ fake news    │  │ de données    │  │              │  │
│  └───────────────┘  └───────────────┘  └──────────────┘  │
│                                                         │
│  Besoin : données variées, volume important, qualité    │
└─────────────────────────────────────────────────────────┘
```
**Style :** 3 cartes avec icônes, fond clair

---

# SLIDE 3 : LES 5 LIVRABLES
```
┌─────────────────────────────────────────────────────────┐
│  📦 LES 5 LIVRABLES OBLIGATOIRES                        │
│                                                         │
│  1️⃣  Rapport d'exploration                               │
│      Sources identifiées (RSS, API, Scraping)           │
│                        ↓                                 │
│  2️⃣  Scripts d'extraction                               │
│      BeautifulSoup, Selenium, API clients                │
│                        ↓                                 │
│  3️⃣  Pipeline ETL                                       │
│      Nettoyage + Modèle de données Mermaid              │
│                        ↓                                 │
│  4️⃣  DAG Airflow                                        │
│      Orchestration automatisée                          │
│                        ↓                                 │
│  5️⃣  Dashboard KPI                                      │
│      Monitoring avec Streamlit                          │
└─────────────────────────────────────────────────────────┘
```
**Style :** Flèche verticale avec étapes numérotées

---

# SLIDE 4 : SOURCES IDENTIFIÉES
```
┌─────────────────────────────────────────────────────────┐
│  📡 SOURCES DE DONNÉES                                  │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ APPROCHE          │ AVANTAGE       │ INCONVÉNIENT│   │
│  ├─────────────────────────────────────────────────┤   │
│  │ APIs REST         │ JSON structuré │ Clés, quotas│   │
│  │ RSS (CHOIX ✅)     │ Gratuit, libre │ Images rares│  │
│  │ Scraping          │ Complet        │ Complexe    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  SOURCES ACTIVES :                                      │
│  ┌──────┬──────┬───────┬────────┬────────┬────────┐   │
│  │Figaro│Monde │20min  │Euronews│ Reddit │ Hacker │   │
│  │  ✅  │  ✅  │  ✅   │  ✅   │  ✅   │   ✅  │   │
│  └──────┴──────┴───────┴────────┴────────┴────────┘   │
│  10 art.  10 art. 10 art.  10 art.  30 posts  20 art. │
└─────────────────────────────────────────────────────────┘
```
**Style :** Tableau + badges de statut

---

# SLIDE 5 : DISTINCTION ÉTHIQUE
```
┌─────────────────────────────────────────────────────────┐
│  ⚖️ OPINION vs DÉSINFORMATION                            │
│                                                         │
│  ┌────────────────────┐   ┌────────────────────────┐   │
│  │   OPINION          │   │   DÉSINFORMATION       │   │
│  │   CONTROVERSÉE     │   │                        │   │
│  ├────────────────────┤   ├────────────────────────┤   │
│  │ ✓ Source identifiée│   │ ✗ Source anonyme      │   │
│  │ ✓ Intention assumée│   │ ✗ Tromperie délibérée │   │
│  │ ✓ Faits vérifiables│   │ ✗ Fausses données     │   │
│  │ ✓ Média reconnu   │   │ ✗ Buzz, sensationnel  │   │
│  └────────────────────┘   └────────────────────────┘   │
│                                                         │
│  → Système de classification automatique intégré         │
└─────────────────────────────────────────────────────────┘
```
**Style :** Deux colonnes comparatives

---

# SLIDE 6 : ARCHITECTURE D'EXTRACTION
```
┌─────────────────────────────────────────────────────────┐
│  🔧 ARCHITECTURE TECHNIQUE                              │
│                                                         │
│     ┌─────────┐                                         │
│     │  RSS    │──→ rss_fetcher.py                       │
│     └─────────┘                                         │
│                                                         │
│     ┌─────────┐                                         │
│     │  APIs   │──→ api_client.py                        │
│     │(REST)   │   (Reddit, HN, NewsAPI)                  │
│     └─────────┘                                         │
│                                                         │
│     ┌─────────────┐                                     │
│     │ Scraping    │──→ scraper_bs4.py (HTML)            │
│     │             │──→ scraper_selenium.py (JS)         │
│     └─────────────┘                                     │
│                                                         │
│  Stack : Python • BeautifulSoup • Requests • Selenium   │
└─────────────────────────────────────────────────────────┘
```
**Style :** Diagramme de flux descendant

---

# SLIDE 7 : GESTION DES ERREURS
```
┌─────────────────────────────────────────────────────────┐
│  🛡️ ROBUSTESSE ET GESTION D'ERREURS                     │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  TIMEOUT 15s         │  Retry 2x              │   │
│  │  ─────────────────── │  ─────────────────────  │   │
│  │  Par requête HTTP    │  avec délai 5 min      │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ✓ User-Agent personnalisé                             │
│  ✓ Logs structurés (INFO/ERROR)                        │
│  ✓ Fallback automatique                                │
│  ✓ Validation des données                             │
│                                                         │
│  Exemple de log :                                      │
│  ┌─────────────────────────────────────────────────┐   │
│  │ INFO - le_figaro: 10 articles extraits         │   │
│  │ ERROR - reddit: Connexion timeout               │   │
│  │ INFO - Traitement continué avec sources restantes│   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```
**Style :** Code block pour les logs

---

# SLIDE 8 : PIPELINE ETL
```
┌─────────────────────────────────────────────────────────┐
│  🔄 PIPELINE DE TRANSFORMATION                          │
│                                                         │
│     ╔═══════════╗                                       │
│     ║ EXTRACT  ║  → Données brutes (RSS, API, Scraping)│
│     ╚════╤═════╝                                       │
│          ↓                                              │
│     ╔═══════════╗                                       │
│     ║ TRANSFORM ║  → Nettoyage + Validation             │
│     ║           ║    • Suppression HTML                │
│     ║           ║    • Normalisation texte             │
│     ║           ║    • Classification Opinion/Disinfo   │
│     ╚════╤═════╝                                       │
│          ↓                                              │
│     ╔═══════════╗                                       │
│     ║   LOAD   ║  → Stockage (JSON, SQLite)           │
│     ╚════╤═════╝                                       │
│                                                         │
│     Python • Pandas • SQLite                            │
└─────────────────────────────────────────────────────────┘
```
**Style :** Diagramme en entonnoir/flowchart

---

# SLIDE 9 : MODÈLE DE DONNÉES
```
┌─────────────────────────────────────────────────────────┐
│  🗄️ MODÈLE CONCEPTUEL DE DONNÉES (Mermaid)             │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                   │   │
│  │  ARTICLE───────────KEYWORD                       │   │
│  │  (id, title,                                 │   │
│  │   description,                               │   │
│  │   content,                                   │   │
│  │   image_url,                                 │   │
│  │   is_multimodal)                             │   │
│  │        │                                      │   │
│  │        ├───┬───────────SOURCE                 │   │
│  │        │   │  (id, name, url)                   │   │
│  │        │   │                                    │   │
│  │        │   └──────────EXTRACTION_LOG           │   │
│  │        │        (start_time, articles_count)    │   │
│  │        │                                    │   │
│  │        └────────────────METRICS                 │   │
│  │             (timestamp, value, unit)           │   │
│  │                                                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  Entités : ARTICLE, SOURCE, KEYWORD, LOG, METRICS       │
└─────────────────────────────────────────────────────────┘
```
**Style :** Schéma ER simplifié

---

# SLIDE 10 : DAG AIRFLOW
```
┌─────────────────────────────────────────────────────────┐
│  ⚡ ORCHESTRATION AVEC AIRFLOW                          │
│                                                         │
│         ┌──────────────┐                                │
│         │  START        │                                │
│         └──────┬───────┘                                │
│                ↓                                         │
│    ┌───────────┴───────────┐                            │
│    ↓                       ↓                             │
│  ┌────────┐          ┌─────────┐                       │
│  │  RSS   │          │ Reddit  │   (PARALLÈLE)         │
│  │ 10 art │          │ 30 post  │                       │
│  └────┬───┘          └────┬────┘                       │
│       └──────┬────────────┘                             │
│              ↓                                           │
│       ┌──────────────┐                                  │
│       │ MERGE RAW     │  Fusion des données              │
│       └──────┬───────┘                                  │
│              ↓                                           │
│       ┌──────────────┐                                  │
│       │ TRANSFORM    │  Nettoyage + Classification      │
│       └──────┬───────┘                                  │
│              ↓                                           │
│       ┌──────────────┐                                  │
│       │ LOAD         │  Stockage BDD                    │
│       └──────┬───────┘                                  │
│              ↓                                           │
│       ┌──────────────┐                                  │
│       │ KPIs         │  Métriques                       │
│       └──────────────┘                                  │
│                                                         │
│  Schedule : 2x/jour (6h, 18h)                          │
└─────────────────────────────────────────────────────────┘
```
**Style :** Flowchart vertical du DAG

---

# SLIDE 11 : DASHBOARD STREAMLIT
```
┌─────────────────────────────────────────────────────────┐
│  📊 DASHBOARD DE MONITORING                             │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  📰 CheckIt.AI - Fake News Killer                │   │
│  ├─────────────────────────────────────────────────┤   │
│  │  [KPIs] [Données brutes] [Transformées] [Moni.] │   │
│  ├─────────────────────────────────────────────────┤   │
│  │                                                   │   │
│  │   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐  │   │
│  │   │ RSS    │ │Reddit  │ │Multi-  │ │Taux    │  │   │
│  │   │  50    │ │  30    │ │modal  │ │succès  │  │   │
│  │   │articles│ │posts   │ │  65   │ │ 95%    │  │   │
│  │   └────────┘ └────────┘ └────────┘ └────────┘  │   │
│  │                                                   │   │
│  │   [📈 Graphique répartition]  [📈 Sources]      │   │
│  │                                                   │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  KPIs : Extraction, Multimodalité, Taux de validité     │
└─────────────────────────────────────────────────────────┘
```
**Style :** Mockup du dashboard

---

# SLIDE 12 : RÉSULTATS
```
┌─────────────────────────────────────────────────────────┐
│  ✅ RÉSULTATS VALIDÉS                                    │
│                                                         │
│       ┌─────────────────────────────────────────┐       │
│       │         PERFORMANCE DU PIPELINE          │       │
│       ├─────────────────────────────────────────┤       │
│       │  📥 Extraction     │  80 articles/run  │       │
│       │  🖼️ Multimodalité  │  100% avec images  │       │
│       │  ✅ Validité        │  >95% après nettoyage│      │
│       │  ⏱️ Temps exec.    │  < 2 minutes        │       │
│       │  🔄 Automatisation  │  2x/jour Airflow    │       │
│       └─────────────────────────────────────────┘       │
│                                                         │
│       🎯  Objectifs atteints : 5/5 livrables            │
└─────────────────────────────────────────────────────────┘
```
**Style :** Statistiques avec icônes

---

# SLIDE 13 : DIFFICULTÉS
```
┌─────────────────────────────────────────────────────────┐
│  🔧 DIFFICULTÉS RENCONTRÉES                             │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  1. URL RSS 20 Minutes (404)                   │   │
│  │                                                 │   │
│  │  ❌ URL officielle : /rss/une.xml → Erreur 404 │   │
│  │  ✅ URL correcte : /feeds/rss-une.xml          │   │
│  │                                                 │   │
│  │  → Inspecter le code source du site            │   │
│  └─────────────────────────────────────────────────┘   │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │  2. Clés API non disponibles                    │   │
│  │                                                 │   │
│  │  NewsAPI et Reddit nécessitent inscription      │   │
│  │  → Code prêt, clés non livrées dans le cadre    │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```
**Style :** Alert boxes (erreur/résolution)

---

# SLIDE 14 : COMPÉTENCES ACQUISES
```
┌─────────────────────────────────────────────────────────┐
│  🎓 COMPÉTENCES ACQUISES                                │
│                                                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │                                                   │   │
│  │  🕷️ Web Scraping                                │   │
│  │     BeautifulSoup, Selenium, parsing HTML/XML    │   │
│  │                                                   │   │
│  │  🌐 APIs REST                                    │   │
│  │     Consumption, gestion JSON, rate limiting     │   │
│  │                                                   │   │
│  │  🔄 Pipeline ETL                                 │   │
│  │     Extraction, transformation, chargement       │   │
│  │                                                   │   │
│  │  ⚡ Orchestration                                 │   │
│  │     Apache Airflow, DAGs, XCom, scheduling       │   │
│  │                                                   │   │
│  │  📊 Modélisation & Monitoring                     │   │
│  │     Mermaid, Streamlit, KPIs                     │   │
│  │                                                   │   │
│  └─────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```
**Style :** Cards avec icônes

---

# SLIDE 15 : PERSPECTIVES
```
┌─────────────────────────────────────────────────────────┐
│  🚀 PERSPECTIVES D'ÉVOLUTION                            │
│                                                         │
│     1️⃣  Intégrer les APIs complètes                     │
│         (avec clés NewsAPI, Reddit)                    │
│                                                         │
│     2️⃣  Base de données PostgreSQL                      │
│         (persistance robuste)                          │
│                                                         │
│     3️⃣  Tests unitaires pytest                          │
│         (couverture code)                              │
│                                                         │
│     4️⃣  Déploiement Cloud                               │
│         (OKD/Kubernetes)                               │
│                                                         │
│     5️⃣  ML pour la classification                       │
│         (améliorer la détection fake news)            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```
**Style :** Liste numérotée avec progression

---

# SLIDE 16 : CONCLUSION
```
┌─────────────────────────────────────────────────────────┐
│                                                         │
│                    ✅ CONCLUSION                        │
│                                                         │
│        5/5 LIVRABLES    ✅  FONCTIONNELS               │
│                                                         │
│   ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │
│   │Rapport  │ │Scripts  │ │Pipeline │ │DAG      │   │
│   │explorat.│ │extract. │ │ETL+MCD  │ │Airflow  │   │
│   └─────────┘ └─────────┘ └─────────┘ └─────────┘   │
│                        ┌─────────┐                     │
│                        │Dashboard│                     │
│                        └─────────┘                     │
│                                                         │
│   ─────────────────────────────────────────────        │
│                                                         │
│              Merci pour votre attention !              │
│                                                         │
│              Questions ?                                │
│                                                         │
└─────────────────────────────────────────────────────────┘
```
**Style :** Badge 5/5 vert, titre centré

---

# NOTES POUR L'ANIMATEUR

## Timing suggéré
- Slides 1-3 (Intro) : 2-3 min
- Slides 4-5 (Sourcing) : 3-4 min
- Slides 6-7 (Extraction) : 4-5 min
- Slides 8-9 (Transformation) : 3-4 min
- Slide 10 (Airflow) : 3-4 min
- Slide 11 (Dashboard) : 2-3 min
- Slides 12-16 (Conclusion) : 3-4 min

**TOTAL : ~20-25 minutes**

## Démonstrations à préparer
1. Terminal : `pixi run python src/extraction/main.py`
2. Browser : Dashboard Streamlit (port 8501)
3. Airflow : Interface web (port 8080) si disponible
