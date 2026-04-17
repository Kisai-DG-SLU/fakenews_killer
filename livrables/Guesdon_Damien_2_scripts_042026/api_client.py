"""Client API pour l'extraction de données d'actualité."""

import os
import logging
from datetime import datetime
from typing import Optional
import requests

logger = logging.getLogger(__name__)


class HackerNewsClient:
    """Client pour l'API Hacker News (gratuit, sans clé)."""
    
    BASE_URL = "https://hacker-news.firebaseio.com/v0"
    
    def get_top_stories(self, limit: int = 20) -> list[dict]:
        """Récupère les meilleures histoires."""
        try:
            response = requests.get(f"{self.BASE_URL}/topstories.json", timeout=10)
            response.raise_for_status()
            story_ids = response.json()[:limit]
            
            articles = []
            for story_id in story_ids:
                item_response = requests.get(
                    f"{self.BASE_URL}/item/{story_id}.json", 
                    timeout=5
                )
                if item_response.status_code == 200:
                    item = item_response.json()
                    if item and item.get("url"):
                        articles.append({
                            "title": item.get("title", ""),
                            "description": item.get("text", "")[:500] if item.get("text") else "",
                            "content": item.get("text", ""),
                            "url": item.get("url", ""),
                            "image_url": "",  # HN ne fournit pas d'images
                            "source": "hacker_news",
                            "author": item.get("by", ""),
                            "published_at": datetime.fromtimestamp(
                                item.get("time", 0)
                            ).isoformat() if item.get("time") else "",
                            "extracted_at": datetime.now().isoformat(),
                            "score": item.get("score", 0),
                            "type": "hacker_news"
                        })
            
            logger.info(f"Hacker News: {len(articles)} articles")
            return articles
            
        except requests.RequestException as e:
            logger.error(f"Erreur Hacker News: {e}")
            return []


class NewsAPIAIClient:
    """Client pour l'API NewsAPI.ai / Event Registry (gratuit avec clé)."""
    
    BASE_URL = "https://eventregistry.org/api/v1"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or "482fd0f1-a345-4943-982a-ecc96d78e634"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def get_articles(
        self,
        keyword: str = "France",
        language: str = "fra",
        max_results: int = 20
    ) -> list[dict]:
        """Récupère des articles via Event Registry API."""
        endpoint = f"{self.BASE_URL}/article/getArticles"
        
        params = {
            "apiKey": self.api_key,
            "keyword": keyword,
            "lang": language,
            "articlesCount": max_results,
            "articlesSortBy": "date",
            "includeArticleImage": True,
            "includeArticleBasicInfo": True
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            articles_data = data.get("articles", {}).get("results", [])
            logger.info(f"NewsAPI.ai (Event Registry): {len(articles_data)} articles")
            return self._normalize_articles(articles_data)
            
        except requests.RequestException as e:
            logger.error(f"Erreur NewsAPI.ai: {e}")
            return []
    
    def _normalize_articles(self, articles: list[dict]) -> list[dict]:
        """Normalise les articles au format standard."""
        normalized = []
        for article in articles:
            normalized.append({
                "title": article.get("title", ""),
                "description": article.get("summary", ""),
                "content": article.get("body", ""),
                "url": article.get("url", ""),
                "image_url": article.get("image", ""),
                "source": article.get("source", {}).get("title", "") if isinstance(article.get("source"), dict) else "",
                "author": "",
                "published_at": article.get("date", ""),
                "extracted_at": datetime.now().isoformat(),
                "type": "newsapi_ai"
            })
        return normalized


class NewsAPIClient:
    """Client pour l'API NewsAPI (newsapi.org) - OBSOLÈTE, utiliser NewsAPIAIClient."""
    
    BASE_URL = "https://newsapi.org/v2"
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("NEWS_API_KEY", "")
        if not self.api_key:
            logger.warning("NEWS_API_KEY non définie. API non fonctionnelle sans clé.")
    
    def is_available(self) -> bool:
        """Vérifie si l'API est configurée."""
        return bool(self.api_key)
    
    def get_top_headlines(
        self,
        country: str = "fr",
        category: Optional[str] = None,
        page_size: int = 20
    ) -> list[dict]:
        """Récupère les dernières actualités."""
        if not self.api_key:
            logger.error("Clé API manquante - obtenir une clé sur https://newsapi.org")
            return []
            return []
        
        endpoint = f"{self.BASE_URL}/top-headlines"
        params = {
            "apiKey": self.api_key,
            "country": country,
            "pageSize": page_size
        }
        if category:
            params["category"] = category
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                articles = data.get("articles", [])
                logger.info(f"Récupéré {len(articles)} articles de NewsAPI")
                return self._normalize_articles(articles)
            else:
                logger.error(f"Erreur API: {data.get('message')}")
                return []
                
        except requests.RequestException as e:
            logger.error(f"Erreur requête: {e}")
            return []
    
    def search_news(self, query: str, page_size: int = 20) -> list[dict]:
        """Recherche des articles par mot-clé."""
        if not self.api_key:
            return []
        
        endpoint = f"{self.BASE_URL}/everything"
        params = {
            "apiKey": self.api_key,
            "q": query,
            "pageSize": page_size,
            "sortBy": "publishedAt"
        }
        
        try:
            response = requests.get(endpoint, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                return self._normalize_articles(data.get("articles", []))
            return []
            
        except requests.RequestException as e:
            logger.error(f"Erreur recherche: {e}")
            return []
    
    def _normalize_articles(self, articles: list[dict]) -> list[dict]:
        """Normalise les articles au format standard."""
        normalized = []
        for article in articles:
            normalized.append({
                "title": article.get("title", ""),
                "description": article.get("description", ""),
                "content": article.get("content", ""),
                "url": article.get("url", ""),
                "image_url": article.get("urlToImage", ""),
                "source": article.get("source", {}).get("name", ""),
                "author": article.get("author", ""),
                "published_at": article.get("publishedAt", ""),
                "extracted_at": datetime.now().isoformat(),
                "type": "news_api"
            })
        return normalized


class RedditClient:
    """Client pour l'API Reddit."""
    
    BASE_URL = "https://www.reddit.com"
    
    def __init__(self, user_agent: str = "CheckIt.AI/1.0"):
        self.headers = {"User-Agent": user_agent}
    
    def get_hot_posts(self, subreddit: str = "news", limit: int = 25) -> list[dict]:
        """Récupère les posts populaires d'un subreddit."""
        endpoint = f"{self.BASE_URL}/r/{subreddit}/hot.json"
        params = {"limit": limit}
        
        try:
            response = requests.get(
                endpoint, 
                headers=self.headers, 
                params=params,
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            
            posts = data.get("data", {}).get("children", [])
            logger.info(f"Récupéré {len(posts)} posts de r/{subreddit}")
            return self._normalize_posts(posts)
            
        except requests.RequestException as e:
            logger.error(f"Erreur Reddit: {e}")
            return []
    
    def _normalize_posts(self, posts: list[dict]) -> list[dict]:
        """Normalise les posts au format standard."""
        normalized = []
        for post in posts:
            data = post.get("data", {})
            
            # Déterminer si c'est une image
            is_image = data.get("post_hint") == "image"
            image_url = data.get("url") if is_image else ""
            
            normalized.append({
                "title": data.get("title", ""),
                "description": data.get("selftext", "")[:500],
                "content": data.get("selftext", ""),
                "url": f"https://reddit.com{data.get('permalink', '')}",
                "image_url": image_url,
                "source": f"reddit/r/{data.get('subreddit', '')}",
                "author": data.get("author", ""),
                "published_at": datetime.fromtimestamp(
                    data.get("created_utc", 0)
                ).isoformat(),
                "extracted_at": datetime.now().isoformat(),
                "score": data.get("score", 0),
                "type": "reddit"
            })
        return normalized