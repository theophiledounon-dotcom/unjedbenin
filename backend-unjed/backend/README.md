# Backend UNJED-BENIN — déploiement sur PythonAnywhere (plan GRATUIT)

## 1. Créer le compte
Va sur https://www.pythonanywhere.com → **"Pricing & signup"** → choisis **"Create a Beginner account"**
(gratuit, aucune carte bancaire demandée). Choisis un nom d'utilisateur — ce sera
aussi ton adresse : `https://TON-NOM.pythonanywhere.com`.

⚠️ **A retenir** : sur le plan gratuit, le site s'éteint automatiquement si personne
ne se connecte à PythonAnywhere pendant **1 mois**. Mets-toi un rappel mensuel pour
te reconnecter (ça suffit à le garder actif, pas besoin de faire quoi que ce soit
de plus). Les emails automatiques et le futur paiement en ligne ne fonctionneront
probablement pas sur ce plan (connexions sortantes limitées) — seule la publication
de contenu (photos, annonces, documents) est concernée par ce guide, et ça marche
très bien en gratuit.

## 2. Envoyer les fichiers
Dans l'onglet **Files** de PythonAnywhere, crée un dossier `unjed-backend` et uploade
tous les fichiers de ce dossier (`app.py`, `models.py`, `emailer.py`, `seed_admins.py`,
`requirements.txt`).

Ou, plus simple, via un terminal Bash PythonAnywhere (onglet **Consoles** > **Bash**) :
```bash
git clone <url-de-ton-repo-backend> unjed-backend
cd unjed-backend
```

## 3. Installer les dépendances
Dans une console Bash PythonAnywhere :
```bash
cd unjed-backend
pip install --user -r requirements.txt
```

## 4. Créer les comptes admin
Toujours dans la console Bash :
```bash
python3 seed_admins.py
```
Suis les instructions (nom d'utilisateur + mot de passe pour chacun des 2-3 admins).
Les mots de passe ne sont jamais écrits dans un fichier, juste hashés en base.

## 5. Configurer l'application Web
Onglet **Web** > **Add a new web app** > choisis **Flask** > la version Python
disponible sur le plan gratuit (3.11/3.12/3.13 selon ton compte).
Dans la section **Code**, indique le chemin vers `app.py`.
PythonAnywhere génère un fichier WSGI — édite-le pour qu'il importe ton app :
```python
import sys
path = '/home/TON-USERNAME/unjed-backend'
if path not in sys.path:
    sys.path.append(path)
from app import app as application
```

## 6. Variables d'environnement (secrets)
Onglet **Web** > section **Environment variables**, ajoute au minimum :

| Nom | Valeur |
|---|---|
| `SECRET_KEY` | une longue chaîne aléatoire (génère-la avec `python3 -c "import secrets; print(secrets.token_hex(32))"` dans une console Bash) |

Les variables liées à l'email (`MAIL_SERVER`, `MAIL_USERNAME`, etc.) peuvent être
ajoutées plus tard, quand tu passeras sur un plan payant — inutile de les configurer
maintenant puisqu'elles ne fonctionneront pas avec les connexions sortantes limitées
du plan gratuit. Tant qu'elles ne sont pas configurées, le site continue de marcher
normalement (les emails sont juste silencieusement non envoyés, sans erreur).

## 7. Recharger l'app
Bouton vert **Reload** en haut de l'onglet **Web**.

## 8. Mettre à jour le site (GitHub Pages)
Dans `administration.html`, `multimedia.html` et `components.js`, remplace :
```js
var API_BASE = "https://VOTRE-USERNAME.pythonanywhere.com";
```
par ta vraie adresse PythonAnywhere (ex: `https://theophile.pythonanywhere.com`).

## 9. Tester
- Va sur `https://TON-USERNAME.pythonanywhere.com/api/health` → doit répondre `{"status":"ok"}`
- Va sur `administration.html` de ton site, connecte-toi avec un des comptes créés à l'étape 4.

## Rappel mensuel
Mets un rappel (téléphone, calendrier) pour te connecter sur pythonanywhere.com
une fois par mois — sinon le site gratuit se désactive automatiquement après
1 mois d'inactivité de ton compte.

## Plus tard : email + paiement (FedaPay/Kkiapay)
Quand tu auras un petit budget, passe sur un plan payant PythonAnywhere (débloque
les connexions sortantes illimitées), puis :
1. Ajoute les variables d'environnement email (`MAIL_SERVER`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `MAIL_FROM`)
2. Complète l'emplacement commenté `PAIEMENT ADHESION` dans `app.py` avec les clés FedaPay/Kkiapay
