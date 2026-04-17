# Rapport d'exploration des sources

**Projet:** CheckIt.AI - Fake News Killer  
**Date:** 2026-04-03  
**Auteur:** Damien G.

---

## 1. Objectif

Identifier des sources multimodales (texte + images) d'actualité pour alimenter un détecteur de Fake News.

---

## 2. Sources potentielles

### 2.1 News API (newsapi.org)

| Critère | Détail |
|---------|--------|
| **Type** | API REST |
| **Gratuit** | 100 requêtes/jour (Plan gratuit) |
| **Données** | Titres, descriptions, URL source, date |
| **Images** | ✅ Oui (URL vers image) |
| **Catégories** | business, entertainment, general, health, science, sports, technology |
| **Limite** | Pas de scraping direct, nécessite clé API |

**Avantages:** Structure JSON claire, images disponibles  
**Inconvénients:** Limite quotidienne, nécessitent inscription

---

### 2.2 Reddit (reddit.com)

| Critère | Détail |
|---------|--------|
| **Type** | API REST + Scraping |
| **Gratuit** | ✅ Illimité (avec authentification OAuth) |
| **Données** | Posts, commentaires, métadonnées |
| **Images** | ✅ Oui (upload ou URL) |
| **Subreddits** | r/news, r/worldnews, r/politics |
| **Limite** | Rate limit 60 requêtes/minute |

**Avantages:** Contenu varié, multimodal (texte + images), gratuit  
**Inconvénients:** Contenu utilisateur, qualité variable

---

### 2.3 MediaStack (mediastack.com)

| Critère | Détail |
|---------|--------|
| **Type** | API REST |
| **Gratuit** | 1000 requêtes/mois |
| **Données** | Articles complets, images |
| **Images** | ✅ Oui |
| **Couverture** | Monde entier |

**Avantages:** Articles complets avec images  
**Inconvénients:** Limite mensuelle

---

### 2.4 RSS + Scraping (BeautifulSoup)

| Critère | Détail |
|---------|--------|
| **Type** | Scraping |
| **Gratuit** | ✅ Illimité |
| **Sources** | Le Figaro, Le Monde, 20minutes, etc. |
| **Images** | ✅ Oui (extraction depuis HTML) |
| **Limite** | Respect du robots.txt, pas de charge excessive |

**Avantages:** Gratuit, contrôle total, données complètes  
**Inconvénients:** Code plus complexe, risque de blocage

---

## 3. Distinction éthique

### Opinion controversée vs Désinformation

| Critère | Opinion controversée | Désinformation |
|---------|---------------------|----------------|
| **Source** | Médias identifiés, éditorialistes | Sources non identifiées, sites inconnus |
| **Intentionalité** | Point de vue assumé | Tromperie délibérée |
| **Vérifiabilité** | Faits vérifiables | Fausses données |
| **Traitement** | À analyser | À exclure/rejeter |

---

## 4. Recommandation

**Source choisie pour le livrable 2:** **News API** ou **RSS + BeautifulSoup**

- **News API** : plus simple à implémenter, structure prédéfinie
- **RSS + Scraping** : gratuit, plus de contrôle, données complètes

**Plan d'action:**
1. Implémenter un script Python avec `requests` pour News API
2. Fallback: scraper un flux RSS (Le Figaro ou 20minutes)
3. Extraction des images avec `urllib` ou `requests`
4. Stockage local en JSON/CSV

---

## 5. Technologies utilisées

```python
import requests           # API calls
from bs4 import BeautifulSoup  # HTML parsing
import feedparser        # RSS parsing
import urllib            # Image download
```

---

## 6. Conclusion

Plusieurs sources sont disponibles et adaptées au projet. Le choixfinal dépendra de la facilité d'implémentation et du volume de données souhaité. La solution combinée (API + fallback scraping) offre la meilleure résilience.