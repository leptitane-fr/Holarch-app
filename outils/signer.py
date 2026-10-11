#!/usr/bin/env python3
"""Signe le paquet d'un holon (voir outils/paquet.py) : écrit `<dossier>/signature.txt`.

La clé de l'éditeur ne va jamais dans ce dépôt. Elle vient de la variable HOLARCH_EDITEUR
(64 caractères hexadécimaux, la même que pour holarch.hln dans Holarch-windows), ou d'un
fichier passé par --cle. Sa clé publique doit être celle de `editeurs/<éditeur>/editeur.txt`
(champ « clé »), que Holarch connaît déjà.

Usage : HOLARCH_EDITEUR=… python outils/signer.py apps/bloc-notes [--editeur holarch-system]
        python outils/signer.py apps/bloc-notes --cle chemin/de/la/cle
"""
import os
import sys
from pathlib import Path

from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

sys.path.insert(0, str(Path(__file__).resolve().parent))
from paquet import champs, condense, fichiers, manifeste_canonique  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent


def main():
    args = sys.argv[1:]
    option = lambda nom, defaut=None: args[args.index(nom) + 1] if nom in args else defaut  # noqa: E731
    dossiers = [a for i, a in enumerate(args) if not a.startswith("--") and (i == 0 or not args[i - 1].startswith("--"))]
    if len(dossiers) != 1:
        raise SystemExit(__doc__)
    dossier = (ROOT / dossiers[0]).resolve()
    editeur = option("--editeur", champs(dossier / "vitrine.txt").get("éditeur", "holarch-system"))
    hexa = Path(option("--cle")).read_text().strip() if option("--cle") else os.environ.get("HOLARCH_EDITEUR", "")
    if len(hexa) != 64:
        raise SystemExit("clé de l'éditeur absente : HOLARCH_EDITEUR (64 caractères hexadécimaux) ou --cle")
    cle = Ed25519PrivateKey.from_private_bytes(bytes.fromhex(hexa))
    publique = cle.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw).hex()
    connue = champs(ROOT / "editeurs" / editeur / "editeur.txt").get("clé")
    if connue != publique:
        raise SystemExit(f"cette clé n'est pas celle de editeurs/{editeur}/editeur.txt (clé publique {publique})")
    texte, _ = manifeste_canonique(dossier / "manifeste.json")
    c = condense(texte, fichiers(dossier / "holon"))
    signature = cle.sign(b"HLN1 editeur" + bytes.fromhex(c)).hex()
    (dossier / "signature.txt").write_text(
        f"condensé = {c}\néditeur = {editeur}\nclé = {publique}\nsignature = {signature}\n", "utf-8"
    )
    print(f"{dossier.relative_to(ROOT)}/signature.txt : condensé {c[:16]}…")


if __name__ == "__main__":
    main()
