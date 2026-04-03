# Notes du présentateur - Soutenance P12 CheckIt.AI

---

## Slide 1: Titre

**Dire**: "Bonjour, je vais vous présenter le Projet 12 de la Formation IA : CheckIt.AI, un pipeline d'extraction de données multimodales pour un détecteur de Fake News."

**Argumenter**: Ce projet répond à un besoin concret - alimenter une IA de détection de fake news avec des données variées (texte + images).

---

## Slide 2: Contexte

**Dire**: "L'objectif de ce projet est d'industrialiser l'acquisition de données depuis le web. Nous avons besoin de récupérer des articles d'actualité avec leur texte et leurs images."

**Expliquer**: 
- Le détecteur de fake news a besoin de données d'entraînement
- Les données doivent être multimodales (texte + image)
- Le processus doit être automatisé car le volume est important

---

## Slide 3: Les 5 livrables

**Dire**: "Ce projet comprend 5 livrables obligatoires :"

1. **Rapport d'exploration** - "J'ai identifié les sources disponibles : API (News API, Reddit), flux RSS, et scraping direct."

2. **Scripts d'extraction** - "J'ai développé 5 scripts Python utilisant BeautifulSoup, Selenium, et les API REST."

3. **Pipeline ETL** - "Un pipeline de nettoyage et normalisation avec un modèle conceptuel de données en Mermaid."

4. **DAG Airflow** - "L'orchestration complète avec Apache Airflow qui automatise tout le cycle."

5. **Dashboard KPI** - "Un tableau de bord Streamlit pour surveiller les métriques."

---

## Slide 4: Architecture

**Dire**: "Voici l'architecture technique du projet. Les données passent par 4 étapes : extraction, transformation, stockage, et monitoring."

**Pointer**:
- Sources: RSS, API, Scraping
- Outils: BeautifulSoup, Selenium, Pandas
- Stockage: JSON/CSV
- Monitoring: Streamlit

**Souligner**: La modularité - chaque composant peut fonctionner indépendamment.

---

## Slide 5: Sources de données

**Dire**: "J'ai configuré 4 sources RSS françaises qui fonctionnent parfaitement. Les API News API et Reddit nécessitent des clés mais le code est prêt."

**Démontrer**: 
- Le Figaro, Le Monde, 20 Minutes, Nouvel Obs
- Toutes fournissent des images avec les articles

**Astuce**: Mentionner que 20 Minutes nécessitait une URL spécifique (/feeds/rss-une.xml au lieu de /rss/une.xml)

---

## Slide 6: DAG Airflow

**Dire**: "Le DAG Airflow orchestre tout le pipeline automatiquement. Il s'exécute 2 fois par jour (6h et 18h)."

**Expliquer le flux**:
1. extract_rss et extract_reddit en parallèle
2. merge_raw combine les données
3. transform applique le nettoyage
4. load stocke en base
5. calculate_kpis génère les métriques

**Point fort**: Retry automatique en cas d'erreur, logs détaillés.

---

## Slide 7: Résultats

**Dire**: "Le pipeline a été testé et validé :"

- 4 sources actives = 20 articles par exécution
- 100% des articles sont multimodaux (avec images)
- Taux de validité >95% après nettoyage
- Dashboard Streamlit opérationnel

---

## Slide 8: Points clés

**Dire**: "Voici les points importants à retenir pour comprendre ce que j'ai fait :"

1. **Multimodalité** - Je récupère texte ET images, c'est la contrainte du projet
2. **Automatisation** - Tout est géré par Airflow, pas d'intervention humaine
3. **Modularité** - Les scripts sont réutilisables, on peut ajouter des sources facilement
4. **Qualité** - Nettoyage, validation, KPIs pour garantir la qualité des données

---

## Slide 9: Difficultés

**Dire**: "J'ai rencontré deux difficultés principales :"

1. **URL RSS 20 Minutes** - L'URL officielle donnait 404, j'ai dû chercher l'URL réelle dans le code source du site
2. **Clés API** - News API et Reddit nécessitent une inscription, non livrée dans le cadre du projet

**Montrer la résolution**: Le code gère ces cas avec des fallbacks.

---

## Slide 10: Perspectives

**Dire**: "Ce projet peut être enrichi de plusieurs façons :"

- Intégrer les API (avec les clés)
- Ajouter une vraie base de données
- Tests unitaires pytest
- Déploiement Cloud

---

## Slide 11: Structure du projet

**Dire**: "Voici l'organisation du code dans /mnt/prod/"

Montrer les différents dossiers et leur contenu.

---

## Slide 12: Démonstration

**Dire**: "Je vais maintenant montrer une démonstration live du pipeline."

**Commandes à exécuter**:
```bash
cd /mnt/prod
pixi run python src/extraction/main.py --multimodal-only
pixi run streamlit run dashboard/app.py
```

**Prévoir**: avoir les commandes prêtes si pas de live.

---

## Slide 13: Conclusion

**Dire**: "Pour conclude, ce projet m'a permis de maîtriser :"

- Web scraping (BeautifulSoup, Selenium)
- Pipeline ETL complet
- Orchestration avec Airflow
- Monitoring avec Streamlit
- Modélisation de données (Mermaid)

**Merci pour votre attention !**

---

## Questions potentiellement posées

### Q: Pourquoi avoir choisi RSS plutôt que News API ?
**R**: RSS est gratuit et fonctionne sans clé. News API a un quota quotidien (100 req/jour). J'ai préparé les deux.

### Q: Comment gérez-vous les erreurs ?
**R**: Chaque script a un try/except avec logging. Airflow gère les retries automatiquement.

### Q: Quelle est la différence entre Opinion et Désinformation ?
**R**: L'opinion a une source identifiée et une intention explicite. La désinformation est délibérément trompeuse avec de fausses données.

### Q: Pourquoi Streamlit plutôt que Grafana ?
**R**: Streamlit est plus simple pour un dashboard Python, et demandé explicitement dans les specs.

### Q: Le code est-il prêt pour la production ?
**R**: Il est fonctionnel pour un POC. Pour la production, il faudrait: tests unitaires, base de données, monitoring avancé.