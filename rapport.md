# RAPPORT - Application GMAO

## Sommaire

- [PARTIE 1 : Présentation générale de l'application](#partie-1--présentation-générale-de-lapplication)
- [PARTIE 2 : Architecture logicielle et base de données](#partie-2--architecture-logicielle-et-base-de-données)
- [PARTIE 3 : API REST - Endpoints, sécurité et client](#partie-3--api-rest---endpoints-sécurité-et-client)
- [PARTIE 4 : Fonctionnalités métiers, écrans et rôles](#partie-4--fonctionnalités-métiers-écrans-et-rôles)
- [PARTIE 5 : Configuration, utilisation et état du projet](#partie-5--configuration-utilisation-et-état-du-projet)

---

# PARTIE 1 : Présentation générale de l'application

## 1.1 Objectif de l'application

L'application GMAO (Gestion et Maintenance Assistée par Ordinateur) est un logiciel de gestion de maintenance (CMMS) développé dans le cadre d'un projet de groupe (« Groupe 02 »). Elle permet la gestion centralisée du parc de matériel, des demandes d'intervention, des bons de travail, des techniciens et de la maintenance préventive.

## 1.2 Contexte du projet

Le projet est hébergé sous Git sur le dépôt https://github.com/FoxIngenious/GMAO_App.git, sur la branche master. Il s'agit d'une application à vocation pédagogique/démonstrative, développée en Python.

## 1.3 Stack technique

Le projet repose sur les technologies suivantes :

| Couche | Technologie |
|---|---|
| Interface graphique (GUI) | customtkinter (https://customtkinter.tomschimansky.com/) |
| Serveur API | FastAPI (https://fastapi.tiangolo.com/) + Uvicorn (https://www.uvicorn.org/) |
| Client HTTP | requests (https://requests.readthedocs.io/) |
| Validation des données | Pydantic (https://docs.pydantic.dev/) |
| Base de données | SQLite (https://www.sqlite.org/) |
| Authentification | PBKDF2-HMAC-SHA256 + tokens opaques |

## 1.4 Architecture générale

L'application adopte une architecture client-serveur à 3 niveaux, intégrée dans un unique dépôt :

```
Interface Tkinter (customtkinter)
        ↓  HTTP/JSON
Client HTTP (requests.Session) – api_client.py
        ↓  Requêtes avec headers X-API-Key + X-Auth-Token
Serveur REST (FastAPI + Uvicorn) – api.py
        ↓  Couche métier
Couche d'accès aux données (models.py)
        ↓  Connexions
Base de données SQLite (database.db)
```

Cette architecture sépare clairement la présentation (IHM), la logique applicative (API) et la persistance des données (BDD). Le serveur FastAPI est lancé automatiquement en sous-processus par l'interface graphique au démarrage de l'application.

## 1.5 Arborescence et volumétrie du projet

Le répertoire racine `/home/foxingenious/Documents/GMAO` contient l'ensemble des sources Python, les ressources et la base de données locale.

### 1.5.1 Fichiers sources Python

Le projet compte 19 fichiers Python pour un total de 2 567 lignes de code.

| Fichier | Lignes | Rôle |
|---|---|---|
| models.py | 558 | Couche d'accès aux données (modèles métier, CRUD, logique applicative) |
| api.py | 337 | Définition de l'API REST FastAPI (endpoints, dépendances) |
| bons_travail.py | 246 | Écran de gestion des bons de travail (IHM) |
| demandes_intervention.py | 223 | Écran de gestion des demandes d'intervention (IHM) |
| api_client.py | 192 | Client HTTP centralisé (wrappers des endpoints API) |
| preventif.py | 152 | Écran de gestion de la maintenance préventive (IHM) |
| main.py | 151 | Point d'entrée de l'application, bootstrap, routage des pages |
| techniciens.py | 118 | Écran de gestion des techniciens (IHM) |
| seed.py | 93 | Script de génération de données de démonstration |
| materiels.py | 74 | Écran de gestion des matériels (IHM) |
| schemas.py | 70 | Schémas Pydantic (modèles de requête/réponse API) |
| ajouter.py | 69 | Formulaire d'ajout/modification d'un matériel (IHM) |
| sideBar.py | 63 | Barre latérale de navigation, filtrée par rôle |
| accueil.py | 51 | Écran d'accueil post-connexion (IHM) |
| login.py | 48 | Écran de connexion (dialog) |
| security.py | 45 | Authentification, hachage des mots de passe, gestion des tokens |
| landing.py | 27 | Page d'accueil publique avant connexion (IHM) |
| database.py | 26 | Initialisation et connexion à la base SQLite |
| impression.py | 21 | Fonctionnalité d'impression/aperçu d'imprimables |
| **Total** | **2 567** | |

### 1.5.2 Autres fichiers et répertoires

| Élément | Description |
|---|---|
| .gitignore | Exclut `__pycache__/`, `*.py[cod]`, `database.db`, `.venv/` |
| .idea/ | Projet PyCharm (configuration IDE) |
| assets/ | Ressources — contient un fichier `assets/models.py` obsolète (3 lignes) |
| database.db | Base de données SQLite locale (non versionnée selon .gitignore) |
| requirements.txt | Dépendances Python du projet |
| venv/ | Environnement virtuel Python |
| `__pycache__/` | Fichiers compilés Python (.pyc) |

---

# PARTIE 2 : Architecture logicielle et base de données

## 2.1 Processus de démarrage (bootstrap)

L'application est lancée via `main.py`. Le flux de démarrage est le suivant :

1. **Initialisation de l'IHM** (`main.py:21–24`) : Configuration de customtkinter (mode dark, thème green), création de la fenêtre principale `CTk()` intitulée « Gestion Matériel | Groupe 02 ».
2. **Mise en page de la fenêtre** (`main.py:136–147`) : Fenêtre maximisée (`state("zoomed")` avec fallback sur géométrie écran). Création des conteneurs menu (barre latérale) et page_conteneur (zone d'affichage des écrans).
3. **Démarrage du serveur API** (`main.py:43–50`, `_lancer_api()` lignes 32–41) :
   - Vérification de la disponibilité de l'API via `api_client.est_joignable()` (appel `GET /health`).
   - Si l'API n'est pas joignable, un thread daemon lance uvicorn via `subprocess.Popen` : `sys.executable -m uvicorn api:app --host 127.0.0.1 --port 8000` (sorties stdout/stderr ignorées).
   - Attente active jusqu'à ce que l'API réponde (polling sur `/health`, environ 15 secondes maximum).
4. **Affichage de l'interface** (`main.py:150–152`) : Affichage de la page publique AccueilPublic (landing), puis lancement de `app.mainloop()`.
5. **Initialisation de la base de données** (`api.py:25–28`) : À son démarrage, l'API FastAPI exécute `models.initialiser_base()` via le hook lifespan, ce qui permet de créer ou de réajuster les tables SQLite selon leur définition dans `models.py`.

## 2.2 Base de données SQLite

### 2.2.1 Tables définies

La couche `models.py` (lignes 17–102) définit 6 tables avec leurs colonnes respectives. Ces définitions constituent la source de vérité pour l'initialisation de la base.

| Table | Clé primaire | Colonnes |
|---|---|---|
| materiels | `id` (INTEGER, AUTOINCREMENT) | id, code (UNIQUE, NOT NULL), nom, categorie, emplacement, service (défaut ''), etat |
| demandes_intervention | `id` (INTEGER, AUTOINCREMENT) | id, numero, equipement (défaut ''), description, demandeur, date_creation, priorite (défaut 'Normale'), statut (défaut 'Nouvelle') |
| techniciens | `id` (INTEGER, AUTOINCREMENT) | id, nom, specialite (défaut ''), telephone (défaut '') |
| bons_travail | `id` (INTEGER, AUTOINCREMENT) | id, numero, di (défaut ''), equipement (défaut ''), technicien (défaut ''), statut (défaut 'À faire'), travaux (défaut ''), date_debut (défaut ''), date_fin (défaut ''), duree (défaut ''), cause (défaut ''), taches_realisees (défaut '') |
| utilisateurs | `id` (INTEGER, AUTOINCREMENT) | id, nom, email (UNIQUE), mot_de_passe, role |
| maintenance_preventive | `id` (INTEGER, AUTOINCREMENT) | id, titre, equipement, periodicite, prochaine_echeance, statut (défaut 'Planifiée') |

### 2.2.2 Énumérations métier

Les constantes définies dans `models.py` (lignes 9–15) structurent les valeurs autorisées dans l'application :

| Énumération | Valeurs possibles |
|---|---|
| ETATS_MATERIEL | Disponible, En marche, En panne, En maintenance, Réservé |
| PRIORITES | Basse, Normale, Haute, Urgente, Critique |
| STATUTS_DI | Nouvelle, En attente, Prise en charge, Clôturée, Annulée |
| STATUTS_BT | À faire, En cours, Terminé, Clôturé, Annulé |
| STATUTS_PREVENTIF | Planifiée, À faire, BT généré |
| PERIODICITES | Hebdomadaire, Mensuelle, Trimestrielle, Annuelle |
| ROLES | Responsable Maintenance, Technicien, Opérateur |

### 2.2.3 Gestion de la base de données

- **Initialisation dynamique** (`models.initialiser_base()`, lignes 114–121) : Vérifie la structure de chaque table existante. Si les colonnes diffèrent de la définition attendue, la table est supprimée (`DROP TABLE`) puis recréée avec la structure à jour.
- **Génération automatique des numéros** (`models._prochain_numero()`, lignes 109–111) : Incrémente un compteur (`COUNT(*) + 1`) et formate les numéros sous la forme `DI-###` (demandes d'intervention) et `BT-###` (bons de travail).
- **Remise à zéro des IDs** (`models.supprimer_materiel()`, lignes 178–183) : Après suppression d'un matériel, l'application renumérote les IDs suivants (`UPDATE ... SET id = id-1`) et réinitialise `sqlite_sequence`. Il s'agit d'une approche manuelle de gestion des clés primaires.

> **Remarque** : Le fichier `database.db` présent sur disque peut présenter un écart par rapport aux définitions actuelles de `models.py` (notamment sur certaines colonnes). Au démarrage de l'API, `initialiser_base()` réaligne automatiquement la structure des tables concernées.

## 2.3 Couches logicielles

| Couche | Fichier | Rôle |
|---|---|---|
| Accès données / Métier | models.py | Contient toutes les fonctions CRUD, la logique métier (génération BT, clôture, vérification échéances préventives), les règles de numérotation et les validations métier. |
| Connexion BDD | database.py | Fournit les helpers de connexion à SQLite (`get_connexion()`), utilisés par models.py. |
| Schémas API | schemas.py | Définit les modèles Pydantic pour les entrées/sorties des endpoints (`LoginEntree`, `MaterielEntree`, `DemandeEntree`, `TechnicienEntree`, `BonEntree`, `RapportEntree`, `GenererBtEntree`, `UtilisateurEntree`, `PreventiveEntree`). |
| Serveur API | api.py | Implémente l'application FastAPI, les routes, les dépendances d'authentification (`Depends_cle`, `exiger_utilisateur`) et mappe les requêtes HTTP vers les fonctions de models.py. |
| Client API | api_client.py | Encapsule tous les appels HTTP vers l'API (Session requests, en-têtes communs, gestion des erreurs, timeouts). Fournit des wrappers typés pour chaque endpoint. |
| IHM | Fichiers *.py (hors couches ci-dessus) | Écrans et formulaires customtkinter consommant uniquement api_client.py (aucun accès direct à la BDD). |

---

# PARTIE 3 : API REST - Endpoints, sécurité et client

## 3.1 Présentation générale de l'API

L'API est exposée par `api.py` sous l'application FastAPI (`app = FastAPI(title="API GMAO", version="2.0")`, ligne 31). Elle est accessible localement à l'adresse `http://127.0.0.1:8000`.

Au total, **32 endpoints REST** sont définis dans `api.py` (détectés via les décorateurs `@app.*`).

## 3.2 Endpoints REST détaillés

| Méthode | Chemin | Ligne (api.py) |
|---|---|---|
| GET | /health | 77 |
| POST | /auth/login | 83 |
| GET | /auth/me | 92 |
| GET | /materiels | 98 |
| POST | /materiels | 103 |
| GET | /materiels/{id} | 114 |
| PUT | /materiels/{id} | 122 |
| DELETE | /materiels/{id} | 134 |
| POST | /materiels/{id}/etat | 140 |
| GET | /demandes-intervention | 150 |
| POST | /demandes-intervention | 155 |
| GET | /demandes-intervention/{id} | 166 |
| PUT | /demandes-intervention/{id} | 174 |
| DELETE | /demandes-intervention/{id} | 186 |
| POST | /demandes-intervention/{id}/generer-bt | 192 |
| GET | /techniciens | 202 |
| POST | /techniciens | 207 |
| GET | /techniciens/{id} | 216 |
| PUT | /techniciens/{id} | 224 |
| DELETE | /techniciens/{id} | 233 |
| GET | /bons-travail | 240 |
| POST | /bons-travail | 245 |
| GET | /bons-travail/{id} | 257 |
| PUT | /bons-travail/{id} | 265 |
| DELETE | /bons-travail/{id} | 277 |
| POST | /bons-travail/{id}/rapport | 283 |
| GET | /maintenance-preventive | 295 |
| POST | /maintenance-preventive | 300 |
| GET | /maintenance-preventive/{id} | 311 |
| PUT | /maintenance-preventive/{id} | 319 |
| DELETE | /maintenance-preventive/{id} | 330 |
| POST | /maintenance-preventive/verifier-echeances | 336 |

## 3.3 Sécurité et authentification

L'API met en place deux mécanismes de protection, implémentés dans `security.py` et utilisés dans `api.py`.

### 3.3.1 Dépendances d'authentification (api.py)

| Dépendance | Lignes | Utilisation |
|---|---|---|
| Depends_cle | 35–43 | Vérifie la présence et la validité de l'en-tête `X-API-Key`. Requis pour tous les endpoints, à l'exception de `/health` et `/auth/login`. |
| exiger_utilisateur | 46–55 | Vérifie l'en-tête `X-Auth-Token` (token de session) et résout l'utilisateur associé. Requis principalement pour l'endpoint `GET /auth/me`. |

### 3.3.2 Gestion des mots de passe (security.py)

- **Algorithme** : PBKDF2-HMAC-SHA256 (100 000 itérations)
- **Sel** : Généré aléatoirement (16 octets) pour chaque mot de passe
- **Stockage** : Format `salt:hash` (hexadécimal)
- **Vérification** : Comparaison sécurisée via `hmac.compare_digest`
- **Fonctions** : `hachage_mot_de_passe()` (lignes 12–21), `verifier_mot_de_passe()` (lignes 24–28)

### 3.3.3 Gestion des tokens de session (security.py)

- **Génération** : `secrets.token_hex(24)` (token opaque de 48 caractères hexadécimaux)
- **Stockage** : En mémoire uniquement (dict `_tokens`), indexé par le token
- **Durée de vie** : Tant que le processus serveur (Uvicorn) est actif (aucune persistance). Les tokens sont perdus au redémarrage du serveur.
- **Fonctions** : `creer_token()` (lignes 31–36), `valider_token()` (lignes 38–40)

### 3.3.4 Clé API

La clé API est lue depuis la variable d'environnement `GMAO_API_KEY` (avec valeur par défaut de secours). Elle est transmise via l'en-tête `X-API-Key` dans les appels clients.

## 3.4 Client API (api_client.py)

Le fichier `api_client.py` (192 lignes) constitue le client HTTP centralisé utilisé exclusivement par l'ensemble des écrans de l'IHM.

| Élément | Détails |
|---|---|
| Session HTTP | `requests.Session()` (ligne 8) — réutilise les connexions TCP |
| Configuration | `GMAO_API_URL` (défaut `http://127.0.0.1:8000`) et `GMAO_API_KEY` lus via variables d'environnement (lignes 5–6) |
| En-têtes communs | `X-API-Key` et `X-Auth-Token` injectés dans la session (lignes 8–9) |
| Wrapper générique | `_requete()` (lignes 19–31) — gère les verbes HTTP, les timeouts, le traitement des erreurs et la normalisation des réponses |
| Healthcheck | `est_joignable()` (lignes 12–16) — appel `GET /health` pour vérifier la disponibilité de l'API |
| Wrappers d'endpoints | Environ 35 fonctions typées couvrant l'intégralité des 32 endpoints (CRUD + actions spécifiques) : `login()`, `me()`, `lister_materiels()`, `ajouter_materiel()`, `obtenir_materiel()`, `modifier_materiel()`, `supprimer_materiel()`, `changer_etat_materiel()`, `lister_demandes()`, `ajouter_demande()`, `modifier_demande()`, `supprimer_demande()`, `generer_bt_depuis_di()`, `lister_techniciens()`, `ajouter_technicien()`, `modifier_technicien()`, `supprimer_technicien()`, `lister_bons_travail()`, `ajouter_bon_travail()`, `obtenir_bon_travail()`, `modifier_bon_travail()`, `supprimer_bon_travail()`, `cloturer_bon_travail()`, `lister_preventif()`, `ajouter_preventif()`, `obtenir_preventif()`, `modifier_preventif()`, `supprimer_preventif()`, `verifier_echeances()`, `logout()` (lignes 35–193) |

## 3.5 APIs externes

Aucune API externe (tierce partie) n'est consommée dans ce projet. L'intégralité du trafic HTTP est exclusivement à destination de `http://127.0.0.1:8000` (loopback). Aucun appel vers des services cloud, webhooks, passerelles de paiement, services d'authentification externes ou intégrations IA n'est présent dans le code source.

---

# PARTIE 4 : Fonctionnalités métiers, écrans et rôles

## 4.1 Fonctionnalités métiers (workflows)

L'application implémente les processus métier classiques d'une solution GMAO/CMMS.

### 4.1.1 Workflow 1 : Demandes d'intervention (DI) → Bons de travail (BT)

1. **Création d'une DI** (`models.ajouter_demande()`, lignes ~210–237) : Génération automatique du numéro `DI-###`, initialisation avec `date_creation` = date du jour, priorité par défaut `Normale`, statut par défaut `Nouvelle`.
2. **Génération d'un BT depuis une DI** (`models.generer_bon_travail(di_id, technicien)`, lignes 265–286) :
   - Création d'un bon de travail (`BT-###`) à partir des informations de la demande d'intervention (numéro DI, équipement, description/travaux)
   - Le champ `di` du BT est renseigné avec le numéro de la demande
   - Le statut de la demande d'intervention passe de `Nouvelle` à `Prise en charge`
3. **API correspondante** : `POST /demandes-intervention/{id}/generer-bt`
4. **IHM** : Bouton « Générer BT » dans l'écran des demandes d'intervention (avec sélection du technicien)

### 4.1.2 Workflow 2 : Cycle de vie et clôture des bons de travail

1. **États des BT** : `À faire` → `En cours` → `Terminé` → `Clôturé` (ou `Annulé`)
2. **Clôture avec rapport** (`models.cloturer_bon_travail(id, duree, cause, taches_realisees)`, lignes 390–409) :
   - Exige que les trois champs (`duree`, `cause`, `taches_realisees`) soient renseignés
   - Met à jour le BT avec ces informations
   - Définit `statut = 'Clôturé'` et `date_fin` = date du jour
   - Appelle automatiquement `remettre_materiel_en_marche(equipement)` (lignes 193–198) pour remettre l'équipement concerné à l'état `En marche`
3. **Mise à jour de statut** (`models.modifier_bon_travail()`, lignes 366–388) : Lorsque le statut passe à `Terminé` ou `Clôturé`, l'équipement est également remis automatiquement en état `En marche`.
4. **API correspondante** : `POST /bons-travail/{id}/rapport`
5. **IHM** : Boîte de dialogue `DialogRapport` (`bons_travail.py`) permettant de saisir durée, cause et tâches réalisées pour clôturer un BT.

### 4.1.3 Workflow 3 : Maintenance préventive et vérification des échéances

1. **Planification** (`models.ajouter_maintenance_preventive()`) : Création d'un plan avec titre, équipement, périodicité (Hebdomadaire, Mensuelle, Trimestrielle, Annuelle), prochaine échéance et statut initial `Planifiée`.
2. **Vérification des échéances** (`models.verifier_echeances()`, lignes 534–558) :
   - Sélectionne les plans dont `statut != 'BT généré'` et `prochaine_echeance <= date du jour`
   - Pour chaque échéance atteinte : création automatique d'un BT (champ `di = 'Préventif'`, `travaux` = titre du plan, technicien laissé vide)
   - Avance la prochaine échéance selon la périodicité (`_avancer_echeance()`, lignes 523–531)
   - Passe le statut du plan à `BT généré`
   - Retourne le nombre de BT générés
3. **Calcul des échéances** :
   - Hebdomadaire : +7 jours
   - Mensuelle/Trimestrielle : ajout de mois via `_ajouter_mois()` (lignes 515–520) avec gestion du dernier jour du mois (clamp)
   - Annuelle : +1 an
4. **API correspondante** : `POST /maintenance-preventive/verifier-echeances`
5. **IHM** : Bouton « Vérifier les échéances » dans l'écran de maintenance préventive (`preventif.py`)

### 4.1.4 Gestion des matériels

- CRUD complet avec validation unicité du code matériel
- Gestion des états (`ETATS_MATERIEL`) : Disponible, En marche, En panne, En maintenance, Réservé
- Changement d'état : API `POST /materiels/{id}/etat`
- Remise automatique en marche : Lors de la clôture/modification d'un BT vers un statut `Terminé`/`Clôturé`, l'équipement associé est automatiquement remis à l'état `En marche` (`remettre_materiel_en_marche()`)

## 4.2 Écrans et interfaces utilisateur

L'application comporte 13 modules d'interface graphique (basés sur customtkinter et `ttk.Treeview` pour les listes). Tous consomment exclusivement `api_client.py`.

| Module | Lignes | Écran / Fonctionnalité |
|---|---|---|
| main.py | 151 | Coquille applicative, gestion de la navigation (router de pages), lancement/gestion du serveur API, gestion de la session utilisateur courante. |
| landing.py | 27 | Page d'accueil publique (« AccueilPublic ») affichée avant la connexion. Propose un accès à l'écran de connexion. |
| login.py | 48 | Boîte de dialogue de connexion (EcranConnexion, CTkToplevel). Appelle `api_client.login()`, gère l'authentification et stocke le token. Propose des identifiants de démonstration pré-remplis. |
| accueil.py | 51 | Écran d'accueil post-connexion (Acceuill — légère coquille de nommage). Affiche des raccourcis vers les matériels et l'ajout d'un nouveau matériel. |
| sideBar.py | 63 | Barre latérale de navigation (SideBar). Génère dynamiquement le menu en fonction du rôle de l'utilisateur connecté. Affiche nom et rôle, comporte un bouton de déconnexion. |
| materiels.py | 74 | Gestion du parc de matériels (ListesMateriels). Liste sous forme de tableau (Treeview), actions : Ajouter, Modifier, Supprimer, Actualiser, Imprimer. |
| ajouter.py | 69 | Formulaire d'ajout/modification d'un matériel (AjouterMateriel, CTkToplevel). Champs : code, nom, catégorie, emplacement, service, état (combobox). |
| demandes_intervention.py | 223 | Gestion des demandes d'intervention (GestionDemandesIntervention). Liste, ajout/modification/suppression, génération de BT, impression. Contient également FormulaireDemande (formulaire DI) et un dialogue de génération de BT. |
| bons_travail.py | 246 | Gestion des bons de travail (GestionBonsTravail). Liste des BT, création/modification/suppression, clôture via rapport. Contient FormulaireBonTravail et DialogRapport (formulaire de clôture). |
| techniciens.py | 118 | Gestion des techniciens (GestionTechniciens). CRUD complet + impression. Contient FormulaireTechnicien. |
| preventif.py | 152 | Gestion de la maintenance préventive (GestionMaintenancePreventive). Liste des plans, ajout/modification/suppression, bouton « Vérifier les échéances » (déclenche `verifier_echeances()`), impression. Contient FormulairePreventif. |
| impression.py | 21 | Fonction utilitaire d'impression/aperçu (`imprimer_fiche()`). Ouvre une fenêtre CTkToplevel affichant le contenu textuel à imprimer (aperçu local, sans impression matérielle directe). |

## 4.3 Gestion des rôles et permissions

L'application définit 3 rôles utilisateurs (`models.ROLES`, ligne 15) :

| Rôle | Libellé |
|---|---|
| Responsable Maintenance | Rôle disposant d'un accès étendu à l'ensemble des fonctionnalités |
| Technicien | Rôle orienté exécution (bons de travail, interventions) |
| Opérateur | Rôle orienté saisie (demandes d'intervention) |

### 4.3.1 Filtrage du menu latéral (sideBar.py:32–52)

La visibilité des onglets dans la barre latérale est filtrée par rôle :

| Menu | Responsable Maintenance |
|---|---|
| Accueil | Oui |
| Matériels | Oui |
| Intervention (DI) | Oui |
| Bons de travail (BT) | Oui |
| Préventif | Oui |
| Techniciens | Oui |

### 4.3.2 Restrictions fonctionnelles et filtrage des données

| Écran | Règle de restriction/filtrage |
|---|---|
| demandes_intervention.py (lignes 23–24, 30, 52–53) | Pour les rôles Opérateur et Technicien (liste `roles_restreints`), le bouton « Générer BT » n'est pas affiché. De plus, pour ces rôles, la liste des demandes d'intervention est filtrée pour n'afficher que celles dont le demandeur correspond au nom de l'utilisateur connecté (`demandeur == utilisateur["nom"]`). |
| bons_travail.py (lignes 22, 49–50) | Pour le rôle Technicien, la liste des bons de travail est filtrée pour n'afficher que ceux dont le technicien affecté correspond au nom de l'utilisateur connecté (`technicien == utilisateur["nom"]`). |
| main.py:130 | Le rôle de l'utilisateur (`utilisateur["role"]`) est transmis à SideBar pour le rendu conditionnel du menu. |

### 4.3.3 Remarque sur l'application des rôles

Le filtrage des permissions est appliqué uniquement côté IHM (interface graphique). Côté serveur API, l'authentification vérifie la clé API et le token de session, mais les endpoints (hors `/auth/me`) ne mettent pas en œuvre de vérification des rôles utilisateurs. L'ensemble des écrans UI applique les règles ci-dessus pour restreindre l'affichage et l'accès aux actions.

---

# PARTIE 5 : Configuration, utilisation et état du projet

## 5.1 Configuration de l'application

### 5.1.1 Variables d'environnement

L'application peut être configurée via des variables d'environnement (avec valeurs par défaut de secours) :

| Variable | Emplacement |
|---|---|
| GMAO_API_URL | api_client.py:5, security.py:46 |
| GMAO_API_KEY | api.py:22, api_client.py:6, security.py:45 |

Aucun fichier `.env` n'est présent dans le projet.

### 5.1.2 Dépendances (requirements.txt)

Le fichier `requirements.txt` liste les dépendances nécessaires à l'exécution :

```
customtkinter
datetime
pathlib
fastapi
uvicorn
requests
pydantic
```

> **Remarque** : `datetime` et `pathlib` font partie de la bibliothèque standard Python. Leur présence dans `requirements.txt` n'est pas nécessaire à l'installation.

### 5.1.3 Données de démonstration (seed.py)

Le fichier `seed.py` (93 lignes) est un script autonome permettant de peupler la base de données avec des données de démonstration.

- **Exécution** : Manuelle uniquement (`if __name__ == "__main__": seed()` à la ligne 93–94). Il n'est pas appelé automatiquement au démarrage de l'application.
- **Contenu généré** : Utilisateurs de démo, matériels, techniciens, demandes d'intervention, bons de travail et plans de maintenance préventive.
- **Utilisation** : Permet de disposer d'identifiants de test pour se connecter à l'application.

## 5.2 État du projet (Git)

Le projet est suivi sous Git (distant `origin/master`).

### 5.2.1 Historique des commits

**18 commits** au total. Les 5 derniers commits sont :

| Commit | Date |
|---|---|
| c9bb6a8 | 2026-10-08 |
| e0b4ada | 2026-10-08 |
| fc0d30c | 2026-10-02 |
| b7f9413 | 2026-09-26 |
| fc94c8e | 2026-09-26 |

L'historique montre une évolution progressive (initialisations, uploads successifs) avec des ajouts récents liés aux dépendances.

### 5.2.2 État du working tree (git status)

À l'état actuel, la branche master est à jour par rapport à `origin/master`. On observe :

- **Fichiers modifiés (suivis)** : `ajouter.py`, `bons_travail.py`, `database.db`, `database.py`, `demandes_intervention.py`, `main.py`, `materiels.py`, `models.py`, `requirements.txt`, `sideBar.py`, `techniciens.py`, ainsi que des fichiers compilés `.pyc` dans `__pycache__/`.
- **Fichiers non suivis (nouveaux)** : `api.py`, `api_client.py`, `landing.py`, `login.py`, `preventif.py`, `schemas.py`, `security.py`, `seed.py`.

Ce constat indique que la couche API REST complète (FastAPI), le client HTTP, l'authentification, les schémas Pydantic et le script de seed constituent des ajouts non encore commités par rapport à l'historique existant, s'ajoutant à une base de code IHM/BDD plus ancienne.

## 5.3 Éléments de documentation et tests

| Élément | État |
|---|---|
| Tests automatisés | Aucun fichier de test présent (`tests/`, `test_*.py`, configuration pytest/unittest absente). |
| Documentation | Aucun fichier de documentation (`README.md`, `README`, `.md`, `.rst`, `docs/`) présent dans le répertoire racine. |
| Commentaires dans le code | Absence de commentaires explicatifs (conformément à la convention de style du projet). |

## 5.4 Caractéristiques générales du projet

| Caractéristique | Détail |
|---|---|
| Type d'application | Application desktop (client lourd) à architecture client-serveur locale |
| Mode de fonctionnement | Monoposte/local — serveur API auto-lancé sur `127.0.0.1:8000`, base SQLite locale |
| Langage | Python 100 % |
| Persistance | SQLite (`database.db`) — fichier local, exclu du suivi Git |
| Démarrage | Automatique (l'IHM lance Uvicorn en sous-processus) |
| Point d'entrée | `main.py` |
| Couplage IHM/API | Faible : tous les écrans accèdent aux données via `api_client.py` uniquement |

## 5.5 Synthèse de l'état du projet

Le projet GMAO se présente sous la forme d'une application CMMS fonctionnelle à deux niveaux (IHM + API REST), structurée de manière claire avec une séparation entre couches (présentation, logique, persistance). Il couvre l'ensemble des entités métier principales (matériels, demandes d'intervention, bons de travail, techniciens, maintenance préventive) et implémente des workflows métiers cohérents.

L'architecture est bien définie (FastAPI + customtkinter + requests + SQLite), les rôles sont gérés au niveau de l'interface graphique, et l'API REST expose un jeu complet d'endpoints (32 endpoints) couvrant les opérations CRUD et les actions métier spécifiques. Le projet est dans un état de développement actif, avec une couche API récemment ajoutée (non encore intégrée dans l'historique Git).
