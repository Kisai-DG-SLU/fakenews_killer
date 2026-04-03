"""
DAG Airflow pour le pipeline d'extraction de données Fake News Killer.

Flow: Extraction → Transformation → Stockage → Métriques
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, BranchPythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.utils.task_group import TaskGroup
from airflow.models import Variable
import logging

# Configuration
DEFAULT_ARGS = {
    "owner": "CheckIt.AI",
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
}

PROJECT_DIR = "/mnt/prod"
DATA_RAW = f"{PROJECT_DIR}/data/raw"
DATA_PROCESSED = f"{PROJECT_DIR}/data/processed"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def extract_rss(**context):
    """Tâche d'extraction RSS."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    from src.extraction.rss_fetcher import RSSFetcher
    
    fetcher = RSSFetcher()
    articles = fetcher.fetch_all(limit_per_feed=15)
    
    # Sauvegarde temporaire
    import json
    from datetime import datetime
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filepath = f"{DATA_RAW}/rss_extract_{timestamp}.json"
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False)
    
    logger.info(f"RSS: {len(articles)} articles extraits")
    
    # Push vers XCom pour transmission
    context["task_instance"].xcom_push(key="rss_count", value=len(articles))
    context["task_instance"].xcom_push(key="rss_file", value=filepath)
    
    return filepath


def extract_reddit(**context):
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
    
    context["task_instance"].xcom_push(key="reddit_count", value=len(all_posts))
    context["task_instance"].xcom_push(key="reddit_file", value=filepath)
    
    return filepath


def merge_raw_data(**context):
    """Fusionne les données brutes de toutes les sources."""
    import json
    import glob
    import os
    
    ti = context["task_instance"]
    
    # Récupère les fichiers des tâches précédentes
    rss_file = ti.xcom_pull(key="rss_file", task_ids="extract_rss")
    reddit_file = ti.xcom_pull(key="reddit_file", task_ids="extract_reddit")
    
    all_articles = []
    
    for filepath in [rss_file, reddit_file]:
        if filepath and os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                articles = json.load(f)
                all_articles.extend(articles)
    
    # Merge
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    merged_file = f"{DATA_RAW}/merged_raw_{timestamp}.json"
    
    with open(merged_file, "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False)
    
    logger.info(f"Merge: {len(all_articles)} articles au total")
    
    context["task_instance"].xcom_push(key="merged_file", value=merged_file)
    context["task_instance"].xcom_push(key="total_count", value=len(all_articles))
    
    return merged_file


def transform_data(**context):
    """Tâche de transformation/ETL."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    from src.transformation.pipeline import TransformationPipeline
    from src.transformation.cleaner import DataValidator
    
    ti = context["task_instance"]
    merged_file = ti.xcom_pull(key="merged_file", task_ids="merge_raw")
    
    if not merged_file:
        logger.error("Aucun fichier à transformer")
        return None
    
    pipeline = TransformationPipeline(
        input_dir=DATA_RAW,
        output_dir=DATA_PROCESSED
    )
    
    # Extraire le nom de fichier
    import os
    filename = os.path.basename(merged_file)
    
    articles = pipeline.load_raw_data(filename)
    transformed = pipeline.transform(articles)
    output_file = pipeline.save(transformed)
    
    # Validation finale
    validation = DataValidator.validate_batch(transformed)
    
    logger.info(f"Transformation: {validation['valid']} valides, {validation['multimodal']} multimodaux")
    
    context["task_instance"].xcom_push(key="transformed_file", value=output_file)
    context["task_instance"].xcom_push(key="validation", value=validation)
    
    return output_file


def load_to_database(**context):
    """Tâche de chargement en base (simulation)."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    ti = context["task_instance"]
    transformed_file = ti.xcom_pull(key="transformed_file", task_ids="transform")
    
    logger.info(f"Chargement en base: {transformed_file}")
    
    # Ici on pourrait ajouter SQLite/PostgreSQL
    # import sqlite3
    # conn = sqlite3.connect("fakenews.db")
    
    return "Données chargées avec succès"


def calculate_kpis(**context):
    """Calcule les KPIs."""
    import sys
    sys.path.insert(0, PROJECT_DIR)
    
    ti = context["task_instance"]
    
    rss_count = ti.xcom_pull(key="rss_count", task_ids="extract_rss") or 0
    reddit_count = ti.xcom_pull(key="reddit_count", task_ids="extract_reddit") or 0
    total_count = ti.xcom_pull(key="total_count", task_ids="merge_raw") or 0
    validation = ti.xcom_pull(key="validation", task_ids="transform") or {}
    
    kpis = {
        "extraction_rss": rss_count,
        "extraction_reddit": reddit_count,
        "total_raw": total_count,
        "valid_after_clean": validation.get("valid", 0),
        "multimodal": validation.get("multimodal", 0),
        "text_only": validation.get("text_only", 0),
        "success_rate": validation.get("valid", 0) / max(total_count, 1) * 100,
        "timestamp": datetime.now().isoformat()
    }
    
    # Sauvegarde KPIs
    import json
    kpi_file = f"{DATA_PROCESSED}/kpis.json"
    
    with open(kpi_file, "w") as f:
        json.dump(kpis, f, indent=2)
    
    logger.info(f"KPIs calculés: {kpis}")
    
    return kpis


# Définition du DAG
with DAG(
    dag_id="fakenews_etl_pipeline",
    default_args=DEFAULT_ARGS,
    description="Pipeline ETL pour l'extraction de données multimodales",
    schedule_interval="0 6,18 * * *",  # 2 fois par jour (6h et 18h)
    start_date=datetime(2026, 4, 1),
    catchup=False,
    tags=["fakenews", "etl", "multimodal"]
) as dag:
    
    # Point de départ
    start = EmptyOperator(task_id="start")
    
    # ==================== EXTRACTION ====================
    with TaskGroup("extraction_group") as extraction:
        extract_rss = PythonOperator(
            task_id="extract_rss",
            python_callable=extract_rss,
            provide_context=True
        )
        
        extract_reddit = PythonOperator(
            task_id="extract_reddit",
            python_callable=extract_reddit,
            provide_context=True
        )
        
        merge_raw = PythonOperator(
            task_id="merge_raw",
            python_callable=merge_raw_data,
            provide_context=True
        )
        
        [extract_rss, extract_reddit] >> merge_raw
    
    # ==================== TRANSFORMATION ====================
    transform = PythonOperator(
        task_id="transform",
        python_callable=transform_data,
        provide_context=True
    )
    
    # ==================== CHARGEMENT ====================
    load = PythonOperator(
        task_id="load",
        python_callable=load_to_database,
        provide_context=True
    )
    
    # ==================== MONITORING ====================
    kpis = PythonOperator(
        task_id="calculate_kpis",
        python_callable=calculate_kpis,
        provide_context=True
    )
    
    # ==================== FLUX ====================
    start >> extraction >> transform >> load >> kpis