"""Extraction de données via flux RSS."""

import logging
from datetime import datetime
from typing import Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class RSSFetcher:
    """Gestionnaire de flux RSS."""
    
    DEFAULT_FEEDS = {
        "le_figaro": "https://www.lefigaro.fr/rss/figaro_actualites.xml",
        "le_monde": "https://www.lemonde.fr/rss/une.xml",
        "nouvel_obs": "https://www.nouvelobs.com/rss.xml",
        "20_minutes": "https://www.20minutes.fr/feeds/rss-une.xml",
        "euronews": "https://www.euronews.com/rss",
    }
    
    def __init__(self, feeds: Optional[dict[str, str]] = None):
        self.feeds = feeds or self.DEFAULT_FEEDS
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "CheckIt.AI/1.0 (Research Project)"
        })
    
    def fetch_all(self, limit_per_feed: int = 10) -> list[dict]:
        """Récupère tous les flux RSS."""
        all_articles = []
        
        for name, url in self.feeds.items():
            articles = self.fetch_feed(name, url, limit_per_feed)
            all_articles.extend(articles)
            logger.info(f"{name}: {len(articles)} articles")
        
        return all_articles
    
    def fetch_feed(
        self, 
        name: str, 
        url: str, 
        limit: int = 10
    ) -> list[dict]:
        """Récupère un flux RSS spécifique."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "xml")
            items = soup.find_all("item")[:limit]
            
            articles = []
            for item in items:
                article = self._parse_item(name, item)
                if article:
                    articles.append(article)
            
            return articles
            
        except requests.RequestException as e:
            logger.error(f"Erreur fetch {name}: {e}")
            return []
    
    def _parse_item(self, feed_name: str, item) -> Optional[dict]:
        """Parse un élément RSS."""
        try:
            title = item.find("title")
            link = item.find("link")
            description = item.find("description")
            pub_date = item.find("pubDate")
            
            # Extraction de l'image depuis enclosure ou media:content
            image_url = ""
            enclosure = item.find("enclosure")
            if enclosure and enclosure.get("type", "").startswith("image"):
                image_url = enclosure.get("url", "")
            
            if not image_url:
                media = item.find("media:content") or item.find("media:thumbnail")
                if media:
                    image_url = media.get("url", "")
            
            # Fallback: extraction depuis description HTML
            if not image_url and description:
                img_soup = BeautifulSoup(description.get_text("", strip=True), "html.parser")
                img_tag = img_soup.find("img")
                if img_tag:
                    image_url = img_tag.get("src", "")
            
            return {
                "title": title.get_text(strip=True) if title else "",
                "description": self._clean_html(
                    description.get_text(strip=True) if description else ""
                ),
                "content": "",
                "url": link.get_text(strip=True) if link else "",
                "image_url": image_url,
                "source": feed_name,
                "author": "",
                "published_at": self._parse_date(
                    pub_date.get_text(strip=True) if pub_date else ""
                ),
                "extracted_at": datetime.now().isoformat(),
                "type": "rss"
            }
            
        except Exception as e:
            logger.warning(f"Erreur parsing item: {e}")
            return None
    
    def _clean_html(self, text: str) -> str:
        """Supprime les balises HTML du texte."""
        if not text:
            return ""
        soup = BeautifulSoup(text, "html.parser")
        return soup.get_text(strip=True)
    
    def _parse_date(self, date_str: str) -> str:
        """Parse une date RSS en ISO format."""
        try:
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return dt.isoformat()
        except Exception:
            return datetime.now().isoformat()