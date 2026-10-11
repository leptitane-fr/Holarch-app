# Holarch-app

Les applications de **Holarch System**, un système d'exploitation écrit
de zéro en Rust (micronoyau, programmes isolés ; son dépôt,
Holarch-system, est privé). Dans Holarch, une application est un
**Holon-app** : une capsule autonome et signée, qui ne détient que les
capacités que son parent lui délègue, et rien de plus.

Ce dépôt suit le principe de **[Holarch-sys](https://github.com/leptitane-fr/Holarch-sys)**,
celui des pilotes (les Holon-sys) : on y trouve le nécessaire pour
écrire une application, le guide, les applications proposées (en
source), et les rapports d'essai signés par Holarch.

## État : en préparation

**Rien n'est encore prêt à écrire une application.** Le contrat d'un
Holon-app (son manifeste, ses capacités, sa capsule `.hln`, son cycle
de vie) se fixe d'abord dans Holarch-system (l'architecture des Holons,
étapes A à C). Ce dépôt se remplira ensuite.

## Ce qu'il contiendra

| Dossier | Contenu |
|---|---|
| `sdk/` | le nécessaire pour compiler une application, tel que Holarch le sert |
| `guide/` | le guide : la boîte à outils de l'interface, les fenêtres et les tâches, les outils déclarés, les droits à demander |
| `apps/` | les applications proposées, **source seulement**, chacune avec son manifeste et son origine |
| `essais/` | les rapports d'essai signés par Holarch (« fonctionnel » ne vaut que pour le matériel et la version essayés) |
| `cles/` | les clés publiques d'attestation reconnues |
| `outils/` | la construction reproductible (même source, même empreinte), la vérification des rapports, l'index |

## Les règles qui ne changeront pas

- **Personne n'entre dans Holarch** : c'est lui qui vient chercher une
  application, la vérifie, montre à l'écran les droits qu'il calcule
  pour elle, et ne la lance qu'après l'accord de son utilisateur,
  **devant l'écran**.
- **Une application ne reçoit jamais plus** que ce que tient son parent,
  et que ce que son manifeste demande.
- **Source seulement** : Holarch reconstruit l'application, octet pour
  octet ; jamais de binaire dans ce dépôt.

## La Bibliothèque de Holarch

Chaque holon qui a une **vitrine** paraît dans la Bibliothèque de Holarch
(le « Holons Store »), classé par catégorie. Dans son dossier :

| Fichier | Contenu |
|---|---|
| `vitrine.txt` | `nom`, `catégorie`, `résumé`, `version`, `icône`, `captures` (facultatif), `éditeur` (facultatif), `modes` (thèmes) ; un champ par ligne, `clé = valeur` |
| `description.txt` | la description longue, paragraphes séparés par une ligne vide |
| `icone.svg` | l'icône, carrée |
| `captures/` | les captures d'écran (WebP ou PNG) |

Les applications sont dans `apps/`, les thèmes (Holon-thème) dans `themes/`.
Une application ou un thème va sur toutes les plateformes de Holarch.

Catégories d'un Holon-app : Atelier (les modes de l'Atelier), Productivité,
Création, Multimédia, Communication, Internet, Outils, Éducation, Jeux.
Catégories d'un thème : Nature, Paysages, Villes, Espace, Abstraits ; ses `modes`
disent s'il sait rendre le jour, la nuit, ou les deux.

L'éditeur d'un holon a son profil dans `editeurs/<nom>/` : `editeur.txt`
(`nom = …`) et, s'il en a une, son image de profil `avatar.svg` (ou .png,
.webp). Ce que développe Holarch porte l'éditeur `holarch-system`.

`python outils/catalogue.py` recalcule `catalogue.json`, que la
Bibliothèque lit ; `--verifie` refuse un catalogue pas à jour.

Premiers holons recensés : **Écriture** et **Tableur**, les deux modes de
l'Atelier, et les thèmes **Désert** et **No Futur** (leur source est dans
Holarch-windows). **Bloc-notes** est le premier holon qu'on installe
vraiment depuis la Bibliothèque.

## Un holon installable

Un holon que la Bibliothèque sait installer a, en plus de sa vitrine, son
**paquet** (exemple : `apps/bloc-notes/`) :

| Fichier | Contenu |
|---|---|
| `manifeste.json` | le manifeste du format `.hln` : `id`, `nom`, `genre`, `version`, `abi`, `editeur`, `droits` demandés, `licence`… |
| `holon/` | ses fichiers, **source seulement** ; `index.html` est l'entrée, ses `<link rel="stylesheet">` et `<script src>` locaux y sont mis en ligne par Holarch ; `glyphe.svg` (facultatif) donne le dessin de sa sphère (des `<path>` seulement, sur 32 × 32) |
| `signature.txt` | le condensé du paquet, signé par l'éditeur |

Le **condensé** est exactement celui d'une capsule `.hln` faite du même
manifeste et des mêmes fichiers. Holarch télécharge les fichiers, recalcule
le condensé lui-même, vérifie la signature avec la clé de l'éditeur **qu'il
connaît déjà** (pas celle que dit le catalogue), montre à l'écran les droits
demandés, et n'installe qu'avec l'accord de l'utilisateur. Un seul octet
changé et l'installation est refusée.

- `python outils/signer.py apps/<holon> --cle <fichier>` (ou la variable
  `HOLARCH_EDITEUR`) signe le paquet ; la clé publique doit être celle de
  `editeurs/<éditeur>/editeur.txt` (champ `clé`). **La clé privée ne va
  jamais dans ce dépôt.**
- `python outils/catalogue.py` refuse un holon modifié depuis sa signature.

Un holon tourne **isolé** : pas d'accès au Bureau, aux fichiers, au réseau
ni aux autres holons. Il ne parle à Holarch que par `window.holarch` :

| Appel | Droit | Effet |
|---|---|---|
| `holarch.lire(clé)` | `stockage:propre` | promesse du texte rangé sous cette clé, ou `null` |
| `holarch.ecrire(clé, texte)` | `stockage:propre` | range le texte (2 Mo au plus pour tout le holon) |
| `holarch.effacer(clé)`, `holarch.cles()` | `stockage:propre` | efface une clé, liste les clés |
| `holarch.apparence.nuit` | | `true` la nuit ; l'évènement `holarch:apparence` signale le changement |
| `holarch.droits` | | les droits accordés |

Droits que Holarch sait accorder aujourd'hui : `ecran` (ouvrir sa fenêtre)
et `stockage:propre` (garder ses propres données, rangées dans Holarch). Un
holon qui en demande un autre est refusé. Désinstallé, il part avec ses
données.

## Licences

Chaque application aura la sienne, dite dans son origine (identifiant
SPDX). Le reste du dépôt (textes, outils) est sous licence MIT
(`LICENSE`).
