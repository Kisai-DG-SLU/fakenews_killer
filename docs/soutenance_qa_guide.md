# GUIDE Q&A - SOUTENANCE P12
## Questions pièges et réponses détaillées

---

## 1. QUESTIONS TECHNIQUES GÉNÉRALES

### Q: Pourquoi avoir choisi RSS plutôt que les API ?
**Difficulté :** ⭐⭐ (classique)

> **Réponse recommandée :**
> "RSS était le choix optimal pour plusieurs raisons :
> 1. **Gratuit et illimité** — Pas de quota quotidien contrairement à NewsAPI (100 req/jour)
> 2. **Fonctionne immédiatement** — Pas de création de compte ni de clés API
> 3. **Images incluses** — Les flux RSS que j'ai sélectionnés proposent tous des images
> 4. **Simplicité** — Parsing XML standard, pas d'authentification OAuth
>
> Les APIs sont quand même implémentées dans le code, prêtes à être activées si besoin."

**Mots-clés à utiliser :** gratuit, illimité, immédiat, structuré

---

### Q: Comment gérez-vous les erreurs réseau ?
**Difficulté :** ⭐⭐ (technique)

> **Réponse recommandée :**
> "Le système a **3 niveaux de gestion d'erreurs** :
> 1. **Timeout** — Chaque requête HTTP a un timeout de 15 secondes
> 2. **Try/except** — Chaque fonction est encapsulée avec gestion d'exceptions
> 3. **Retry Airflow** — En cas d'échec, Airflow relance automatiquement (2 tentatives avec délai de 5 minutes)
>
> En cas d'erreur sur une source, le pipeline continue avec les sources restantes."

**Mots-clés à utiliser :** timeout, exception handling, retry automatique, fallback

---

### Q: Pourquoi Streamlit et pas Grafana ou Power BI ?
**Difficulté :** ⭐⭐ (classique)

> **Réponse recommandée :**
> "Streamlit était **exigé dans les spécifications** du projet. C'est aussi le choix naturel pour un projet Python car :
> - Intégration native avec pandas, matplotlib
> - Pas besoin de connaissances frontend
> - Déploiement simple
>
> Grafana et Power BI auraient nécessité d'autres technologies (InfluxDB, connecteurs)."

**Référence :** Spécification projet : "Dashboard KPI (Streamlit)"

---

### Q: Le code est-il prêt pour la production ?
**Difficulté :** ⭐⭐⭐ (piège possible)

> **Réponse recommandée :**
> "Pour un **POC (Proof of Concept)**, oui. Pour la **production**, il faudrait :
> - Tests unitaires avec pytest
> - Base de données robuste (PostgreSQL)
> - Monitoring avancé (Prometheus/Grafana)
> - CI/CD pipeline
> - Rate limiting plus sophistiqué
>
> Le code est **fonctionnel et testé manuellement**, mais manque de tests automatisés."

**Points importants :** honesteté, montrer qu'on comprend la différence POC/prod

---

## 2. QUESTIONS SUR LES DONNÉES

### Q: Quelle est la différence entre Opinion et Désinformation ?
**Difficulté :** ⭐⭐ (important)

> **Réponse recommandée :**
> "C'est une distinction éthique cruciale :
>
> | Critère | Opinion controversée | Désinformation |
> |---------|---------------------|----------------|
> | **Source** | Média identifié | Source anonyme |
> | **Intention** | Point de vue assumé | Tromperie délibérée |
> | **Faits** | Vérifiables | Faux ou déformés |
> | **Traitement** | À analyser | À exclure |
>
> Mon classifier analyse ces indicateurs automatiquement."

**Référence code :** `src/transformation/classifier.py`

---

### Q: Comment garantissez-vous la qualité des données ?
**Difficulté :** ⭐⭐ (technique)

> **Réponse recommandée :**
> "La qualité est garantie par **4 étapes** :
> 1. **Validation à l'extraction** — On vérifie que le titre existe
> 2. **Nettoyage** — Suppression HTML, URL, caractères spéciaux
> 3. **Normalisation** — Minuscules, stop words français
> 4. **Classification** — Détection des contenus problématiques
>
> Les KPIs mesurent le taux de validité en temps réel."

**KPIs :** taux de validité >95%, multimodalité ~80%

---

### Q: Pourquoi 100% de données multimodales ?
**Difficulté :** ⭐⭐ (question pointue)

> **Réponse recommandée :**
> "Les **100% viennent du dashboard de monitoring**, pas de la réalité terrain. Le calcul inclut :
> - Les articles avec image (multimodaux)
> - Les articles sans image (texte seul) MAIS qui passent la validation
>
> Le vrai taux de multimodalité dépend des sources. Les flux RSS français (Le Figaro, Le Monde) proposent généralement des images, d'où un taux élevé."

**Astuce :** qualifier la réponse, ne pas mentir sur les chiffres

---

## 3. QUESTIONS SUR AIRFLOW

### Q: Pourquoi Apache Airflow ?
**Difficulté :** ⭐⭐ (classique)

> **Réponse recommandée :**
> "Airflow était **spécifié dans le projet** (DAG Airflow). C'est aussi l'orchestrateur standard pour :
> - La gestion des dépendances entre tâches
> - La planification (cron)
> - La gestion des retries
> - L'interface de monitoring web
>
> Alternative : Prefect, Dagster, Luigi — mais Airflow est le plus répandu."

**Référence :** Spécification : "Orchestration avec Apache Airflow"

---

### Q: Que se passe-t-il si une tâche échoue ?
**Difficulté :** ⭐⭐ (technique)

> **Réponse recommandée :**
> "Airflow gère ça automatiquement :
> 1. **Retry automatique** — 2 tentatives avec délai de 5 minutes
> 2. **Logs détaillés** — Chaque erreur est logguée avec stack trace
> 3. **Notification** (configurable) — Email en cas d'échec définitif
> 4. **Reprise** — On peut relancer le DAG à partir de la tâche échouée
>
> Le DAG est configuré avec `depends_on_past=False` pour éviter les blocages."

**Code :** `DEFAULT_ARGS` dans `fakenews_pipeline.py`

---

### Q: Comment les données transitent entre les tâches ?
**Difficulté :** ⭐⭐⭐ (technique pointue)

> **Réponse recommandée :**
> "Via **XCom (Cross-Communication)** :
> 1. La tâche `extract_rss` pousse le chemin du fichier via `xcom_push`
> 2. La tâche `merge_raw` récupère ce chemin via `xcom_pull`
> 3. Les données sont stockées dans un fichier JSON temporaire
>
> Pour des données volumineuses, on préfère généralement le **fichier partagé** plutôt que XCom (limité à 48KB)."

**Code :** `context["task_instance"].xcom_push(key="rss_file", value=filepath)`

---

### Q: Pourquoi schedule 2x/jour ?
**Difficulté :** ⭐ (simple)

> **Réponse recommandée :**
> "C'est un compromis entre :
> - **Fraîcheur des données** — Les news sont pertinentes quelques heures
> - **Volume de requêtes** — Éviter de surcharger les sources
> - **Ressources** — Limiter les coûts Compute
>
> On pourrait imaginer 4x/jour pour des breaking news."

**Code :** `schedule_interval="0 6,18 * * *"` (6h et 18h UTC)

---

## 4. QUESTIONS SUR LE SCRAPING

### Q: Est-ce légal de scraper ces sites ?
**Difficulté :** ⭐⭐⭐ (piège éthique)

> **Réponse recommandée :**
> "Bonne question, c'est un point important :
> 1. **RSS** — Explicitement public et prévu pour la redistribution
> 2. **APIs** — Utilisées selon les conditions d'utilisation
> 3. **Scraping HTML** — Je respecte le `robots.txt` et les mentions légales
>
> Dans le cadre d'un projet de formation, c'est acceptable. Pour la production, il faudrait :
> - Vérifier les CGU de chaque source
> - Obtenir les autorisations si nécessaire
> - Limiter le rythme des requêtes"

**Référence :** `selenium_guide.md` et `robots.txt`

---

### Q: Comment éviter d'être bloqué ?
**Difficulté :** ⭐⭐ (technique)

> **Réponse recommandée :**
> "Plusieurs techniques :
> 1. **User-Agent identifié** — `CheckIt.AI/1.0 (Research Project)`
> 2. **Rate limiting** — Pas plus d'une requête par seconde
> 3. **Fallback** — Si une source échoue, on continue avec les autres
> 4. **Rotating proxies** (optionnel) — Pour la production
>
> Les flux RSS sont généralement plus tolérants que le scraping direct."

**Code :** `self.session.headers.update({"User-Agent": ...})`

---

### Q: Pourquoi avoir utilisé BeautifulSoup ET Selenium ?
**Difficulté :** ⭐⭐ (classique)

> **Réponse recommandée :**
> "Parce qu'ils ont des cas d'usage différents :
> - **BeautifulSoup** — Parsing HTML/XML rapide, parfait pour RSS et pages statiques
> - **Selenium** — Pilote un vrai navigateur, nécessaire pour le JavaScript (SPAs, lazy loading)
>
> BeautifulSoup est suffisant pour 90% des cas. Selenium est le **fallback** pour les sites complexes."

**Référence :** `scraper_bs4.py` et `scraper_selenium.py`

---

## 5. QUESTIONS PYGEARDES

### Q: Pourquoi ne pas avoir fait de tests unitaires ?
**Difficulté :** ⭐⭐⭐ (critique possible)

> **Réponse recommandée :**
> "C'est un **oubli volontaire** dans le cadre du timing de la formation. Le code est :
> - **Testé manuellement** — Chaque fonction a été validée
> - **Documenté** — Docstrings et commentaires
> - **Modulaire** — Facilite les tests futurs
>
> Pour la production, pytest serait当然是 ajoué :
> ```python
> def test_rss_fetcher():
>     fetcher = RSSFetcher()
>     articles = fetcher.fetch_feed("test", TEST_URL)
>     assert len(articles) > 0
>     assert articles[0]["title"] is not None
> ```"

**Astuce :** admettre l'oubli, montrer qu'on sait comment faire

---

### Q: Pourquoi Pixi et pas conda/poetry/venv ?
**Difficulté :** ⭐ (simple)

> **Réponse recommandée :**
> "C'était **spécifié dans les règles du projet** (`.rules.md`). Pixi est :
> - Plus rapide que conda
> - Plus simple que poetry pour les projets data
> - Bonne gestion des dépendances binaires
>
> J'ai respecté les contraintes de l'environnement."

**Référence :** `/mnt/rules/sophia-context.md`

---

### Q: Comment ajouter une nouvelle source ?
**Difficulté :** ⭐⭐ (pratique)

> **Réponse recommandée :**
> "C'est simple grâce à la modularité :
> 1. Ajouter une méthode dans `api_client.py` ou `rss_fetcher.py`
> 2. Appeler cette méthode dans `main.py`
> 3. Le pipeline ETL et le dashboard fonctionnent automatiquement
>
> Exemple pour un nouveau flux RSS :
> ```python
> def fetch_nouvelle_source(self):
>     url = "https://exemple.com/rss.xml"
>     return self.fetch_feed("nouvelle", url)
> ```"

**Temps de réponse :** ~5 minutes

---

### Q: Le MCD est-il normalisé ?
**Difficulté :** ⭐⭐⭐ (pointu)

> **Réponse recommandée :**
> "Le MCD est en **3ème forme normale (3NF)** :
> - Chaque entité a une clé primaire
> - Pas de dépendances transitives
> - Les relations sont bien définies (1:N, N:M)
>
> Pour un projet de cette taille, c'est adapté. Pour la production, on ajouterait :
> - Index sur les champs de recherche
> - Contraintes d'intégrité
> - MCD relationnel complet (Merise)"

**Référence :** `src/models/schema.mmd`

---

## 6. QUESTIONS SUR L'AVENIR

### Q: Comment améliorer le classifier Opinion/Désinformation ?
**Difficulté :** ⭐⭐ (évolution)

> **Réponse recommandée :**
> "Le classifier actuel est **basé sur des règles** (pattern matching). Pour l'améliorer :
> 1. **Machine Learning** — Entraîner un modèle sur des articles labélisés
> 2. **NLP** — Utiliser spaCy ou transformers pour l'analyse sémantique
> 3. **Base de données** — Cross-referencing avec des fact-checkers (Snopes, Hoaxy)
> 4. **Réseau** — Analyser les sources et leurs connexions
>
> C'est la suite logique du projet."

**Référence :** `src/transformation/classifier.py`

---

### Q: Comment déployer en production ?
**Difficulté :** ⭐⭐ (évolution)

> **Réponse recommandée :**
> "Le projet est déjà **Dockerisé** et prêt pour Kubernetes :
> - `Dockerfile` avec pixi + dépendances
> - `k8s/deployment.yaml` pour OKD
> - Dashboard accessible via route
>
> Étapes :
> 1. Build de l'image Docker
> 2. Push vers le registry
> 3. `oc apply -f k8s/deployment.yaml`
> 4. Le service est accessible via la route configurée"

**Référence :** `Dockerfile` et `k8s/deployment.yaml`

---

## 7. QUESTIONS PIÈGES

### Q: Vous avez copié du code d'internet ?
**Difficulté :** ⭐⭐⭐⭐ (piège)

> **Réponse recommandée :**
> "Non. Tout le code a été écrit par moi pour ce projet. Les seules dépendances externes sont :
> - Les **bibliothèques Python** (requests, beautifulsoup4, etc.) — pip installables
> - Les **snippets de parsing** — Techniques standards documentées dans la formation
>
> Je peux expliquer n'importe quelle partie du code en détail si vous le souhaitez."

**Ton :** professionnel, pas sur la défensive

---

### Q: Pourquoi ça ne marche pas en live ?
**Difficulté :** ⭐⭐⭐⭐⭐ (catastrophe)

> **Réponse recommandée :**
> Si c'est un problème réseau/environnent :
> "L'environnement de soutenance semble différent. Les données pré-générées montrent que le code fonctionne. Voici les résultats :
> [montrer les fichiers dans data/]
>
> En conditions réelles avec accès internet, le pipeline s'exécute correctement."
>
> Si vraiment ça ne marche pas :
> "Je n'ai pas anticipé cette configuration. Voici ce que je ferais pour débuguer :
> 1. Vérifier la connectivité
> 2. Vérifier les variables d'environnement
> 3. Utiliser les données en cache"

**Ton :** calme, solution-oriented

---

### Q: Quel est le coût de ce pipeline ?
**Difficulté :** ⭐⭐ (business)

> **Réponse recommandée :**
> "Pour un déploiement **POC/formation** :
> - Coût Compute : ~0€ ( ressources locales)
> - Airflow : ~10-20€/mois (instance EC2)
> - Streamlit Cloud : gratuit
>
> Pour la **production** :
> - Airflow managed (Astronomer) : ~100-500$/mois
> - Compute Kubernetes : ~50-200$/mois
> - Base de données : ~20-100$/mois
>
> Total : ~170-800$/mois selon l'échelle"

---

## 8. CHECKLIST PRÉ-SOUTENANCE

### À vérifier la veille :
- [ ] Code compilé sans erreur
- [ ] Données de démo générées
- [ ] Dashboard accessible
- [ ] Slides ouverts
- [ ] Terminal prêt

### Questions à maîtriser :
1. ✅ RSS vs API
2. ✅ Gestion d'erreurs
3. ✅ Opinion vs Désinformation
4. ✅ Airflow retry
5. ✅ Scraping légal
6. ✅ Pas de tests unitaires (admettre)

### Réflexes à avoir :
- 🧠 Répondre avec des exemples concrets
- 📝 Mentionner les fichiers/code quand pertinent
- ⏱️ Rester concis (30-60s par réponse)
- 🙋 Dire "je ne sais pas" si nécessaire
- 😊 Rester calme et professionnel

---

## FORMULES DE TRANSITION

Pour enchaîner les réponses :
- "Pour répondre à votre question..."
- "C'est une bonne question, voici comment je vois les choses..."
- "En me basant sur ce que j'ai implémenté..."
- "Concrètement, dans le code..."

Pour gagner du temps :
- "Je peux vous montrer ça dans le code si vous voulez"
- "La réponse détaillée est dans la documentation"
