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

## Licences

Chaque application aura la sienne, dite dans son origine (identifiant
SPDX). Le reste du dépôt (textes, outils) est sous licence MIT
(`LICENSE`).
