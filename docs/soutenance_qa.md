# Questions/Réponses - Soutenance P12 CheckIt.AI

---

## Questions techniques

### Q: Pourquoi avoir choisi RSS plutôt que News API ?
**R**: RSS est gratuit, sans clé, et fonctionne immédiatement. News API a un quota gratuit limité (100 req/jour). Le code pour les deux est développé - RSS est juste activé par défaut.

---

### Q: Comment gérez-vous les erreurs de scraping ?
**R**: Chaque script utilise try/except avec logging détaillé. Le code gère:
- Timeouts (15 secondes)
- HTTP errors (4xx, 5xx)
- Parsing errors
- Images non disponibles

Airflow ajoute une couche de retry automatique (2 tentatives).

---

### Q: Quelle est la différence entre Opinion controversée et Désinformation ?
**R**:
- **Opinion**: Source identifiée (média, éditorialiste), intention assumée, faits vérifiables
- **Désinformation**: Source non identifiée, trompeuse délibérément, fausses données

Mon pipeline ne fait pas cette distinction - c'est un travail pour le modèle ML en aval.

---

### Q: Pourquoi Streamlit plutôt que Grafana pour le dashboard ?
**R**: Streamlit était explicitement demandé dans les spécifications du projet (#Streamlit dans les technologies). C'est aussi plus simple à intégrer avec du code Python.

### Q: Le code est-il prêt pour la production ?
**R**: Pour un POC/MVP, oui. Pour la production, il faudrait ajouter:
- Tests unitaires pytest (non implémentés)
- Base de données réelle (SQLite/PostgreSQL)
- Monitoring avancé (Prometheus, Jaeger)
- Authentification Airflow
- Gestion des secrets (pas de clés dans le code)

---

## Points non fonctionnels (limitations)

### Q: News API ne fonctionne pas - pourquoi l'avoir mentionné ?
**R**: Le code est écrit et fonctionnel si on a une clé API. Le plan gratuit permet 100 requêtes/jour. La clé peut être obtenue sur newsapi.org. Le projet gère ce cas avec un warning clair.

### Q: Selenium n'est pas testé ?
**R**: Le code est développé et suit les bonnes pratiques (headless, wait explicites, gestion d'erreurs). Il nécessite Chrome/Chromedriver installé pour fonctionner. Non testable dans l'environnement actuel.

---

## Questions sur le projet

### Q: Quelle est la taille des données extraites ?
**R**: ~20-50 articles par exécution (selon nombre de sources). Format JSON (~50-100 KB).

### Q: Combien de temps pour exécuter le pipeline ?
**R**: < 30 secondes pour l'extraction RSS. La transformation ajoute ~5 secondes.

### Q: Pourquoi 4 sources RSS françaises ?
**R**: Ce sont les sources d'actualité principales en France avec flux RSS accessible et.images dans le flux. J'ai écarté 20 Minutes initialement car l'URL était incorrecte (corrigé depuis).

### Q: Quelle est la fréquence d'exécution ?
**R**: Le DAG Airflow est configuré pour 2 exécutions par jour (6h et 18h). Peut être ajusté selon besoins.

---

## Questions sur les compétences

### Q: Qu'avez-vous appris avec ce projet ?
**R**:
- Web scraping multi-sources (RSS, API, BeautifulSoup, Selenium)
- Pipeline ETL complet (Extract → Transform → Load)
- Orchestration avec Apache Airflow
- Dashboarding avec Streamlit
- Modélisation de données (MCD Mermaid)
- Gestion de projet Data Engineering

### Q: Quels sont les points faibles du projet ?
**R**:
- Pas de tests unitaires
- Pas de base de données (fichiers JSON/CSV)
- Clés API non intégrées
- Monitoring basique

---

## Questions surprises possibles

### Q: Comment gèrez-vous les images non disponibles ?
**R**: L'article est marqué comme non-multimodal. Le filtre `--multimodal-only` permet de ne garder que les articles avec images.

### Q: Que se passe-t-il si une source est-down ?
**R**: Le script catch l'erreur, log un warning, et continue avec les autres sources. Airflow permet aussi de retenter en cas d'échec.

### Q: Pourquoi Mermaid pour le schéma ?
**R**: Demandé dans les spécifications (#ConceptualDataModel #Mermaid). Plus léger qu'un outil CASE et intégrable en Markdown.