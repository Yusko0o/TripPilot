# TripPilot

Application full-stack de préparation de voyage : recherche de vols, météo,
hôtels, activités et favoris personnels.

## Fonctionnalités du MVP

- Recherche de trajet puis redirection vers Luxair, Air France et Ryanair
- Autocomplétion de près de 7 900 aéroports par code, ville ou nom
- Redirection des vols vers le site officiel de leur compagnie
- Redirection des hôtels et activités vers une page de réservation/recherche
- Interface complète en français et en anglais
- Mode sombre mémorisé dans le navigateur
- Météo actuelle en direct via Open-Meteo
- 10 hôtels et 5 activités de démonstration par destination
- Détection de l'aéroport proche avec l'autorisation de localisation du navigateur
- Aucune position enregistrée par le serveur
- Pages séparées d'inscription et de connexion, sécurisées par session
- Favoris de vols et de destinations
- Aucune clé nécessaire pour les vols, la météo ou la localisation
- Protection CSRF, validation des entrées, hachage `scrypt`, cookies sécurisés
  et requêtes SQL paramétrées par SQLAlchemy

## Lancer le projet

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows : .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
python run.py
```

L'API démarre sur `http://localhost:5000`.

Sous Windows PowerShell, utilise plutôt :

```powershell
cd backend
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
python run.py
```

### Frontend

Dans un second terminal :

```bash
cd frontend
npm install
npm run dev
```

Ouvrir ensuite `http://localhost:5173`. Vite transmet automatiquement `/api`
au backend Flask, y compris les cookies de session.

## Tests

```bash
cd backend
pytest
```

```bash
cd frontend
npm run build
```

## Fonctionnement de la recherche de vols

TripPilot prépare le trajet, la date et le nombre de voyageurs, puis propose
les sites officiels de Luxair, Air France et Ryanair. Les horaires et prix ne
sont pas inventés dans l'application : ils sont consultés sur le site de la
compagnie choisie.

Avant toute mise en production, remplace `SECRET_KEY` dans `.env` par une
valeur aléatoire longue et configure `FLASK_ENV=production`. Tu peux générer
une clé avec :

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## Destinations et météo

La recherche reconnaît les codes IATA, les villes et les noms d'aéroport. Par
exemple, `NYC` ou `New Y` propose les aéroports de New York. Le départ par
défaut est `LUX`. La météo est obtenue en direct. Les hôtels et activités sont
des suggestions de démonstration et ouvrent une recherche externe.

Le bouton « Utiliser mon aéroport le plus proche » emploie la fonctionnalité de
localisation intégrée au navigateur. La position est envoyée uniquement le
temps de calculer la distance avec les aéroports et n'est pas enregistrée.

## Déploiement gratuit : Render + Neon

Le frontend React est compilé puis servi par Flask sur le même domaine. Cela
évite une configuration CORS et permet aux cookies sécurisés et à la protection
CSRF de fonctionner simplement.

### 1. Créer la base PostgreSQL gratuite

1. Crée un compte sur [Neon](https://console.neon.tech/) et un projet.
2. Dans **Connect**, copie la chaîne de connexion PostgreSQL complète. Elle
   commence par `postgresql://` et doit contenir `sslmode=require`.
3. Ne publie jamais cette valeur et ne l'ajoute jamais dans Git.

### 2. Mettre le projet sur GitHub

Crée un dépôt GitHub puis, depuis le dossier TripPilot :

```bash
git init
git add .
git commit -m "Prepare TripPilot deployment"
git branch -M main
git remote add origin https://github.com/TON-COMPTE/TON-DEPOT.git
git push -u origin main
```

### 3. Déployer sur Render

1. Sur [Render](https://dashboard.render.com/), choisis **New > Blueprint**.
2. Connecte le dépôt GitHub. Render détectera automatiquement `render.yaml`.
3. Lorsqu'il demande `DATABASE_URL`, colle la chaîne de connexion Neon.
4. Lance le déploiement. `SECRET_KEY` est générée automatiquement par Render.
5. Ouvre l'adresse gratuite `https://tripilot-....onrender.com`.

Le endpoint `https://TON-SITE.onrender.com/api/health` doit répondre avec
`{"status":"ok","service":"TripPilot API"}`.

### Vérification locale du mode production

```bash
npm ci --prefix frontend
npm run build --prefix frontend
pip install -r backend/requirements.txt
gunicorn --chdir backend --workers 1 --threads 4 run:app
```

Ouvre ensuite `http://localhost:8000`. En développement, SQLite reste utilisée
si `DATABASE_URL` n'est pas définie.
