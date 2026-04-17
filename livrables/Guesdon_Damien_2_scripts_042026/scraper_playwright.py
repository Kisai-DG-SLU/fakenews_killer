"""Scraping avec Playwright pour les sites dynamiques (JS)."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class PlaywrightScraper:
    """Scraper utilisant Playwright pour les sites JavaScript."""
    
    def __init__(self, output_dir: str = "data/raw"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.browser = None
        self.context = None
    
    async def _init_browser(self):
        """Initialise le navigateur Playwright."""
        try:
            from playwright.async_api import async_playwright
            
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(
                user_agent="CheckIt.AI/1.0 (Research Project)"
            )
            return True
            
        except Exception as e:
            logger.error(f"Erreur initialisation Playwright: {e}")
            return False
    
    async def close(self):
        """Ferme le navigateur."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, 'playwright'):
            await self.playwright.stop()
    
    async def scrape_dynamic_site(
        self,
        url: str,
        article_selector: str = "article",
        title_selector: str = "h2, h3",
        image_selector: str = "img",
        limit: int = 10
    ) -> list[dict]:
        """Scrape un site nécessitant JavaScript."""
        if not await self._init_browser():
            return []
        
        try:
            page = await self.context.new_page()
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            # Attendre le chargement des articles
            await page.wait_for_selector(article_selector, timeout=5000)
            
            # Extraire les articles
            articles_elements = await page.query_selector_all(article_selector)
            articles = []
            
            for elem in articles_elements[:limit]:
                article = await self._extract_dynamic_article(
                    elem, title_selector, image_selector
                )
                if article:
                    articles.append(article)
            
            logger.info(f"Playwright scrape {url}: {len(articles)} articles")
            
            await page.close()
            return articles
            
        except Exception as e:
            logger.error(f"Erreur scrape dynamique: {e}")
            return []
        finally:
            await self.close()
    
    async def _extract_dynamic_article(
        self,
        element,
        title_selector: str,
        image_selector: str
    ) -> Optional[dict]:
        """Extrait les données d'un élément dynamique."""
        try:
            title_elem = await element.query_selector(title_selector)
            title = await title_elem.text_content() if title_elem else ""
            
            img_elem = await element.query_selector(image_selector)
            image_url = await img_elem.get_attribute("src") if img_elem else ""
            
            link_elem = await element.query_selector("a")
            link = await link_elem.get_attribute("href") if link_elem else ""
            
            return {
                "title": title.strip() if title else "",
                "description": "",
                "content": "",
                "url": link or "",
                "image_url": image_url or "",
                "source": "playwright_scraped",
                "author": "",
                "published_at": datetime.now().isoformat(),
                "extracted_at": datetime.now().isoformat(),
                "type": "scraped_playwright"
            }
            
        except Exception as e:
            logger.warning(f"Erreur extraction dynamique: {e}")
            return None


async def main():
    """Exemple d'utilisation."""
    logging.basicConfig(level=logging.INFO)
    
    scraper = PlaywrightScraper()
    
    # Exemple: scrape d'un site dynamique
    articles = await scraper.scrape_dynamic_site(
        "https://www.bfmtv.com/",
        article_selector="article",
        limit=5
    )
    
    print(f"Articles récupérés: {len(articles)}")
    for a in articles:
        print(f"  - {a['title'][:50]}...")


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())