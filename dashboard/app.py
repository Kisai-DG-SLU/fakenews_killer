"""
Dashboard Streamlit pour le suivi des KPIs du pipeline Fake News Killer.

Usage: streamlit run dashboard/app.py
"""

import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
from pathlib import Path

# Configuration
DATA_DIR = Path("/workspace/fakenews_killer/data/processed")
RAW_DIR = Path("/workspace/fakenews_killer/data/raw")

st.set_page_config(
    page_title="CheckIt.AI - Dashboard",
    page_icon="📰",
    layout="wide"
)


def load_kpis():
    """Charge les KPIs."""
    kpi_file = DATA_DIR / "kpis.json"
    
    if not kpi_file.exists():
        return {
            "extraction_rss": 0,
            "extraction_reddit": 0,
            "total_raw": 0,
            "valid_after_clean": 0,
            "multimodal": 0,
            "text_only": 0,
            "success_rate": 0,
            "timestamp": datetime.now().isoformat()
        }
    
    with open(kpi_file, "r") as f:
        return json.load(f)


def load_transformed_data():
    """Charge les données transformées."""
    json_files = list(DATA_DIR.glob("transformed_*.json"))
    
    if not json_files:
        return pd.DataFrame()
    
    latest = max(json_files, key=os.path.getmtime)
    
    with open(latest, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    return pd.DataFrame(data)


def load_raw_data():
    """Charge les données brutes du dernier run."""
    merged_files = list(RAW_DIR.glob("merged_raw_*.json"))
    
    if not merged_files:
        return pd.DataFrame()
    
    latest = max(merged_files, key=os.path.getmtime)
    
    with open(latest, "r", encoding="utf-8") as fp:
        data = json.load(fp)
    
    return pd.DataFrame(data)


def main():
    """Dashboard principal."""
    st.title("📰 CheckIt.AI - Fake News Killer")
    st.markdown("**Pipeline d'extraction de données multimodales**")
    
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio(
        "Aller vers:",
        ["KPIs", "Données brutes", "Données transformées", "Monitoring"]
    )
    
    st.sidebar.markdown("---")
    st.sidebar.info("Projet P12 - Formation IA")
    
    # Chargement des données
    kpis = load_kpis()
    
    if page == "KPIs":
        st.header("📊 Indicateurs clés de performance")
        
        # Métriques en haut
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Articles extraits (RSS)",
                kpis.get("extraction_rss", 0),
                delta_color="normal"
            )
        
        with col2:
            st.metric(
                "Posts Reddit",
                kpis.get("extraction_reddit", 0),
                delta_color="normal"
            )
        
        with col3:
            st.metric(
                "Articles multimodaux",
                kpis.get("multimodal", 0),
                delta_color="normal"
            )
        
        with col4:
            st.metric(
                "Taux de réussite",
                f"{kpis.get('success_rate', 0):.1f}%",
                delta_color="normal"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            exec_time = kpis.get('execution_time_seconds', 0)
            st.metric(
                "Temps d'exécution",
                f"{exec_time:.1f}s" if exec_time > 0 else "N/A"
            )
        with col2:
            st.metric(
                "Articles valides",
                kpis.get('valid_after_clean', 0)
            )
        
        st.markdown("---")
        
        # Graphiques
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Répartition des données")
            if kpis.get("total_raw", 0) > 0:
                chart_data = pd.DataFrame({
                    "Catégorie": ["Multimodaux", "Texte seul", "Filtrés"],
                    "Nombre": [
                        kpis.get("multimodal", 0),
                        kpis.get("text_only", 0),
                        kpis.get("total_raw", 0) - kpis.get("valid_after_clean", 0)
                    ]
                })
                st.bar_chart(chart_data.set_index("Catégorie"))
            else:
                st.info("Aucune donnée disponible. Exécutez d'abord le pipeline.")
        
        with col2:
            st.subheader("Sources d'extraction")
            df = load_transformed_data()
            if not df.empty and "source" in df.columns:
                source_counts = df["source"].value_counts().reset_index()
                source_counts.columns = ["Source", "Articles"]
                st.bar_chart(source_counts.set_index("Source"))
            elif kpis.get("total_raw", 0) > 0:
                sources_data = pd.DataFrame({
                    "Source": ["RSS", "Reddit"],
                    "Articles": [kpis.get("extraction_rss", 0), kpis.get("extraction_reddit", 0)]
                })
                st.bar_chart(sources_data.set_index("Source"))
        
        # Timestamp
        st.markdown("---")
        st.caption(f"Dernière mise à jour: {kpis.get('timestamp', 'N/A')}")
    
    elif page == "Données brutes":
        st.header("📥 Données brutes extraites")
        
        df_raw = load_raw_data()
        
        if df_raw.empty:
            st.warning("Aucune donnée brute disponible.")
        else:
            st.write(f"**Total: {len(df_raw)} articles**")
            
            # Filtres
            col1, col2 = st.columns(2)
            with col1:
                type_filter = st.multiselect(
                    "Filtrer par type",
                    options=df_raw["type"].unique() if "type" in df_raw else []
                )
            with col2:
                source_filter = st.multiselect(
                    "Filtrer par source",
                    options=df_raw["source"].unique() if "source" in df_raw else []
                )
            
            if type_filter:
                df_raw = df_raw[df_raw["type"].isin(type_filter)]
            if source_filter:
                df_raw = df_raw[df_raw["source"].isin(source_filter)]
            
            st.dataframe(
                df_raw[["title", "source", "type", "published_at"]].head(200),
                width='stretch'
            )
    
    elif page == "Données transformées":
        st.header("✅ Données transformées et nettoyées")
        
        df_transformed = load_transformed_data()
        
        if df_transformed.empty:
            st.warning("Aucune donnée transformée disponible.")
        else:
            st.write(f"**Total: {len(df_transformed)} articles**")
            
            # Statistiques
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Articles multimodaux",
                    len(df_transformed[df_transformed.get("is_multimodal", False) == True])
                )
            
            with col2:
                st.metric(
                    "Articles texte seul",
                    len(df_transformed[df_transformed.get("is_multimodal", False) == False])
                )
            
            with col3:
                avg_words = df_transformed["word_count"].mean() if "word_count" in df_transformed else 0
                st.metric("Mots moy./article", f"{avg_words:.0f}")
            
            # Affichage
            st.dataframe(
                df_transformed[[
                    "title", "source", "is_multimodal", "word_count", "keywords"
                ]].head(100),
                width='stretch'
            )
        
        # Tableau classification
        st.subheader("Classification des articles")
        
        if not df_transformed.empty and "classification" in df_transformed.columns:
            df_class = df_transformed["classification"].apply(pd.Series)
            class_counts = df_class["category"].value_counts().reset_index()
            class_counts.columns = ["Catégorie", "Nombre"]
            
            st.dataframe(class_counts, width='stretch')
            
            # Stats nettoyés vs bruts
            st.subheader("Articles nettoyés")
            st.write(f"Bruts: {int(kpis.get('total_raw', 0))} → Valides: {int(kpis.get('valid_after_clean', 0))} (rejet és: {int(kpis.get('total_raw', 0) - kpis.get('valid_after_clean', 0)))")
            
            # Par source
            st.subheader("Par source")
            source_stats = df_transformed.groupby("source").agg({
                "title": "count",
                "is_multimodal": "sum"
            }).rename(columns={"title": "Total", "is_multimodal": "Multimodal"})
            st.dataframe(source_stats, width='stretch')
        else:
            st.info("Aucune classification disponible.")
    
    elif page == "Monitoring":
        st.header("🔍 Monitoring du pipeline")
        
        # État du système
        st.subheader("État des composants")
        
        # Vérification des fichiers
        raw_files = len(list(RAW_DIR.glob("*.json")))
        processed_files = len(list(DATA_DIR.glob("*.json")))
        
        col1, col2 = st.columns(2)
        
        with col1:
            status = "✅" if raw_files > 0 else "❌"
            st.write(f"{status} Données brutes: {raw_files} fichiers")
        
        with col2:
            status = "✅" if processed_files > 0 else "❌"
            st.write(f"{status} Données traitées: {processed_files} fichiers")
        
        # Logs
        st.subheader("Derniers logs")
        
        if kpis.get("timestamp"):
            st.code(f"""
Timestamp: {kpis['timestamp']}
RSS: {kpis.get('extraction_rss', 0)} articles
Reddit: {kpis.get('extraction_reddit', 0)} articles
Total brut: {kpis.get('total_raw', 0)}
Valides: {kpis.get('valid_after_clean', 0)}
Multimodaux: {kpis.get('multimodal', 0)}
Taux réussite: {kpis.get('success_rate', 0):.1f}%
            """, language="text")
        
        # Plan de monitoring
        st.markdown("---")
        st.subheader("📋 Plan de monitoring")
        
        monitoring_plan = """
| Métrique | Objectif | Alerte si |
|----------|----------|-----------|
| Temps d'exécution | < 5 min | > 10 min |
| Articles extraits | > 50 | < 20 |
| Taux de validité | > 80% | < 50% |
| Articles multimodaux | > 30% | < 10% |
        """
        st.markdown(monitoring_plan)


if __name__ == "__main__":
    main()