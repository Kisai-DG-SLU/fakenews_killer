"""Orchestrateur principal pour l'extraction de données."""

import sys
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.extraction.api_client import NewsAPIAIClient, RedditClient, HackerNewsClient  # noqa: E402
from src.extraction.rss_fetcher import RSSFetcher  # noqa: E402
from src.extraction.scraper_bs4 import NewsScraper  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class DataExtractor:
    """Orchestrateur d'extraction multimodale."""
    
    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.newsapi_client = NewsAPIAIClient()
        self.hackernews_client = HackerNewsClient()
        self.reddit_client = RedditClient()
        self.rss_fetcher = RSSFetcher()
        self.scraper = NewsScraper(output_dir)
    
    def extract_all(
        self,
        use_api: bool = True,
        use_rss: bool = True,
        use_reddit: bool = True,
        use_scraping: bool = False
    ) -> list[dict]:
        """Extraction depuis toutes les sources configurées."""
        all_articles = []
        
        if use_rss:
            logger.info("=== Extraction RSS ===")
            rss_articles = self.rss_fetcher.fetch_all(limit_per_feed=10)
            all_articles.extend(rss_articles)
            logger.info(f"RSS: {len(rss_articles)} articles")
        
        if use_api:
            if self.newsapi_client.is_available():
                logger.info("=== Extraction NewsAPI.ai (Event Registry) ===")
                articles = self.newsapi_client.get_articles(
                    keyword="France",
                    language="fra",
                    max_results=20
                )
                all_articles.extend(articles)
                logger.info(f"NewsAPI.ai: {len(articles)} articles")
            else:
                logger.warning("=== NewsAPI.ai: non disponible ===")
        
        # Hacker News API (gratuit, sans clé)
        if use_api:
            logger.info("=== Extraction Hacker News ===")
            hn_articles = self.hackernews_client.get_top_stories(limit=20)
            all_articles.extend(hn_articles)
            logger.info(f"Hacker News: {len(hn_articles)} articles")
        
        if use_reddit:
            logger.info("=== Extraction Reddit ===")
            subreddits = ["news", "france", "worldnews"]
            for sub in subreddits:
                posts = self.reddit_client.get_hot_posts(sub, limit=10)
                all_articles.extend(posts)
            logger.info(f"Reddit: {len(posts)} posts de r/{sub}")
        
        if use_scraping:
            logger.info("=== Extraction Scraping (BeautifulSoup) ===")
            # Scraping direct sur sites cibles
            from src.extraction.scraper_bs4 import SITE_SELECTORS
            for name, selectors in SITE_SELECTORS.items():
                articles = self.scraper.scrape_site(
                    selectors["url"], 
                    selectors, 
                    limit=5
                )
                all_articles.extend(articles)
            logger.info("Scraping terminé")
        
        logger.info(f"Total: {len(all_articles)} articles multimodal")
        return all_articles
    
    def extract_multimodal_only(self, articles: list[dict]) -> list[dict]:
        """Filtre pour ne garder que les articles avec images."""
        multimodal = [a for a in articles if a.get("image_url")]
        logger.info(f"Articles multimodaux (avec images): {len(multimodal)}")
        return multimodal
    
    def save(self, articles: list[dict], filename: Optional[str] = None) -> str:
        """Sauvegarde les articles en JSON."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"extracted_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Sauvegardé: {filepath}")
        return str(filepath)
    
    def save_csv(self, articles: list[dict], filename: Optional[str] = None) -> str:
        """Sauvegarde les articles en CSV."""
        if not articles:
            return ""
        
        import pandas as pd
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"extracted_{timestamp}.csv"
        
        filepath = self.output_dir / filename
        df = pd.DataFrame(articles)
        df.to_csv(filepath, index=False)
        
        logger.info(f"Sauvegardé CSV: {filepath}")
        return str(filepath)


def main():
    """CLI pour l'extraction."""
    parser = argparse.ArgumentParser(description="Extraction de données multimodales")
    parser.add_argument("--output", "-o", default="data/raw", help="Répertoire de sortie")
    parser.add_argument("--no-api", action="store_true", help="Désactiver News API")
    parser.add_argument("--no-rss", action="store_true", help="Désactiver RSS")
    parser.add_argument("--no-reddit", action="store_true", help="Désactiver Reddit")
    parser.add_argument("--scraping", action="store_true", help="Activer le scraping")
    parser.add_argument("--multimodal-only", action="store_true", help="Garder que les articles avec images")
    parser.add_argument("--format", choices=["json", "csv", "both"], default="json")
    
    args = parser.parse_args()
    
    extractor = DataExtractor(output_dir=args.output)
    
    articles = extractor.extract_all(
        use_api=not args.no_api,
        use_rss=not args.no_rss,
        use_reddit=not args.no_reddit,
        use_scraping=args.scraping
    )
    
    if args.multimodal_only:
        articles = extractor.extract_multimodal_only(articles)
    
    if args.format in ["json", "both"]:
        extractor.save(articles)
    
    if args.format in ["csv", "both"]:
        extractor.save_csv(articles)
    
    print(f"\n✓ Extraction terminée: {len(articles)} articles")
    print(f"  - Multimodaux: {len([a for a in articles if a.get('image_url')])}")


if __name__ == "__main__":
    main()