"""
Module de persistence des données - Base SQLite/NoSQL

Ce module gère la persistance des données dans une base sécurisée.
"""

import sqlite3
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from contextlib import contextmanager

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Gestionnaire de base de données SQLite."""
    
    def __init__(self, db_path: str = "data/fakenews.db"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    @contextmanager
    def _get_connection(self):
        """Contexte pour gérer les connexions."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Erreur DB: {e}")
            raise
        finally:
            conn.close()
    
    def _init_database(self):
        """Initialise les tables de la base."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Table des articles
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT,
                    content TEXT,
                    url TEXT UNIQUE,
                    image_url TEXT,
                    source TEXT,
                    author TEXT,
                    published_at TEXT,
                    extracted_at TEXT NOT NULL,
                    type TEXT,
                    classification_category TEXT,
                    classification_confidence REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des sources
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    type TEXT,
                    url TEXT,
                    reliability TEXT,
                    last_fetch TEXT,
                    article_count INTEGER DEFAULT 0
                )
            """)
            
            # Table des extractions (logs)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS extraction_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    articles_count INTEGER,
                    errors_count INTEGER DEFAULT 0,
                    status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Table des KPIs
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS kpis (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_name TEXT NOT NULL,
                    value REAL,
                    unit TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Index pour performance
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_source ON articles(source)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_extracted ON articles(extracted_at)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_articles_classif ON articles(classification_category)")
            
            logger.info(f"Base de données initialisée: {self.db_path}")
    
    def insert_article(self, article: dict) -> Optional[int]:
        """Insère un article dans la base."""
        try:
            with self._get_connection() as conn:
                cursor = conn.cursor()
                
                classification = article.get("classification", {})
                
                cursor.execute("""
                    INSERT OR IGNORE INTO articles (
                        title, description, content, url, image_url,
                        source, author, published_at, extracted_at, type,
                        classification_category, classification_confidence
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    article.get("title"),
                    article.get("description"),
                    article.get("content"),
                    article.get("url"),
                    article.get("image_url"),
                    article.get("source"),
                    article.get("author"),
                    article.get("published_at"),
                    article.get("extracted_at"),
                    article.get("type"),
                    classification.get("category"),
                    classification.get("confidence")
                ))
                
                return cursor.lastrowid if cursor.rowcount > 0 else None
                
        except sqlite3.IntegrityError:
            logger.debug(f"Article déjà existant: {article.get('url')}")
            return None
        except Exception as e:
            logger.error(f"Erreur insertion article: {e}")
            return None
    
    def insert_articles_batch(self, articles: list[dict]) -> int:
        """Insère plusieurs articles en batch."""
        count = 0
        for article in articles:
            if self.insert_article(article):
                count += 1
        logger.info(f"Insertés: {count} articles")
        return count
    
    def get_articles(
        self,
        source: Optional[str] = None,
        classification: Optional[str] = None,
        limit: int = 100
    ) -> list[dict]:
        """Récupère des articles avec filtres."""
        query = "SELECT * FROM articles WHERE 1=1"
        params = []
        
        if source:
            query += " AND source = ?"
            params.append(source)
        
        if classification:
            query += " AND classification_category = ?"
            params.append(classification)
        
        query += " ORDER BY extracted_at DESC LIMIT ?"
        params.append(limit)
        
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
    
    def get_statistics(self) -> dict:
        """Retourne des statistiques sur la base."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            
            # Total articles
            cursor.execute("SELECT COUNT(*) as total FROM articles")
            total = cursor.fetchone()["total"]
            
            # Par source
            cursor.execute("""
                SELECT source, COUNT(*) as count 
                FROM articles 
                GROUP BY source 
                ORDER BY count DESC
            """)
            by_source = {row["source"]: row["count"] for row in cursor.fetchall()}
            
            # Par classification
            cursor.execute("""
                SELECT classification_category, COUNT(*) as count 
                FROM articles 
                WHERE classification_category IS NOT NULL
            """)
            by_classification = {
                row["classification_category"]: row["count"] 
                for row in cursor.fetchall()
            }
            
            # Avec images
            cursor.execute("SELECT COUNT(*) as count FROM articles WHERE image_url IS NOT NULL AND image_url != ''")
            with_images = cursor.fetchone()["count"]
            
            return {
                "total_articles": total,
                "by_source": by_source,
                "by_classification": by_classification,
                "with_images": with_images,
                "multimodal_ratio": round(with_images/total*100, 1) if total > 0 else 0
            }
    
    def insert_extraction_log(self, log: dict) -> int:
        """Insère un log d'extraction."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO extraction_logs (source, start_time, end_time, articles_count, errors_count, status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                log.get("source"),
                log.get("start_time"),
                log.get("end_time"),
                log.get("articles_count"),
                log.get("errors_count", 0),
                log.get("status")
            ))
            return cursor.lastrowid
    
    def insert_kpi(self, metric_name: str, value: float, unit: str = "") -> int:
        """Insère un KPI."""
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO kpis (timestamp, metric_name, value, unit)
                VALUES (?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                metric_name,
                value,
                unit
            ))
            return cursor.lastrowid
    
    def export_to_json(self, output_path: str) -> str:
        """Exporte la base en JSON."""
        articles = self.get_articles(limit=10000)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Export JSON: {output_path}")
        return output_path


class NoSQLManager:
    """Gestionnaire de données NoSQL (mode document JSON)."""
    
    def __init__(self, data_dir: str = "data/nosql"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
    
    def save_document(self, collection: str, doc_id: str, data: dict) -> str:
        """Sauvegarde un document."""
        collection_dir = self.data_dir / collection
        collection_dir.mkdir(exist_ok=True)
        
        filepath = collection_dir / f"{doc_id}.json"
        
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return str(filepath)
    
    def get_document(self, collection: str, doc_id: str) -> Optional[dict]:
        """Récupère un document."""
        filepath = self.data_dir / collection / f"{doc_id}.json"
        
        if not filepath.exists():
            return None
        
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def query_by_field(self, collection: str, field: str, value: str) -> list[dict]:
        """Requête par champ (basique)."""
        collection_dir = self.data_dir / collection
        
        if not collection_dir.exists():
            return []
        
        results = []
        for filepath in collection_dir.glob("*.json"):
            with open(filepath, "r", encoding="utf-8") as f:
                doc = json.load(f)
                if doc.get(field) == value:
                    results.append(doc)
        
        return results


def main():
    """Test de la base de données."""
    db = DatabaseManager("data/test.db")
    
    # Insertion de test
    test_article = {
        "title": "Article de test",
        "description": "Description test",
        "url": "https://test.com",
        "source": "test",
        "extracted_at": datetime.now().isoformat(),
        "type": "test",
        "classification": {
            "category": "neutre",
            "confidence": 0.5
        }
    }
    
    db.insert_article(test_article)
    
    stats = db.get_statistics()
    print(f"Stats: {stats}")
    
    # Cleanup
    import os
    os.remove("data/test.db")


if __name__ == "__main__":
    main()