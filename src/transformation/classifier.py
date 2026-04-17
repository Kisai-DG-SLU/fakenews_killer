"""
Module de classification Opinion vs Désinformation.

Ce module analyse les articles pour distinguer les opinions controversées
des contenus potentiellement trompeurs (désinformation).
"""

import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ContentClassifier:
    """Classifieur de contenu pour détecter Opinion vs Désinformation."""
    
    # Indicateurs d'opinion controversée (sources identifiées, intention assumée)
    OPINION_INDICATORS = {
        "positive": [
            "selon", "d'après", "estime", "considère", "affirme",
            "déclare", "explique", "précise", "ajoute",
            "éditorial", "chronique", "tribune", "opinion",
            "point de vue", "analyse", "perspective"
        ],
        "sources_connues": [
            "le figaro", "le monde", "le point", "20 minutes",
            "france info", "france inter", "bfmtv", "euronews",
            "reuters", "afp", "associated press", "bbc",
            "nouvel obs", "lobs", "20 minutes"
        ]
    }
    
    # Indicateurs de désinformation potentielle
    DISINFO_INDICATORS = {
        "alerte": [
            "urgent", "breaking", "exclusif", "scandale",
            "choc", "incroyable", "inacceptable", "trahison",
            "complot", "secret", "caché", "manipulation",
            "code red", "alerte maximale"
        ],
        "emotions": [
            "haine", "colère", "peur", "panique",
            "faux", "mensonge", "tromperie", "fake"
        ],
        "sources_inconnues": [
            "selon une source", "d'après des sources",
            "on apprend que", "il parait que",
            "buzz", "viral", "sensationnel"
        ],
        "absence_verification": [
            "n'a pas pu être vérifié", "ne peut être confirmé",
            "en attente de vérification", "à confirmer"
        ],
        "sources_douteuses": [
            "breitbart", "infowars", "gateway pundit",
            "zerohedge", "alex jones", "rebel news"
        ]
    }
    
    def __init__(self):
        self.stats = {
            "opinion": 0,
            "desinformation": 0,
            "neutre": 0,
            "indetermine": 0
        }
    
    def classify(self, article: dict) -> dict:
        """
        Classifie un article comme opinion, désinformation, ou neutre.
        
        Args:
            article: Dictionary avec title, description, content, source
            
        Returns:
            Classification result avec:
            - category: "opinion" | "desinformation" | "neutre" | "indetermine"
            - confidence: float (0-1)
            - reasons: list[str]原因
            - flags: list[str]indicateurs trouvés
        """
        title = article.get("title", "").lower()
        description = article.get("description", "").lower()
        content = article.get("content", "").lower()
        source = article.get("source", "").lower()
        
        text = f"{title} {description} {content}"
        
        # Calcul des scores
        opinion_score = self._calculate_opinion_score(text, source)
        disinfo_score = self._calculate_disinfo_score(text, source)
        
        # Détermination de la catégorie
        if opinion_score > 0.3 and disinfo_score < 0.4:
            category = "opinion"
            confidence = min(opinion_score + 0.2, 1.0)
            self.stats["opinion"] += 1
        elif disinfo_score > 0.5:
            category = "desinformation"
            confidence = min(disinfo_score, 1.0)
            self.stats["desinformation"] += 1
        elif disinfo_score > 0.3 or opinion_score > 0.2:
            category = "neutre"
            confidence = 0.5
            self.stats["neutre"] += 1
        else:
            category = "indetermine"
            confidence = 0.3
            self.stats["indetermine"] += 1
        
        return {
            "category": category,
            "confidence": round(confidence, 2),
            "opinion_score": round(opinion_score, 2),
            "disinfo_score": round(disinfo_score, 2),
            "extracted_at": datetime.now().isoformat(),
            "type": "classification"
        }
    
    def _calculate_opinion_score(self, text: str, source: str) -> float:
        """Calcule le score d'opinion."""
        score = 0.0
        factors = 0
        
        # Normaliser source (remplacer _ par espace pour matcher)
        source_normalized = source.lower().replace("_", " ")
        
        # Source connue (média identifié)
        for known_source in self.OPINION_INDICATORS["sources_connues"]:
            if known_source in source_normalized:
                score += 0.3
                factors += 1
                break
        
        # Indicateurs d'opinion
        for indicator in self.OPINION_INDICATORS["positive"]:
            if indicator in text:
                score += 0.15
                factors += 1
        
        # Présence de l'auteur
        if "par" in text and any(x in text for x in ["journaliste", "auteur", "par"]):
            score += 0.1
        
        return min(score, 1.0) if factors > 0 else 0.0
    
    def _calculate_disinfo_score(self, text: str, source: str) -> float:
        """Calcule le score de désinformation potentielle."""
        score = 0.0
        factors = 0
        
        # Source inconnue
        unknown_patterns = ["source anonym", "on apprend", "il parait"]
        if any(p in text for p in unknown_patterns):
            score += 0.25
            factors += 1
        
        # Indicateurs émotionnels/sensationnalistes
        for indicator in self.DISINFO_INDICATORS["alerte"]:
            if indicator in text:
                score += 0.2
                factors += 1
        
        # Indicateurs de désinformation
        for indicator in self.DISINFO_INDICATORS["emotions"]:
            if indicator in text:
                score += 0.15
                factors += 1
        
        # Pas de vérification
        for indicator in self.DISINFO_INDICATORS["absence_verification"]:
            if indicator in text:
                score += 0.3
                factors += 1
        
        # URL inhabituelle (domaine peu connu)
        suspicious_domains = [".xyz", ".top", ".gq", ".tk", ".ml"]
        if any(d in source for d in suspicious_domains):
            score += 0.4
            factors += 1
        
        # Sources douteuses (listes connues de désinformation)
        source_normalized = source.lower().replace("_", " ")
        for doubtful_source in self.DISINFO_INDICATORS["sources_douteuses"]:
            if doubtful_source in source_normalized:
                score += 0.35
                factors += 1
                break
        
        return min(score, 1.0) if factors > 0 else 0.0
    
    def classify_batch(self, articles: list[dict]) -> list[dict]:
        """Classifie une liste d'articles."""
        results = []
        for article in articles:
            classification = self.classify(article)
            # Ajouter la classification à l'article
            article_with_class = article.copy()
            article_with_class["classification"] = classification
            results.append(article_with_class)
        
        logger.info(f"Classification: {self.stats}")
        return results
    
    def get_stats(self) -> dict:
        """Retourne les statistiques de classification."""
        return self.stats.copy()


class EthicalAnalyzer:
    """Analyseur éthique pour la distinction Opinion vs Désinformation."""
    
    @staticmethod
    def analyze_source(source: str) -> dict:
        """
        Analyse une source pour déterminer sa fiabilité.
        
        Returns:
            - reliability: "high" | "medium" | "low" | "unknown"
            - type: "established_media" | "social_media" | "unknown"
            - reasons: list[str]
        """
        established_media = [
            "le figaro", "le monde", "le point", "20 minutes",
            "france info", "france inter", "france tv",
            "bfmtv", "m6", "tf1", "euronews",
            "reuters", "afp", "associated press", "bbc",
            "nyt", "washington post", "guardian"
        ]
        
        social_media = [
            "reddit", "twitter", "facebook", "instagram",
            "tiktok", "youtube", "linkedin"
        ]
        
        source_lower = source.lower()
        
        # Check established media
        for media in established_media:
            if media in source_lower:
                return {
                    "reliability": "high",
                    "type": "established_media",
                    "reasons": [f"Source connue: {media}"]
                }
        
        # Check social media
        for social in social_media:
            if social in source_lower:
                return {
                    "reliability": "medium",
                    "type": "social_media",
                    "reasons": [f"Source: {social} - vérifier les informations"]
                }
        
        # Unknown
        return {
            "reliability": "unknown",
            "type": "unknown",
            "reasons": ["Source non identifiée - nécessite vérification"]
        }
    
    @staticmethod
    def generate_report(articles: list[dict]) -> str:
        """Génère un rapport éthique sur les articles analysés."""
        classifier = ContentClassifier()
        classified = classifier.classify_batch(articles)
        
        stats = classifier.get_stats()
        
        report = """# Rapport d'Analyse Éthique

## Résumé de la classification

| Catégorie | Nombre | Pourcentage |
|-----------|--------|-------------|
| Opinion controversée | {opinion} | {opinion_pct:.1f}% |
| Désinformation potentielle | {desinformation} | {desinfo_pct:.1f}% |
| Neutre | {neutre} | {neutre_pct:.1f}% |
| Indéterminé | {indetermine} | {indet_pct:.1f}% |

## Analyse

""".format(
            opinion=stats["opinion"],
            opinion_pct=stats["opinion"]/len(articles)*100 if articles else 0,
            desinformation=stats["desinformation"],
            desinfo_pct=stats["desinformation"]/len(articles)*100 if articles else 0,
            neutre=stats["neutre"],
            neutre_pct=stats["neutre"]/len(articles)*100 if articles else 0,
            indetermine=stats["indetermine"],
            indet_pct=stats["indetermine"]/len(articles)*100 if articles else 0
        )
        
        # Ajouter les articles suspects
        suspects = [a for a in classified if a.get("classification", {}).get("category") == "desinformation"]
        if suspects:
            report += "\n## Articles potentiellement problématiques\n\n"
            for a in suspects[:10]:
                report += f"- **{a.get('title', 'Sans titre')}** (score: {a.get('classification', {}).get('disinfo_score', 0)})\n"
        
        return report


def main():
    """Test du classifier."""
    test_articles = [
        {
            "title": "Le gouvernement annonce une nouvelle réforme",
            "description": "Selon le Premier ministre, cette réforme devrait améliorer le quotidien des Français. Il a déclaré lors d'une conférence de presse que...",
            "source": "le_monde",
            "content": ""
        },
        {
            "title": "SCANDALE: Le gouvernement cache la vérité!",
            "description": "Des sources anonymes révèlent que le gouvernement ment depuis des années. Personne ne peut confirmer ces informations.",
            "source": "inconnu.xyz",
            "content": ""
        }
    ]
    
    classifier = ContentClassifier()
    for article in test_articles:
        result = classifier.classify(article)
        print(f"Article: {article['title'][:50]}...")
        print(f"  Catégorie: {result['category']} (confiance: {result['confidence']})")
        print(f"  Opinion: {result['opinion_score']}, Disinfo: {result['disinfo_score']}")
        print()


if __name__ == "__main__":
    main()