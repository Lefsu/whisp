# Whisp

Whisp est un projet entièrement open-source, une application web zéro-trust pour garantir une confidentialité maximale.

Whisp repose sur la philosophie du **Zero Trust**, ce qui signifie que le serveur ne voit que des données chiffrées. De plus, une politique **No-Log** est appliquée : aucune adresse IP, aucune localisation, aucune donnée personnelle n'est enregistrée sur le serveur. La seule information stockée est la **liste de contacts**, qui est elle-même chiffrée.

### 1. **Création d'un Utilisateur**

**Étape 1.1 : Inscription de l'utilisateur**  
Lors de l'inscription, l'utilisateur choisit un mot de passe, qui sera utilisé pour générer la clé privée et publique de l'utilisateur.

- **Génération de la clé privée et publique (par exemple avec Ed25519 ou X25519)** :
  - La paire de clés est générée côté client (dans le navigateur de l'utilisateur).  
  - La clé privée est immédiatement chiffrée à l'aide d'une fonction de dérivation de clé (KDF), comme **PBKDF2** ou **Argon2**, en utilisant le mot de passe de l'utilisateur.  
  - La clé publique est envoyée au serveur.
  
- **Chiffrement de la clé privée** :  
  - La clé privée est chiffrée à l'aide de la clé dérivée du mot de passe.
  - La clé publique et la clé privée chiffrée sont envoyées au serveur pour être stockées (le serveur ne stocke jamais la clé privée en clair).

- **Stockage sur le serveur** :  
  - Le serveur stocke uniquement la clé publique, la clé privée chiffrée et un sel pour la dérivation de clé.

### 2. **Connexion de l'Utilisateur**

**Étape 2.1 : Authentification de l'utilisateur**  
Lors de la connexion, l'utilisateur entre son identifiant et son mot de passe.

- **Récupération de la clé privée chiffrée** :  
  - Le serveur récupère la clé privée chiffrée associée à l'identifiant de l'utilisateur et la renvoie au client.

- **Dérivation de la clé de déchiffrement** :  
  - Côté client, le mot de passe de l'utilisateur est utilisé pour dériver une clé de déchiffrement à l'aide d'un KDF (par exemple, **PBKDF2** ou **Argon2**).
  
- **Déchiffrement de la clé privée en mémoire** :  
  - La clé privée chiffrée est déchiffrée en mémoire, uniquement dans le navigateur de l'utilisateur. Elle n'est jamais stockée localement sur l'appareil.

- **Vérification de la clé privée** :  
  - L'utilisateur peut maintenant utiliser sa clé privée pour interagir avec d'autres utilisateurs, comme signer des messages ou générer des clés de session.

### 3. **Authentification à Deux Facteurs (2FA)**

**Étape 3.1 : Mise en place de 2FA**  
L'authentification à deux facteurs est utilisée pour renforcer la sécurité du compte.

- **Génération d'un code de vérification** :  
  - Lors de la connexion, après l'authentification par mot de passe, un code à usage unique est envoyé à l'utilisateur via un moyen sécurisé (via une application d'authentification).

- **Vérification du code 2FA** :  
  - L'utilisateur entre le code reçu dans l'interface de l'application.  
  - Le serveur valide le code et autorise l'accès à l'utilisateur.

### 4. **Ajout d'un Ami**

**Étape 4.1 : Recherche de l'ami**  
L'utilisateur peut rechercher d'autres utilisateurs à ajouter en tant qu'amis en utilisant leurs identifiants.

- **Demande d'ami** :
  - L'utilisateur envoie une demande d'ajout à l'ami, l'ami accepte.

- **Récupération de la clé publique de l'ami** :  
  - Si l'ami accepte la demande, le serveur renvoie la clé publique de l'ami à l'utilisateur, et l'ami est ajouté à la liste des contacts de l'utilisateur.

### 5. **Création d'un Canal Sécurisé et Chiffré**

**Étape 5.1 : Création d'un canal de communication**  
Une fois qu'Alice a ajouté Bob en tant qu'ami, un canal sécurisé est créé pour leur communication.

- **Génération d'une clé de session éphémère** :  
  - Alice et Bob génèrent une clé de session commune à l'aide d'un échange Diffie-Hellman avec leurs clés privées et publiques respectives.  
  - Cela génère un secret de session partagé que seuls Alice et Bob connaissent. Ce secret est utilisé pour dériver une clé symétrique pour le chiffrement des messages.

- **Utilisation du Double Ratchet** :  
  - Alice et Bob utilisent le protocole **Double Ratchet** pour chaque message envoyé. Cela garantit que chaque message est chiffré avec une clé unique et que les anciennes clés sont ratchetées après chaque message, ce qui permet de maintenir la sécurité même si une clé de session est compromise.
  
**Étape 5.2 : Envoi d'un message sécurisé**

- **Chiffrement du message** :  
  - Le message est chiffré côté client (dans le navigateur) avec la clé symétrique générée à partir de la clé de session partagée, en utilisant un algorithme comme **AES-GCM** (mode de chiffrement avec authentification).

- **Envoi du message** :  
  - Le message chiffré est envoyé au serveur via un canal sécurisé (par exemple, WebSocket ou HTTPS).

**Étape 5.3 : Réception du message**

- **Récupération du message chiffré** :  
  - Le message chiffré est récupéré par Bob depuis le serveur.
  
- **Déchiffrement du message** :  
  - Bob utilise sa clé privée et la clé publique d'Alice pour générer la même clé de session et déchiffrer le message.

- **Affichage du message** :  
  - Le message déchiffré est affiché à Bob dans l'interface.

### 6. **Sécurisation Supplémentaire**

**Étape 6.1 : Protection contre les attaques MITM**  
- Les utilisateurs vérifient les empreintes de leurs clés publiques avant d'établir un canal sécurisé.
  
**Étape 6.2 : Déconnexion et destruction de la clé privée**  
- Dès que l'utilisateur se déconnecte ou ferme le navigateur, la clé privée est **effacée de la mémoire** et aucune donnée sensible n'est stockée localement.

---

### **Stack technique**
#### **1. Backend (Python)**
- **FastAPI** → Pour un backend rapide, asynchrone et sécurisé.  
- **uvicorn** → Serveur ASGI performant.  
- **websockets** → Pour la messagerie en temps réel.  
- **cryptography / PyNaCl** → Pour la gestion des clés et le chiffrement (Ed25519, X25519, AES-GCM).  
- **SQLite (avec SQLCipher)** → Pour stocker uniquement les clés chiffrées et appliquer un chiffrement natif de la base.  

#### **2️. Sécurité**
- **mTLS (mutual TLS)** → Utilisation de certificats X.509 pour authentifier le serveur et les clients.  
- **OAuth2 / TOTP (PyOTP)** → Pour l'authentification à deux facteurs (Google Authenticator ou OTP).  
- **Argon2 / PBKDF2** → Pour le dérivation des clés à partir des mots de passe.  
- **Double Ratchet (avec libsignal)** → Pour la messagerie sécurisée.  

#### **3️. Communication**
- **WebSockets sur TLS 1.3** → Chiffrement des messages en transit.  
- **HTTPS (TLS 1.3 obligatoire)** → Sécurisation des API.  

#### **4️. Base de données**
- **SQLite avec SQLCipher** → Stockage minimaliste et chiffré des clés publiques et des métadonnées.  

---

### **Architecture**
1. **Inscription** → Génération de la clé privée/public côté client (Ed25519/X25519).  
2. **Connexion** → Récupération de la clé privée chiffrée + dérivation avec Argon2.  
3. **2FA** → Code OTP validé via TOTP.  
4. **WebSocket sécurisé** → Messages chiffrés avec Double Ratchet.  
5. **mTLS** → Authentification forte des clients et du serveur.  
