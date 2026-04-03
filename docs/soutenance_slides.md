# Projet P12 - CheckIt.AI
## Extraction de données multimodales pour un détecteur de Fake News

---

## 🎯 Contexte du projet

- **Formation**: Formation IA
- **Projet**: P12 - Extrayez des données multimodales
- **Objectif**: Industrialiser l'acquisition de données (texte + images) depuis le web

---

## 📋 Les 5 livrables

1. **Rapport d'exploration** - Sources identifiées (RSS, API, Scraping)
2. **Scripts d'extraction** - BeautifulSoup, Selenium, API clients
3. **Pipeline ETL** - Nettoyage, normalisation + MCD Mermaid
4. **DAG Airflow** - Orchestration automatisée
5. **Dashboard KPI** - Monitoring avec Streamlit

---

## 🏗️ Architecture technique

```
Sources Web → Extraction → Transformation → Stockage → Monitoring
   (RSS, API)  (BeautifulSoup) (Pandas)    (JSON/CSV)   (Streamlit)
                (Selenium)
```

**Stack**: Python 3.10 • BeautifulSoup • Selenium • Apache Airflow • Streamlit • Mermaid

---

## 📊 Sources de données

| Source | Type | Status |
|--------|------|--------|
| Le Figaro | RSS | ✅ 10 articles |
| Le Monde | RSS | ✅ 10 articles |
| 20 Minutes | RSS | ✅ 10 articles |
| Le Nouvel Obs | RSS | ✅ 10 articles |
| Euronews | RSS | ✅ 10 articles |
| Reddit | API | ✅ 30 posts (3 subreddits) |
| News API | API | ❌ Clé requise (non livrée) |
| Scraping (BeautifulSoup) | Scraping | ✅ Testé fonctionne |
| Scraping (Selenium) | Scraping | ⚠️ Code écrit, Chrome requis |

---

## 🔄 Flux de données (DAG Airflow)

```
extract_rss ─┐
             ├─► merge_raw ─► transform ─► load ─► calculate_kpis
extract_reddit┘
```

Planification: 2x/jour (6h, 18h)

---

## ✅ Résultats validés

- **Extraction**: 4 sources RSS, 20 articles
- **Multimodalité**: 100% (avec images)
- **Pipeline**: Extract → Transform → Load ✅
- **Dashboard**: Streamlit opérationnel

---

## 💡 Points clés pour la soutenance

1. **Multimodalité** = texte + images (要求)
2. **Automatisation** = tout le flux piloté par Airflow
3. **Modularité** = scripts réutilisables, gestion d'erreurs
4. **Qualité** = KPIs pour valider les données

---

## 🔧 Difficultés rencontrées

- **20 Minutes**: URL RSS initiale (404) → résolue avec `/feeds/rss-une.xml`
- **Clés API**: News API et Reddit nécessitent des clés (non livrées)

---

## 🚀 Perspectives d'évolution

- Ajouter News API + Reddit (avec clés)
- Base de données (SQLite/PostgreSQL)
- Tests unitaires pytest
- Déploiement Cloud (Airflow cloud)

---

## 📁 Structure du projet

```
/mnt/prod/
├── docs/exploration_sources.md    # Livrable 1
├── src/extraction/                 # Livrable 2
├── src/transformation/             # Livrable 3
├── src/models/schema.mmd           # MCD
├── dags/fakenews_pipeline.py      # Livrable 4
├── dashboard/app.py                # Livrable 5
└── data/
```

---

## 🎤 Démonstration

**Lancement du pipeline:**
```bash
pixi run python src/extraction/main.py
pixi run python src/transformation/pipeline.py --file extracted_*.json
```

**Dashboard:**
```bash
pixi run streamlit run dashboard/app.py
```

---

## ✅ Conclusion

- **5 livrables**: tous produits et validés
- **Code fonctionnel**: extraction + transformation + monitoring
- **Compétences acquises**: Web Scraping, ETL, Orchestration, Data Quality

**Merci pour votre attention !**