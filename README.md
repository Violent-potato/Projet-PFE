# Projet PFE — Import et extraction de CV

Le projet contient :
- une interface web React/Vite
- une API FastAPI
- un module Python d'extraction de texte depuis des fichiers PDF et DOCX

## Structure du projet

```text
Projet-PFE/
├── upload-doc/
│   ├── src/                 # interface frontend
│   ├── backend/
│   ├── package.json
│   └── README.md
├── extraction-cv/
│   ├── extractor.py         # extraction PDF/DOCX
│   ├── main.py              # usage CLI
│   ├── test_extractor.py    # tests Python
│   └── requirements.txt     # dépendances de l'extracteur + tests
├── requirements.txt         # dépendances de l'API
├── test-requirements.txt   # installation complète pour dev/tests
├── README.md
└── .venv/
```

## Prérequis

- Python 3.10+
- Node.js 18+ et npm
- Git (optionnel)

## Installation

Créer et activer l'environnement virtuel puis installer les dépendances du projet :

```powershell
cd .\Projet-PFE
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r .\test-requirements.txt
```

Le fichier `test-requirements.txt` regroupe les dépendances nécessaires à l'API,
à l'extracteur et aux tests.

Installer ensuite les dépendances du frontend :

```powershell
cd .\upload-doc
npm install
cd ..
```

## Lancement en développement

Ouvrez deux terminaux depuis la racine du projet.

### Terminal 1 — API

```powershell
cd .\upload-doc
python -m uvicorn backend.main:app --reload --port 8000
```

L'API est accessible sur :
- http://127.0.0.1:8000
- http://127.0.0.1:8000/docs

### Terminal 2 — Frontend

```powershell
cd .\upload-doc
npm run dev
```

Puis ouvrez l'URL locale affichée par Vite, généralement :
- http://localhost:5173

## Tests

### Tests Python du module d'extraction

```powershell
python -m pytest .\extraction-cv -v
```

### Tests API

```powershell
python -m pytest .\upload-doc\backend -v
```

### Tests complets

```powershell
python -m pytest .\extraction-cv .\upload-doc\backend -v
```

## Vérification manuelle

### Vérification de santé de l'API

```powershell
curl.exe -i http://127.0.0.1:8000/health
```

Réponse attendue :

```json
{"status":"ok"}
```

### Upload d'un CV

```powershell
curl.exe -i -F "file=@C:\chemin\vers\cv.pdf" http://127.0.0.1:8000/cv/upload
```

Exemple avec un fichier DOCX :

```powershell
curl.exe -i -F "file=@C:\chemin\vers\cv.docx" http://127.0.0.1:8000/cv/upload
```

## Vérification du frontend

Dans `upload-doc` :

```powershell
npm run lint
npm run build
```

## Règles de dépendances

Les dépendances sont séparées selon leur rôle :
- `requirements.txt` : API/backend
- `extraction-cv/requirements.txt` : extraction PDF/DOCX + tests Python
- `test-requirements.txt` : installation complète pour le développement local et les tests

Cela évite d'avoir des bibliothèques dupliquées dans plusieurs fichiers et garde le projet plus lisible.

## Flux complet de validation

1. Installer les dépendances
2. Lancer l'API
3. Lancer le frontend
4. Uploader un fichier PDF ou DOCX
5. Vérifier le texte extrait dans l'interface
6. Vérifier les cas d'erreur : fichier invalide, trop volumineux, vide ou non extractible

## Commandes utiles

```powershell
# créer l'environnement
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# installer les dépendances complètes
python -m pip install -r .\test-requirements.txt

# lancer l'API
cd .\upload-doc
python -m uvicorn backend.main:app --reload --port 8000

# lancer le frontend
cd .\upload-doc
npm run dev

# linter + build frontend
cd .\upload-doc
npm run lint
npm run build

# tests Python
python -m pytest .\extraction-cv .\upload-doc\backend -v
```

