"""Module de transformation - Nettoyage des données."""

import re
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class DataCleaner:
    """Nettoyage des données extraites."""
    
    def __init__(self):
        self.stats = {
            "cleaned": 0,
            "dropped": 0,
            "null_title": 0,
            "null_content": 0
        }
    
    def clean(self, article: dict) -> Optional[dict]:
        """Nettoie un article."""
        if not article:
            return None
        
        cleaned = article.copy()
        
        # Titre
        title = cleaned.get("title", "")
        if not title or title == "[Removed]":
            self.stats["null_title"] += 1
            return None
        
        cleaned["title"] = self._clean_text(title)
        
        # Description
        desc = cleaned.get("description", "")
        cleaned["description"] = self._clean_text(desc)[:500]
        
        # Contenu
        content = cleaned.get("content", "")
        cleaned["content"] = self._clean_text(content)
        
        # URL
        url = cleaned.get("url", "")
        cleaned["url"] = url.strip() if url else ""
        
        # Image URL
        img_url = cleaned.get("image_url", "")
        cleaned["image_url"] = img_url.strip() if img_url else ""
        
        # Source
        source = cleaned.get("source", "")
        cleaned["source"] = source.strip() if source else "unknown"
        
        self.stats["cleaned"] += 1
        return cleaned
    
    def _clean_text(self, text: str) -> str:
        """Nettoie le texte."""
        if not text:
            return ""
        
        # Supprime les caractères spéciaux过剩
        text = re.sub(r'\s+', ' ', text)
        text = text.strip()
        
        # Supprime les URLs
        text = re.sub(r'https?://\S+', '', text)
        
        # Supprime les balises HTML résiduelles
        text = re.sub(r'<[^>]+>', '', text)
        
        return text
    
    def clean_batch(self, articles: list[dict]) -> list[dict]:
        """Nettoie une liste d'articles."""
        cleaned_articles = []
        
        for article in articles:
            cleaned = self.clean(article)
            if cleaned:
                cleaned_articles.append(cleaned)
            else:
                self.stats["dropped"] += 1
        
        logger.info(f"Nettoyage: {self.stats['cleaned']} OK, {self.stats['dropped']} supprimés")
        return cleaned_articles
    
    def get_stats(self) -> dict:
        """Retourne les statistiques."""
        return self.stats.copy()


class TextNormalizer:
    """Normalisation du texte pour analyse."""
    
    @staticmethod
    def normalize(text: str) -> str:
        """Normalise le texte."""
        if not text:
            return ""
        
        # Minuscules
        text = text.lower()
        
        # Supprime la ponctuation过剩
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # Supprime les doubles espaces
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    @staticmethod
    def extract_keywords(text: str, max_keywords: int = 10) -> list[str]:
        """Extrait les mots-clés."""
        if not text:
            return []
        
        # Mots vides français
        stop_words = {
            "le", "la", "les", "un", "une", "des", "de", "du", "au",
            "et", "ou", "mais", "donc", "car", "ni", "que", "qui",
            "quoi", "où", "quand", "comment", "pourquoi", "ce", "cette",
            "ces", "ceux", "celles", "il", "elle", "ils", "elles",
            "être", "avoir", "faire", "pouvoir", "vouloir", "devoir",
            "dans", "sur", "sous", "avec", "sans", "pour", "par",
            "est", "sont", "été", "être", "a", "ont"
        }
        
        words = text.lower().split()
        keywords = [
            w for w in words 
            if len(w) > 3 and w not in stop_words
        ]
        
        # Compte les occurrences
        from collections import Counter
        counter = Counter(keywords)
        
        return [w for w, _ in counter.most_common(max_keywords)]


class DataValidator:
    """Validation des données."""
    
    @staticmethod
    def is_valid_article(article: dict) -> bool:
        """Vérifie si l'article est valide."""
        if not article:
            return False
        
        # Titre obligatoire
        if not article.get("title"):
            return False
        
        # Au moins une source de contenu
        if not any([
            article.get("description"),
            article.get("content")
        ]):
            return False
        
        return True
    
    @staticmethod
    def is_multimodal(article: dict) -> bool:
        """Vérifie si l'article est multimodal (avec image)."""
        return bool(article.get("image_url"))
    
    @staticmethod
    def validate_batch(articles: list[dict]) -> dict:
        """Valide un lot et retourne des statistiques."""
        total = len(articles)
        valid = sum(1 for a in articles if DataValidator.is_valid_article(a))
        multimodal = sum(1 for a in articles if DataValidator.is_multimodal(a))
        
        return {
            "total": total,
            "valid": valid,
            "invalid": total - valid,
            "multimodal": multimodal,
            "text_only": total - multimodal
        }