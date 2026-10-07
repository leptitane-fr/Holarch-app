"""Le paquet d'un holon publié dans ce dépôt : ce que Holarch télécharge, vérifie et installe.

Dans le dossier du holon :
    manifeste.json   le manifeste du format .hln (champs et ordre : hln/src/manifeste.rs de
                     Holarch-windows) ; il demande des droits, Holarch montre et accorde
    holon/           les fichiers du holon, tels quels (index.html est l'entrée)
    signature.txt    le condensé, signé par l'éditeur (outils/signer.py)

Le condensé est exactement celui d'une capsule .hln (hln/FORMAT.md) faite du même manifeste et
des mêmes fichiers : Holarch le recalcule sur ce qu'il a téléchargé, sans faire confiance au
catalogue, et vérifie la signature de l'éditeur avec la clé qu'il connaît déjà.
"""
import hashlib
import json
import struct
from pathlib import Path

ORDRE = ["format", "id", "nom", "genre", "version", "abi", "editeur", "droits", "interfaces", "dependances", "licence"]
GENRES = {"holarch", "holon-app", "holon-sys", "holon-web", "donnees"}
BLOC = 64 * 1024


def _sha(*parties):
    h = hashlib.sha256()
    for p in parties:
        h.update(p)
    return h.digest()


def _mot(t):
    return bool(t) and len(t) <= 128 and all(c.islower() and c.isascii() or c.isdigit() or c in "._:-/" for c in t)


def manifeste_canonique(chemin):
    """Le manifeste tel que l'écrit Holarch (JSON compact, champs dans l'ordre du format)."""
    m = json.loads(Path(chemin).read_text("utf-8"))
    m.setdefault("droits", []), m.setdefault("interfaces", []), m.setdefault("dependances", [])
    inconnus = set(m) - set(ORDRE)
    if inconnus:
        raise SystemExit(f"{chemin} : champs inconnus {sorted(inconnus)}")
    manque = [k for k in ORDRE if k not in m]
    if manque:
        raise SystemExit(f"{chemin} : champs manquants {manque}")
    if m["format"] != 1 or m["genre"] not in GENRES or not _mot(m["id"]):
        raise SystemExit(f"{chemin} : format, genre ou id invalide")
    for k in ("droits", "interfaces", "dependances"):
        if len(set(m[k])) != len(m[k]) or not all(_mot(x) for x in m[k]):
            raise SystemExit(f"{chemin} : « {k} » invalide (mots en minuscules, sans doublon)")
    return json.dumps({k: m[k] for k in ORDRE}, ensure_ascii=False, separators=(",", ":")), m


def fichiers(racine):
    """Les fichiers du holon, triés comme dans une capsule (par octets du chemin)."""
    racine = Path(racine)
    liste = [p for p in racine.rglob("*") if p.is_file()]
    return sorted(((p.relative_to(racine).as_posix(), p.read_bytes()) for p in liste), key=lambda x: x[0].encode())


def _texte(t):
    b = t.encode()
    return struct.pack("<H", len(b)) + b


def _racine(feuilles):
    if not feuilles:
        return _sha(b"HLN1 vide")
    rang = feuilles
    while len(rang) > 1:
        rang = [_sha(b"\x01", rang[i], rang[i + 1]) if i + 1 < len(rang) else rang[i] for i in range(0, len(rang), 2)]
    return rang[0]


def condense(manifeste, liste):
    """Le condensé .hln : SHA-256("HLN1 condense" ‖ SHA-256(manifeste) ‖ fichiers ‖ racine ‖ enfants)."""
    flux = b"".join(o for _, o in liste)
    feuilles = [_sha(b"\x00", b"HLN1 bloc", flux[i:i + BLOC]) for i in range(0, len(flux), BLOC)]
    e = b"HLN1 condense" + _sha(manifeste.encode()) + struct.pack("<I", len(liste))
    for chemin, o in liste:
        e += _texte(chemin) + bytes([0]) + struct.pack("<Q", len(o))
    e += _racine(feuilles) + struct.pack("<I", 0)
    return _sha(e).hex()


def champs(path):
    if not path.is_file():
        return {}
    return dict(l.split(" = ", 1) for l in path.read_text("utf-8").splitlines() if " = " in l)


def paquet(dossier, rel):
    """Le paquet pour le catalogue, ou None si le holon n'en a pas (pas encore installable)."""
    if not (dossier / "holon").is_dir():
        return None
    texte, m = manifeste_canonique(dossier / "manifeste.json")
    liste = fichiers(dossier / "holon")
    if "index.html" not in [c for c, _ in liste]:
        raise SystemExit(f"{rel}/holon : index.html manque")
    s = champs(dossier / "signature.txt")
    c = condense(texte, liste)
    if s.get("condensé") != c:
        raise SystemExit(f"{rel} : le holon a changé depuis sa signature : python outils/signer.py {rel}")
    return {
        "manifeste": texte,
        "racine": f"{rel}/holon",
        "fichiers": [{"chemin": ch, "longueur": len(o)} for ch, o in liste],
        "condense": c,
        "editeur": s["éditeur"],
        "cle": s["clé"],
        "signature": s["signature"],
    }, m
