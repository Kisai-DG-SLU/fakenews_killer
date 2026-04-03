"""Scraping avec Selenium pour les sites dynamiques (JS)."""

import os
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class SeleniumScraper:
    """Scraper utilisant Selenium pour les sites JavaScript."""
    
    def __init__(self, output_dir: str = "data/raw", headless: bool = True):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.headless = headless
        self.driver = None
    
    def _init_driver(self):
        """Initialise le driver Selenium."""
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            options = Options()
            if self.headless:
                options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("user-agent=CheckIt.AI/1.0 (Research)")
            
            self.driver = webdriver.Chrome(options=options)
            return True
            
        except Exception as e:
            logger.error(f"Erreur initialisation Selenium: {e}")
            return False
    
    def scrape_dynamic_site(
        self,
        url: str,
        article_selector: str = "article",
        title_selector: str = "h2, h3",
        image_selector: str = "img",
        limit: int = 10
    ) -> list[dict]:
        """Scrape un site nécessitant JavaScript."""
        if not self._init_driver():
            return []
        
        try:
            self.driver.get(url)
            self.driver.implicitly_wait(3)
            
            from selenium.webdriver.common.by import By
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            # Attendre que les articlesChargent
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, article_selector))
            )
            
            articles_elements = self.driver.find_elements(
                By.CSS_SELECTOR, article_selector
            )[:limit]
            
            articles = []
            for elem in articles_elements:
                article = self._extract_dynamic_article(
                    elem, title_selector, image_selector
                )
                if article:
                    articles.append(article)
            
            logger.info(f"Scrape dynamique {url}: {len(articles)} articles")
            return articles
            
        except Exception as e:
            logger.error(f"Erreur scrape dynamique: {e}")
            return []
        finally:
            if self.driver:
                self.driver.quit()
    
    def _extract_dynamic_article(
        self,
        element,
        title_selector: str,
        image_selector: str
    ) -> Optional[dict]:
        """Extrait les données d'un élément dynamique."""
        try:
            from selenium.webdriver.common.by import By
            
            title_elem = element.find_element(
                By.CSS_SELECTOR, title_selector
            )
            title = title_elem.text.strip()
            
            # Extraire l'image
            image_url = ""
            try:
                img_elem = element.find_element(By.CSS_SELECTOR, image_selector)
                image_url = img_elem.get_attribute("src")
            except:
                pass
            
            # Extraire le lien
            link = ""
            try:
                link_elem = element.find_element(By.TAG_NAME, "a")
                link = link_elem.get_attribute("href")
            except:
                pass
            
            return {
                "title": title,
                "description": "",
                "content": "",
                "url": link,
                "image_url": image_url,
                "source": "dynamic_site",
                "author": "",
                "published_at": datetime.now().isoformat(),
                "extracted_at": datetime.now().isoformat(),
                "type": "scraped_selenium"
            }
            
        except Exception as e:
            logger.warning(f"Erreur extraction dynamique: {e}")
            return None


def main():
    """Exemple d'utilisation."""
    logging.basicConfig(level=logging.INFO)
    
    scraper = SeleniumScraper(headless=True)
    
    # Exemple: scrape d'un site dynamique
    # articles = scraper.scrape_dynamic_site(
    #     "https://www.bfmtv.com/",
    #     article_selector="article",
    #     limit=10
    # )
    # print(f"Articles récupérés: {len(articles)}")


if __name__ == "__main__":
    main()