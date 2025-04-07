# US-30 Live Dashboard

Ce projet fournit un tableau de bord interactif pour visualiser en temps réel l'évolution de l'indice boursier **US-30 (Dow Jones)**. Il est conçu avec **Dash (Plotly)**, met à jour automatiquement les données via un cron job sur Render, et propose de nombreuses options d'affichage pour l'analyse visuelle.

---

## 📉 Fonctionnalités principales

- **Graphique dynamique** (ligne ou chandelier)
- **Sélecteur de période** : 1h, 6h, 12h, 1j, tout
- **Statistiques du jour** : open, close, min, max, moyenne, volatilite
- **Zone de volatilité** : bande autour de la moyenne
- **Tendance naïve** : prévision par régression linéaire
- **SMA (1h)** : moyenne mobile sur une heure
- **Anomalies** : détection de pics statistiques
- **Mode clair / sombre** synchronisé avec le style du graphe
- **Historique journalier** : récap des derniers jours (clôture + volatilite)
- **Export** CSV & PNG du graphe
- **Footer** avec liens GitHub et source Investing.com

---

## 🌐 Démo en ligne
Le site est déployé sur **Render** : [https://live-dashboard-project.onrender.com/](https://live-dashboard-project.onrender.com/)

---

## 🚀 Installation locale
```bash
# 1. Cloner le repo
https://github.com/GaetanAm/live-dashboard-project.git
cd live-dashboard-project

# 2. Installer les dépendances
pip install -r requirements.txt

# 3. Lancer l'app localement
python dashboard.py
```

---

## 📊 Données
- `data.csv` : données temps réel US-30 (timestamp, prix)
- `report.json` : fichier généré automatiquement avec statistiques journalières

Un script `generate_report.py` est exécuté automatiquement tous les jours à 20h via un **cron job Render** et push les fichiers à ce repo GitHub.

---

## 📄 Fichiers importants

| Fichier | Rôle |
|--------|------|
| `dashboard.py` | Code principal du dashboard |
| `data.csv` | Historique des données |
| `report.json` | Rapport quotidien généré |
| `assets/style.css` | Personnalisation claire/sombre |

---

## 🧱 Réalisé par
Projet réalisé par [@GaetanAm](https://github.com/GaetanAm) dans le cadre d'un projet d'application de data visualisation et de scraping.

Source données : [Investing.com - US-30 Index](https://www.investing.com/indices/us-30)

---

## 🚧 Idées futures
- Ajout de prévisions via modèles avancés (ARIMA, Prophet...)
- Comparaison avec d'autres indices (S&P 500, Nasdaq...)
- Ajout d'indicateurs techniques (RSI, MACD)

---

## 📅 Mises à jour
- Avril 2025 : Version initiale, thèmes personnalisés, filtres dynamiques, déploiement Render, graphes évolués.

---

## ✉️ Contact
Pour toute question : via [GitHub](https://github.com/GaetanAm)

---

Merci d'avoir exploré ce projet!

