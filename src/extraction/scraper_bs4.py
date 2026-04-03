"""Scraping de sites d'actualité avec BeautifulSoup."""

import os
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


class NewsScraper:
    """Scraper pour les sites d'actualité."""
    
    USER_AGENT = "CheckIt.AI/1.0 (Research Project)"
    
    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": self.USER_AGENT})
    
    def scrape_site(
        self, 
        url: str, 
        selectors: dict[str, str],
        limit: int = 10
    ) -> list[dict]:
        """Scrape un site avec les sélecteurs CSS fournis."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, "html.parser")
            articles = []
            
            # Extraction des articles selon les sélecteurs
            items = soup.select(selectors.get("article", "article"))[:limit]
            
            for item in items:
                article = self._extract_article(item, selectors)
                if article:
                    articles.append(article)
            
            logger.info(f"Scrape {url}: {len(articles)} articles")
            return articles
            
        except requests.RequestException as e:
            logger.error(f"Erreur scrape {url}: {e}")
            return []
    
    def _extract_article(self, element, selectors: dict) -> Optional[dict]:
        """Extrait les données d'un élément article."""
        try:
            title_el = element.select_one(selectors.get("title", "h2, h3"))
            desc_el = element.select_one(selectors.get("description", "p"))
            link_el = element.select_one(selectors.get("link", "a"))
            img_el = element.select_one(selectors.get("image", "img"))
            
            if not title_el:
                return None
            
            title = title_el.get_text(strip=True)
            url = link_el.get("href", "") if link_el else ""
            
            # URL absolue si relative
            if url.startswith("/"):
                from urllib.parse import urljoin
                base_url = "https://example.com"
                url = urljoin(base_url, url)
            
            return {
                "title": title,
                "description": desc_el.get_text(strip=True)[:500] if desc_el else "",
                "content": "",
                "url": url,
                "image_url": img_el.get("src", "") if img_el else "",
                "source": selectors.get("source_name", "unknown"),
                "author": "",
                "published_at": datetime.now().isoformat(),
                "extracted_at": datetime.now().isoformat(),
                "type": "scraped"
            }
            
        except Exception as e:
            logger.warning(f"Erreur extraction: {e}")
            return None
    
    def download_image(self, url: str, article_hash: str) -> Optional[str]:
        """Télécharge une image et retourne le chemin local."""
        if not url:
            return None
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Déterminer l'extension
            ext = ".jpg"
            if "png" in response.headers.get("Content-Type", ""):
                ext = ".png"
            
            filename = f"{article_hash}{ext}"
            filepath = self.output_dir / "images" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            
            with open(filepath, "wb") as f:
                f.write(response.content)
            
            logger.info(f"Image téléchargée: {filename}")
            return str(filepath)
            
        except requests.RequestException as e:
            logger.warning(f"Erreur download image: {e}")
            return None
    
    def save_articles(self, articles: list[dict], source: str) -> str:
        """Sauvegarde les articles en JSON."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"articles_{source}_{timestamp}.json"
        filepath = self.output_dir / filename
        
        import json
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Articles sauvegardés: {filepath}")
        return str(filepath)


# Sélecteurs pour quelques sites français
SITE_SELECTORS = {
    "le_figaro": {
        "url": "https://www.lefigaro.fr/",
        "article": "article, .article-card",
        "title": "h1, h2",
        "description": "p",
        "link": "a",
        "image": "img",
        "source_name": "Le Figaro"
    },
    "20_minutes": {
        "url": "https://www.20minutes.fr/",
        "article": "article, .article",
        "title": "h2, h3",
        "description": ".article-chapo",
        "link": "a",
        "image": "img",
        "source_name": "20 Minutes"
    },
    "france_info": {
        "url": "https://www.francetvinfo.fr/",
        "article": "article, .bci-article",
        "title": "h1, h2",
        "description": "p",
        "link": "a",
        "image": "img",
        "source_name": "France Info"
    }
}


def main():
    """Exemple d'utilisation du scraper."""
    scraper = NewsScraper(output_dir="data/raw")
    
    for name, selectors in SITE_SELECTORS.items():
        articles = scraper.scrape_site(
            selectors["url"], 
            selectors, 
            limit=5
        )
        
        for article in articles:
            if article.get("image_url"):
                # Hash pour le nom de fichier
                hash_val = hashlib.md5(
                    article["url"].encode()
                ).hexdigest()[:8]
                scraper.download_image(article["image_url"], hash_val)
        
        scraper.save_articles(articles, name)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()