# BRVM Scraper API

Cette API Flask scrape les données des actions de la BRVM et les retourne au format JSON.

## Installation et Exécution Locale

1. Installez les dépendances :
   ```
   pip install -r requirements.txt
   ```

2. Lancez l'application :
   ```
   python app.py
   ```

L'API sera disponible sur `http://localhost:5000/stocks`.

## Déploiement avec Docker

### Avec Docker Compose (recommandé)

1. Construisez et lancez l'application :
   ```
   docker-compose up --build
   ```

2. L'API sera disponible sur `http://localhost:5000/stocks`.

### Avec Docker seul

1. Construisez l'image :
   ```
   docker build -t brvm-api .
   ```

2. Lancez le conteneur :
   ```
   docker run -p 5000:5000 brvm-api
   ```

## Cache

L'API utilise un cache de 5 minutes pour éviter les requêtes répétées vers le site BRVM.

## Endpoints

- `GET /stocks` : Retourne les données des stocks au format JSON avec la date de mise à jour.
