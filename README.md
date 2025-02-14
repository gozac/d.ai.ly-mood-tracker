# Daily Mood Tracker

Une application web permettant aux utilisateurs de suivre leur humeur quotidienne et de recevoir des analyses personnalisées grâce à l'IA.

Une demo est disponible sur : https://daily-tracker.up.railway.app

## 🚀 Fonctionnalités

- Authentification utilisateur
- Formulaire quotidien de suivi d'humeur
- Analyse IA des réponses
- Historique des rapports
- Interface responsive et moderne

## 🛠 Technologies Utilisées

- React
- TypeScript
- Flask
- OpenAI API
- SCSS & Bootstrap 5
- React Router v6
- Axios

## 📋 Prérequis

- Node.js (v14 ou supérieur)
- Python 3.8+
- Clé API OpenAI

## 🔧 Installation

1. **Cloner le repository**
```bash
git clone https://github.com/gozac/d.ai.ly-mood-tracker
cd daily-mood-tracker
```

2. **Installation des dépendances Frontend**
```bash
cd frontend
npm install
```

3. Installation des dépendances Backend
```
cd backend
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
pip install -r requirements.txt
```

4. Configuration des variables d'environnement

Créez un fichier .env dans le dossier frontend :
```
REACT_APP_API_URL=http://localhost:5000
```
Créez un fichier .env dans le dossier backend :
```
FLASK_APP=app.py
FLASK_ENV=development
OPENAI_API_KEY=votre-clé-api
SECRET_KEY=votre-clé-secrète
JWT_KEY=cle-secrete
```

## 🚀 Démarrage

1. Lancer le Backend
```
cd backend
flask run
```

2. Lancer le Frontend
```
cd frontend
npm start
```

L'application sera accessible à l'adresse : http://localhost:5000

## 📝 Structure du Projet

```
daily-mood-tracker/
├── frontend/          # Application React
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── styles/
│   └── public/
└── backend/          # API Flask
    ├── app.py
    └── requirements.txt
```

## 🔒 Sécurité

- Authentification par token JWT
- Hachage des mots de passe
- Protection CSRF
- Validation des données

## 🤝 Contribution

1. Forkez le projet
2. Créez votre branche (git checkout -b feature/AmazingFeature)
3. Committez vos changements (git commit -m 'Add some AmazingFeature')
4. Pushez vers la branche (git push origin feature/AmazingFeature)
5. Ouvrez une Pull Request

## 👥 Contact

Bakayoko Isaac - https://www.linkedin.com/in/gozac