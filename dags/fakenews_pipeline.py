"""
DAG Airflow pour le pipeline d'extraction de données Fake News Killer.

Flow: Extraction → Transformation → Stockage → Métriques
Schedule: Toutes les 2 heures
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import TaskGroup
import logging

DEFAULT_ARGS = {
    "owner": "CheckIt.AI",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

PROJECT_DIR = "/workspace/fakenews_killer"
DATA_RAW = f"{PROJECT_DIR}/data/raw"
DATA_PROCESSED = f"{PROJECT_DIR}/data/processed"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def start_pipeline(ti):
    """Point de départ - initialise le timestamp."""
    ti.xcom_push(key="start_time", value=datetime.now().isoformat())
    return "Pipeline started"


def extract_rss(ti):
    """Tâche d'extraction RSS."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    from src.extraction.rss_fetcher import RSSFetcher
    
    fetcher = RSSFetcher()
    articles = fetcher.fetch_all(limit_per_feed=15)
    
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{DATA_RAW}/rss_extract_{timestamp}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False)
    
    logger.info(f"RSS: {len(articles)} articles extraits")
    
    ti.xcom_push(key="rss_count", value=len(articles))
    ti.xcom_push(key="rss_file", value=filepath)
    
    return filepath


def extract_reddit(ti):
    """Tâche d'extraction Reddit."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    from src.extraction.api_client import RedditClient
    
    client = RedditClient()
    all_posts = []
    
    for sub in ["news", "france", "worldnews"]:
        posts = client.get_hot_posts(sub, limit=10)
        all_posts.extend(posts)
    
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{DATA_RAW}/reddit_extract_{timestamp}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(all_posts, f, ensure_ascii=False)
    
    logger.info(f"Reddit: {len(all_posts)} posts extraits")
    
    ti.xcom_push(key="reddit_count", value=len(all_posts))
    ti.xcom_push(key="reddit_file", value=filepath)
    
    return filepath


def extract_hackernews(ti):
    """Tâche d'extraction HackerNews."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    from src.extraction.api_client import HackerNewsClient
    
    client = HackerNewsClient()
    articles = client.get_top_stories(limit=15)
    
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{DATA_RAW}/hackernews_extract_{timestamp}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False)
    
    logger.info(f"HackerNews: {len(articles)} articles extraits")
    
    ti.xcom_push(key="hackernews_count", value=len(articles))
    ti.xcom_push(key="hackernews_file", value=filepath)
    
    return filepath


def extract_scraper_bs4(ti):
    """Tâche d'extraction via scraper BS4 (Le Figaro article test)."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    from src.extraction.scraper_bs4 import NewsScraper
    
    scraper = NewsScraper(output_dir=DATA_RAW)
    
    selectors = {
        "article": "article",
        "title": "h2, .article-title",
        "link": "a[href]",
        "date": "time, .date"
    }
    
    articles = scraper.scrape_site(
        "https://www.lefigaro.fr/",
        selectors,
        limit=10
    )
    
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{DATA_RAW}/bs4_extract_{timestamp}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False)
    
    logger.info(f"BS4: {len(articles)} articles extraits")
    
    ti.xcom_push(key="bs4_count", value=len(articles))
    ti.xcom_push(key="bs4_file", value=filepath)
    
    return filepath


def extract_scraper_selenium(ti):
    """Tâche d'extraction via Selenium (Le Monde test)."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    try:
        from src.extraction.scraper_selenium import SeleniumScraper
        
        scraper = SeleniumScraper(output_dir=DATA_RAW, headless=True)
        
        selectors = {
            "article": "article",
            "title": "h3, .article-title",
            "link": "a[href]",
            "date": "time, .date"
        }
        
        articles = scraper.scrape_site(
            "https://www.lemonde.fr/",
            selectors,
            limit=10
        )
    except Exception as e:
        logger.warning(f"Selenium error: {e}")
        articles = []
    
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{DATA_RAW}/selenium_extract_{timestamp}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False)
    
    logger.info(f"Selenium: {len(articles)} articles extraits")
    
    ti.xcom_push(key="selenium_count", value=len(articles))
    ti.xcom_push(key="selenium_file", value=filepath)
    
    return filepath


def extract_scraper_playwright(ti):
    """Tâche d'extraction via Playwright (20 Minutes test)."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    try:
        from src.extraction.scraper_playwright import PlaywrightScraper
        
        scraper = PlaywrightScraper(output_dir=DATA_RAW, headless=True)
        
        selectors = {
            "article": "article",
            "title": "h3, .article-title",
            "link": "a[href]",
            "date": "time, .date"
        }
        
        articles = scraper.scrape_site(
            "https://www.20minutes.fr/",
            selectors,
            limit=10
        )
    except Exception as e:
        logger.warning(f"Playwright error: {e}")
        articles = []
    
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{DATA_RAW}/playwright_extract_{timestamp}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False)
    
    logger.info(f"Playwright: {len(articles)} articles extraits")
    
    ti.xcom_push(key="playwright_count", value=len(articles))
    ti.xcom_push(key="playwright_file", value=filepath)
    
    return filepath


def merge_raw_data(ti):
    """Fusionne les données brutes de toutes les sources."""
    import json
    import os
    
    rss_file = ti.xcom_pull(task_ids="extraction_group.extract_rss", key="rss_file")
    reddit_file = ti.xcom_pull(task_ids="extraction_group.extract_reddit", key="reddit_file")
    hackernews_file = ti.xcom_pull(task_ids="extraction_group.extract_hackernews", key="hackernews_file")
    bs4_file = ti.xcom_pull(task_ids="extraction_group.extract_scraper_bs4", key="bs4_file")
    selenium_file = ti.xcom_pull(task_ids="extraction_group.extract_scraper_selenium", key="selenium_file")
    playwright_file = ti.xcom_pull(task_ids="extraction_group.extract_scraper_playwright", key="playwright_file")
    
    all_articles = []
    
    for filepath in [rss_file, reddit_file, hackernews_file, bs4_file, selenium_file, playwright_file]:
        if filepath and os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                articles = json.load(f)
                all_articles.extend(articles)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_file = f"{DATA_RAW}/merged_raw_{timestamp}.json"
    
    with open(merged_file, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False)
    
    logger.info(f"Merge: {len(all_articles)} articles au total")
    
    ti.xcom_push(key="merged_file", value=merged_file)
    ti.xcom_push(key="total_count", value=len(all_articles))
    
    return merged_file


def transform_data(ti):
    """Tâche de transformation/ETL."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    from src.transformation.pipeline import TransformationPipeline
    from src.transformation.cleaner import DataValidator
    
    merged_file = ti.xcom_pull(task_ids="extraction_group.merge_raw", key="merged_file")
    
    if not merged_file:
        logger.error("Aucun fichier à transformer")
        return None
    
    pipeline = TransformationPipeline(
        input_dir=DATA_RAW,
        output_dir=DATA_PROCESSED
    )
    
    import os
    filename = os.path.basename(merged_file)
    
    articles = pipeline.load_raw_data(filename)
    transformed = pipeline.transform(articles)
    output_file = pipeline.save(transformed)
    
    validation = DataValidator.validate_batch(transformed)
    
    logger.info(f"Transformation: {validation['valid']} valides, {validation['multimodal']} multimodaux")
    
    ti.xcom_push(key="transformed_file", value=output_file)
    ti.xcom_push(key="validation", value=validation)
    
    return output_file


def load_to_database(ti):
    """Tâche de chargement en base SQLite."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    from src.transformation.database import DatabaseManager
    
    transformed_file = ti.xcom_pull(task_ids="transform", key="transformed_file")
    
    if not transformed_file:
        logger.warning("Aucun fichier à charger")
        return "Skip"
    
    import json
    with open(transformed_file, "r", encoding="utf-8") as f:
        articles = json.load(f)
    
    db = DatabaseManager(f"{PROJECT_DIR}/data/fakenews.db")
    count = db.insert_articles_batch(articles)
    
    logger.info(f"Base: {count} articles insérés")
    
    return f"Base mise à jour: {count} articles"


def calculate_kpis(ti):
    """Calcule les KPIs."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    rss_count = ti.xcom_pull(task_ids="extraction_group.extract_rss", key="rss_count") or 0
    reddit_count = ti.xcom_pull(task_ids="extraction_group.extract_reddit", key="reddit_count") or 0
    hackernews_count = ti.xcom_pull(task_ids="extraction_group.extract_hackernews", key="hackernews_count") or 0
    bs4_count = ti.xcom_pull(task_ids="extraction_group.extract_scraper_bs4", key="bs4_count") or 0
    selenium_count = ti.xcom_pull(task_ids="extraction_group.extract_scraper_selenium", key="selenium_count") or 0
    playwright_count = ti.xcom_pull(task_ids="extraction_group.extract_scraper_playwright", key="playwright_count") or 0
    total_count = ti.xcom_pull(task_ids="extraction_group.merge_raw", key="total_count") or 0
    validation = ti.xcom_pull(task_ids="transform", key="validation") or {}
    
    start_time = ti.xcom_pull(task_ids="start", key="start_time") or None
    if start_time:
        start_dt = datetime.fromisoformat(start_time)
        exec_time = (datetime.now() - start_dt).total_seconds()
    else:
        exec_time = 0
    
    kpis = {
        "extraction_rss": rss_count,
        "extraction_reddit": reddit_count,
        "extraction_hackernews": hackernews_count,
        "extraction_bs4": bs4_count,
        "extraction_selenium": selenium_count,
        "extraction_playwright": playwright_count,
        "total_raw": total_count,
        "valid_after_clean": validation.get("valid", 0),
        "multimodal": validation.get("multimodal", 0),
        "text_only": validation.get("text_only", 0),
        "success_rate": validation.get("valid", 0) / max(total_count, 1) * 100,
        "execution_time_seconds": round(exec_time, 1),
        "timestamp": datetime.now().isoformat()
    }
    
    import json
    kpi_file = f"{DATA_PROCESSED}/kpis.json"
    
    with open(kpi_file, "w") as f:
        json.dump(kpis, f, indent=2)
    
    logger.info(f"KPIs calculés: {kpis}")
    
    return kpis


with DAG(
    dag_id="fakenews_etl_pipeline",
    default_args=DEFAULT_ARGS,
    description="Pipeline ETL pour l'extraction de données multimodales",
    schedule="0 */2 * * *",
    start_date=datetime(2026, 4, 1),
    catchup=False,
    tags=["fakenews", "etl", "multimodal"]
) as dag:
    
    start = PythonOperator(
        task_id="start",
        python_callable=start_pipeline
    )
    
    with TaskGroup("extraction_group") as extraction:
        extract_rss = PythonOperator(
            task_id="extract_rss",
            python_callable=extract_rss
        )
        
        extract_reddit = PythonOperator(
            task_id="extract_reddit",
            python_callable=extract_reddit
        )
        
        extract_hackernews = PythonOperator(
            task_id="extract_hackernews",
            python_callable=extract_hackernews
        )
        
        extract_scraper_bs4 = PythonOperator(
            task_id="extract_scraper_bs4",
            python_callable=extract_scraper_bs4
        )
        
        extract_scraper_selenium = PythonOperator(
            task_id="extract_scraper_selenium",
            python_callable=extract_scraper_selenium
        )
        
        extract_scraper_playwright = PythonOperator(
            task_id="extract_scraper_playwright",
            python_callable=extract_scraper_playwright
        )
        
        merge_raw = PythonOperator(
            task_id="merge_raw",
            python_callable=merge_raw_data
        )
        
        [extract_rss, extract_reddit, extract_hackernews, extract_scraper_bs4, extract_scraper_selenium, extract_scraper_playwright] >> merge_raw
    
    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_data
    )
    
    load = PythonOperator(
        task_id="load",
        python_callable=load_to_database
    )
    
    kpis = PythonOperator(
        task_id="calculate_kpis",
        python_callable=calculate_kpis
    )
    
    start >> extraction >> transform >> load >> kpis