# Whisp – Application de Messagerie Zéro-Trust

**Whisp** est une application de messagerie web chiffrée de bout en bout, conçue selon une architecture **Zero Trust** et une politique stricte de **non-conservation des données** (no-log). Le projet est entièrement open-source et met l’accent sur la **confidentialité**, la **sécurité**, et la **transparence**.

## Objectifs

- Fournir une plateforme de messagerie chiffrée de bout en bout, où **seuls les utilisateurs** peuvent accéder à leurs messages.
- Garantir qu'aucune information exploitable (métadonnées, messages, contacts, IP) ne soit accessible au serveur.
- Utiliser des protocoles éprouvés et des primitives cryptographiques robustes, exécutés **côté client uniquement**.

---

## Sommaire

1. [Architecture de sécurité](#architecture-de-sécurité)
2. [Cycle de vie d’un utilisateur](#cycle-de-vie-dun-utilisateur)
3. [Protocole d’échange](#protocole-déchange)
4. [Stockage des données](#stockage-des-données)
5. [Stack technique](#stack-technique)
6. [Licence](#licence)

---

## Architecture de sécurité

### Principes

- **Zéro confiance (Zero Trust)** : le serveur n’est jamais en possession d’aucune donnée déchiffrable.
- **No-Log** : aucune trace exploitable n’est conservée (adresse IP, localisation, agents utilisateurs, etc.).
- **Chiffrement bout en bout** : tous les messages, contacts et métadonnées utiles sont chiffrés côté client.
- **Éphémérité des clés de session** : chaque canal utilise une clé temporaire dérivée via un échange sécurisé.

### Primitives utilisées

- **AES-256-GCM** : chiffrement symétrique authentifié.
- **SHA-256** : hachage des mots de passe.

---

## Cycle de vie d’un utilisateur

### Inscription

1. L'utilisateur choisit un identifiant et un mot de passe.
2. Une **paire de clés cryptographiques (privée/publique)** est générée **localement**.
3. Le mot de passe est haché avec **SHA-256**, et le hash est transmis au serveur.

### Connexion

1. L'utilisateur saisit son identifiant et mot de passe.
2. Le mot de passe est à nouveau haché côté client.
3. Le hash est comparé à celui présent en base.
4. Une fois authentifié, le client peut établir des canaux chiffrés avec ses contacts.
5. La **clé publique** est envoyée au serveur.
6. La **clé privée** n’est jamais transmise.


---

## Protocole d’échange

### Établissement d’un canal

1. L’utilisateur A envoie une demande de contact à l’utilisateur B (via son identifiant).
2. Une fois la demande acceptée, un échange **Diffie-Hellman ** est effectué.
3. Les clés publiques sont échangées via le serveur, **sans que le serveur ait accès aux clés privées**.
4. Un **secret partagé** est dérivé.
5. Ce secret sert à générer une clé AES-256-GCM pour chiffrer les messages.

### Communication

- Tous les messages sont :
  - Chiffrés via AES-256-GCM
  - Éphémères (aucune conservation)

---

## Stockage des données

| Élément            | Stocké ? | Chiffré ? | Côté serveur ? |
|--------------------|----------|-----------|----------------|
| Messages           | Non      | Oui       | Non            |
| Liste de contacts  | Oui      | Non       | Oui            |
| Clé publique       | Oui      | Non       | Oui            |
| Clé privée         | Non      | Non       | Non            |
| Adresse IP         | Non      | Non       | Non            |
| Mots de passe      | Oui      | Haché     | Oui            |

---

## Stack technique

### Backend (Python)

- **FastAPI** : framework web asynchrone, performant et moderne.
- **uvicorn** : serveur ASGI rapide pour applications temps réel.
- **websockets** : communication en temps réel via sockets Web.
- **cryptography** : bibliothèque de primitives cryptographiques.
- **SQLite** : base de données embarquée pour la gestion minimale d’état.

### Frontend (JavaScript)

- Chiffrement, génération de clés et échanges effectués **exclusivement côté client**.
- Utilisation des **API Web Crypto** pour garantir une sécurité native dans le navigateur.
- Interface web légère et minimaliste.

---

## Licence

Whisp est distribué sous la licence **MIT**.

Cela signifie que vous êtes libre de l’utiliser, de l’étudier, de le modifier et de le redistribuer, à condition de conserver les mentions de droit d’auteur.

---
