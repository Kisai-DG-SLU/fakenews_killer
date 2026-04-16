#!/bin/bash
# Script de démarrage pour Airflow avec historique KPI
# Usage: ./run_airflow.sh

set -e

echo "=== Initialisation Airflow ==="

# Initialiser la DB si nécessaire
pixi run airflow db init 2>/dev/null || true

# Copier le DAG dans le dossier Airflow
mkdir -p /mnt/prod/airflow/dags
cp /mnt/prod/dags/fakenews_pipeline.py /mnt/prod/airflow/dags/

echo "DAG copié dans /mnt/prod/airflow/dags/"
echo ""
echo "=== Démarrage des services ==="

# Lancer le scheduler en background
echo "Démarrage du scheduler..."
pixi run airflow scheduler --dag-directory /mnt/prod/airflow/dags &
SCHEDULER_PID=$!
echo "Scheduler PID: $SCHEDULER_PID"

sleep 3

# Lancer le webserver en background
echo "Démarrage du webserver..."
pixi run airflow webserver --port 8080 &
WEBSERVER_PID=$!
echo "Webserver PID: $WEBSERVER_PID"

echo ""
echo "=== Airflow démarré ==="
echo "  Web UI: http://localhost:8080"
echo "  DAG: fakenews_etl_pipeline"
echo ""
echo "Pour arrêter: kill $SCHEDULER_PID $WEBSERVER_PID"

# Garder le script alive
wait