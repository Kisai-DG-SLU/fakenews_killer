"""Module de transformation - Pipeline ETL."""

import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Optional

from src.transformation.cleaner import (
    DataCleaner, 
    TextNormalizer, 
    DataValidator
)
from src.transformation.classifier import ContentClassifier
from src.transformation.database import DatabaseManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class TransformationPipeline:
    """Pipeline ETL complet."""
    
    def __init__(
        self, 
        input_dir: str = "data/raw", 
        output_dir: str = "data/processed",
        use_db: bool = True
    ):
        self.input_dir = Path(input_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.cleaner = DataCleaner()
        self.validator = DataValidator()
        self.classifier = ContentClassifier()
        self.db = DatabaseManager() if use_db else None
    
    def load_raw_data(self, filename: str) -> list[dict]:
        """Charge les données brutes."""
        filepath = self.input_dir / filename
        
        if not filepath.exists():
            logger.error(f"Fichier non trouvé: {filepath}")
            return []
        
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        logger.info(f"Chargé: {len(data)} articles de {filename}")
        return data
    
    def transform(self, articles: list[dict]) -> list[dict]:
        """Transforme les articles."""
        logger.info(f"Transformation de {len(articles)} articles...")
        
        # 1. Nettoyage
        cleaned = self.cleaner.clean_batch(articles)
        
        # 2. Normalisation du texte
        for article in cleaned:
            article["normalized_title"] = TextNormalizer.normalize(
                article.get("title", "")
            )
            article["keywords"] = TextNormalizer.extract_keywords(
                article.get("title", "") + " " + article.get("description", "")
            )
        
        # 3. Validation
        valid_articles = [
            a for a in cleaned 
            if self.validator.is_valid_article(a)
        ]
        
        logger.info(f"Articles valides: {len(valid_articles)}")
        
        # 4. Enrichissement
        for article in valid_articles:
            article["is_multimodal"] = self.validator.is_multimodal(article)
            article["word_count"] = len(
                (article.get("title", "") + " " + article.get("description", "")).split()
            )
        
        # 5. Classification Opinion vs Désinformation
        logger.info("Classification Opinion vs Désinformation...")
        classified = self.classifier.classify_batch(valid_articles)
        
        # 6. Persistance en base de données
        if self.db:
            logger.info("Sauvegarde en base SQLite...")
            count = self.db.insert_articles_batch(classified)
            logger.info(f"Articles insérés en DB: {count}")
        
        return classified
    
    def save(self, articles: list[dict], filename: Optional[str] = None) -> str:
        """Sauvegarde les données transformées."""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transformed_{timestamp}.json"
        
        filepath = self.output_dir / filename
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Sauvegardé: {filepath}")
        return str(filepath)
    
    def save_csv(self, articles: list[dict], filename: Optional[str] = None) -> str:
        """Sauvegarde en CSV."""
        if not articles:
            return ""
        
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"transformed_{timestamp}.csv"
        
        import pandas as pd
        filepath = self.output_dir / filename
        
        df = pd.DataFrame(articles)
        df.to_csv(filepath, index=False)
        
        logger.info(f"Sauvegardé CSV: {filepath}")
        return str(filepath)
    
    def get_stats(self) -> dict:
        """Retourne les statistiques de transformation."""
        return {
            "cleaner_stats": self.cleaner.get_stats(),
            "input_dir": str(self.input_dir),
            "output_dir": str(self.output_dir)
        }


def main():
    """CLI pour la transformation."""
    parser = argparse.ArgumentParser(description="Transformation ETL")
    parser.add_argument("--input", "-i", default="data/raw", help="Répertoire d'entrée")
    parser.add_argument("--output", "-o", default="data/processed", help="Répertoire de sortie")
    parser.add_argument("--file", "-f", required=True, help="Fichier d'entrée")
    parser.add_argument("--format", choices=["json", "csv", "both"], default="json")
    
    args = parser.parse_args()
    
    pipeline = TransformationPipeline(
        input_dir=args.input,
        output_dir=args.output
    )
    
    # Charge et transforme
    articles = pipeline.load_raw_data(args.file)
    transformed = pipeline.transform(articles)
    
    # Sauvegarde
    if args.format in ["json", "both"]:
        pipeline.save(transformed)
    if args.format in ["csv", "both"]:
        pipeline.save_csv(transformed)
    
    # Stats finales
    validation = DataValidator.validate_batch(transformed)
    
    print("\n✓ Transformation terminée")
    print(f"  - Total: {validation['total']}")
    print(f"  - Valides: {validation['valid']}")
    print(f"  - Multimodaux: {validation['multimodal']}")
    print(f"  - Texte seul: {validation['text_only']}")


if __name__ == "__main__":
    main()