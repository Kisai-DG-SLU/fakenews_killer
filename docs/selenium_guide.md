# Guide d'installation et d'exécution de Selenium

## Prérequis

### Installation de Chrome/Chromedriver

#### Ubuntu/Debian
```bash
sudo apt update
sudo apt install chromium chromium-driver
```

#### macOS
```bash
brew install chromium
brew install chromedriver
```

#### Windows
Télécharger Chrome depuis https://www.google.com/chrome/
Télécharger chromedriver depuis https://chromedriver.chromium.org/

## Vérification de l'installation

```bash
# Vérifier Chrome
google-chrome --version

# Vérifier Chromedriver
chromedriver --version
```

## Exécution du script Selenium

### Méthode 1: Avec Python direct

```bash
cd /mnt/prod
pip install selenium webdriver-manager

python -c "
from src.extraction.scraper_selenium import SeleniumScraper
scraper = SeleniumScraper(headless=False)  # Mode visible pour test
articles = scraper.scrape_dynamic_site(
    'https://www.bfmtv.com/',
    article_selector='article',
    limit=5
)
print(f'Articles: {len(articles)}')
"
```

### Méthode 2: Mode headless (sans interface graphique)

```python
from src.extraction.scraper_selenium import SeleniumScraper

scraper = SeleniumScraper(headless=True)  # Mode sans interface
articles = scraper.scrape_dynamic_site(
    'https://www.bfmtv.com/',
    article_selector='article',
    limit=10
)
```

### Mode debug

Pour voir ce que fait le navigateur :

```python
scraper = SeleniumScraper(headless=False, slow_mode=True)
```

## Dépannage

### Erreur "Chrome not reachable"
- Vérifier que Chrome et Chromedriver ont la même version
- Utiliser webdriver-manager pour gérer automatiquement les versions

### Erreur "Session not created"
- Mettre à jour Chrome : `sudo apt upgrade google-chrome-stable`
- OU utiliser webdriver-manager (voir ci-dessous)

### Solution automatique avec webdriver-manager

```python
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)
```

## Intégration au pipeline

Le script Selenium peut être intégré au pipeline d'extraction :

```python
from src.extraction.scraper_selenium import SeleniumScraper

# Créer une instance
scraper = SeleniumScraper(headless=True)

# Intégrer dans le flux
articles = await scraper.scrape_dynamic_site(
    url="https://site-dynamique.com",
    article_selector=".article",
    limit=10
)

# Les articles sont au même format que les autres sources
# et peuvent être ajoutés au pipeline de transformation
```