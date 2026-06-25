# 💼 AI CV Analyzer & Smart Improver Pro

Une application web puissante et intelligente basée sur l'IA (**Gemini 1.5 Flash**) qui permet d'analyser l'adéquation entre un CV (au format PDF) et une offre d'emploi spécifique. L'application intègre également un outil de réécriture dynamique pour optimiser les sections de son CV pour les systèmes ATS (Applicant Tracking System).

🚀 **Lien de l'application en production :** [https://cv-analyzer-6vinyxbkxua6wd5xlj57kc.streamlit.app/](https://cv-analyzer-6vinyxbkxua6wd5xlj57kc.streamlit.app/)

---

## ✨ Fonctionnalités

- **📄 Extraction de Texte PDF :** Extraction automatique et fluide du contenu des CV grâce à `pdfplumber`.
- **📊 Score de Correspondance ATS :** Évaluation instantanée et précise (en %) de la compatibilité du candidat avec le poste visé.
- **✅ Points Forts & Manques :** Identification claire des compétences clés validées et des technologies manquantes par rapport à la Job Description.
- **💡 Suggestions Prêtes à l'Emploi :** Recommandations concrètes générées par l'IA sous forme de blocs de code faciles à copier directement dans son CV.
- **🛠️ Smart Improver (Outil Sur-Mesure) :** Collez n'importe quelle section textuelle de votre CV actuel, choisissez un objectif (ex: intégrer des mots-clés, rendre plus percutant) et l'IA reformule le texte instantanément de manière professionnelle.
- **🛡️ Fallback Automatique :** Système de bascule automatique vers `gemini-1.5-flash` en cas de forte charge ou d'indisponibilité temporaire des serveurs de Google (Erreur 503).

---

## 🛠️ Technologies Utilisées

- **Python 3.11+**
- **Streamlit** (Interface utilisateur et déploiement Cloud)
- **Google GenAI SDK** (Intégration des modèles Gemini)
- **Pdfplumber** (Parsing et extraction de fichiers PDF)

---

## 📦 Installation et Lancement en Local

Pour exécuter ce projet sur votre machine locale, suivez ces étapes :

### 1. Cloner le projet
```bash
git clone https://github.com/khouloudaoued/cv-analyzer.git
cd cv-analyzer
