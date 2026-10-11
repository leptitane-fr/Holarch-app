// Bloc-notes, un holon de Holarch. Il ne voit que ce que Holarch lui donne (window.holarch) :
// ses propres données (droit stockage:propre) et l'apparence (jour ou nuit). Ni fichiers, ni réseau.
"use strict";

const holarch = window.holarch;
const CLE = "notes";
const $ = (id) => document.getElementById(id);
const el = {
  liste: $("notes"), aucune: $("aucune"), recherche: $("recherche"), editeur: $("editeur"),
  accueil: $("accueil"), texte: $("texte"), date: $("date"), compte: $("compte"), etat: $("etat"),
  supprimer: $("supprimer"), confirmer: $("confirmer"),
};

/** @type {{id: string, texte: string, cree: number, modifie: number}[]} */
let notes = [];
let choisie = null;
let attente = null;

// --- Enregistrement : à chaque frappe, regroupé ; tout de suite si la fenêtre perd la main.
async function charger() {
  try {
    const t = await holarch.lire(CLE);
    const n = t ? JSON.parse(t) : [];
    if (Array.isArray(n)) notes = n.filter((x) => x && typeof x.texte === "string");
  } catch {
    notes = [];
  }
}
function enregistrer(tout_de_suite) {
  clearTimeout(attente);
  el.etat.textContent = "…";
  const ecrire = () => {
    attente = null;
    holarch.ecrire(CLE, JSON.stringify(notes)).then(
      () => (el.etat.textContent = "Enregistré"),
      () => (el.etat.textContent = "Non enregistré"),
    );
  };
  if (tout_de_suite) ecrire();
  else attente = setTimeout(ecrire, 350);
}
const vider = () => attente && enregistrer(true);
addEventListener("blur", vider);
addEventListener("pagehide", vider);
document.addEventListener("visibilitychange", vider);

// --- Ce qu'on affiche d'une note.
const lignes = (n) => n.texte.split("\n").map((l) => l.trim()).filter(Boolean);
const titre = (n) => lignes(n)[0]?.slice(0, 120) || "Note sans titre";
const extrait = (n) => lignes(n).slice(1).join(" ").slice(0, 160);
const deuxChiffres = (x) => String(x).padStart(2, "0");
function quand(t, long) {
  const d = new Date(t), maintenant = new Date();
  const heure = `${deuxChiffres(d.getHours())}:${deuxChiffres(d.getMinutes())}`;
  const jour = (x) => new Date(x.getFullYear(), x.getMonth(), x.getDate()).getTime();
  const ecart = Math.round((jour(maintenant) - jour(d)) / 864e5);
  if (long) {
    const date = d.toLocaleDateString("fr-FR", { weekday: "long", day: "numeric", month: "long", year: "numeric" });
    return `${date} à ${heure}`;
  }
  const s = (Date.now() - t) / 1000;
  if (s < 60) return "à l'instant";
  if (s < 3600) return `il y a ${Math.floor(s / 60)} min`;
  if (ecart === 0) return heure;
  if (ecart === 1) return "hier";
  if (ecart < 7) return d.toLocaleDateString("fr-FR", { weekday: "long" });
  return `${deuxChiffres(d.getDate())}/${deuxChiffres(d.getMonth() + 1)}/${d.getFullYear()}`;
}
function surligne(parent, texte, q) {
  const i = q ? texte.toLowerCase().indexOf(q) : -1;
  if (i < 0) { parent.append(texte); return; }
  const m = document.createElement("mark");
  m.textContent = texte.slice(i, i + q.length);
  parent.append(texte.slice(0, i), m, texte.slice(i + q.length));
}

function dessinerListe() {
  const q = el.recherche.value.trim().toLowerCase();
  const vues = notes
    .filter((n) => !q || n.texte.toLowerCase().includes(q))
    .sort((a, b) => b.modifie - a.modifie);
  el.liste.replaceChildren(
    ...vues.map((n) => {
      const li = document.createElement("li");
      const b = document.createElement("button");
      b.setAttribute("aria-current", String(n.id === choisie));
      const t = document.createElement("b");
      surligne(t, titre(n), q);
      const s = document.createElement("span");
      const i = document.createElement("i");
      surligne(i, extrait(n) || "Pas d'autre texte", q);
      s.append(quand(n.modifie), i);
      b.append(t, s);
      b.onclick = () => choisir(n.id);
      li.append(b);
      return li;
    }),
  );
  el.aucune.hidden = !(q && !vues.length);
  el.aucune.textContent = `Aucune note ne contient « ${el.recherche.value.trim()} ».`;
}

function dessinerNote() {
  const n = notes.find((x) => x.id === choisie);
  el.editeur.hidden = !n;
  el.accueil.hidden = !!notes.length;
  el.confirmer.hidden = true;
  el.supprimer.hidden = false;
  if (!n) return;
  if (el.texte.value !== n.texte) el.texte.value = n.texte;
  el.date.textContent = `Modifiée le ${quand(n.modifie, true)}`;
  compter(n);
}
function compter(n) {
  const mots = (n.texte.match(/[\p{L}\p{N}'’-]+/gu) || []).length;
  const car = [...n.texte].length;
  el.compte.textContent = `${mots} mot${mots > 1 ? "s" : ""} · ${car} caractère${car > 1 ? "s" : ""}`;
}

function choisir(id) {
  vider();
  choisie = id;
  dessinerListe();
  dessinerNote();
  el.texte.focus();
}
function nouvelle() {
  // Une note vide déjà ouverte sert de nouvelle note.
  const vide = notes.find((n) => !n.texte.trim());
  if (vide) { el.recherche.value = ""; choisir(vide.id); return; }
  const t = Date.now();
  const n = { id: t.toString(36) + Math.random().toString(36).slice(2, 6), texte: "", cree: t, modifie: t };
  notes.push(n);
  el.recherche.value = "";
  choisir(n.id);
  enregistrer();
}

el.texte.addEventListener("input", () => {
  const n = notes.find((x) => x.id === choisie);
  if (!n) return;
  n.texte = el.texte.value;
  n.modifie = Date.now();
  compter(n);
  el.date.textContent = "Modifiée à l'instant";
  dessinerListe();
  enregistrer();
});
el.recherche.addEventListener("input", dessinerListe);
$("nouvelle").onclick = nouvelle;
$("premiere").onclick = nouvelle;
el.supprimer.onclick = () => {
  el.confirmer.hidden = false;
  el.supprimer.hidden = true;
  $("non").focus();
};
$("non").onclick = () => dessinerNote();
$("oui").onclick = () => {
  const reste = notes.filter((n) => n.id !== choisie).sort((a, b) => b.modifie - a.modifie);
  notes = notes.filter((n) => n.id !== choisie);
  choisie = reste[0]?.id ?? null;
  enregistrer(true);
  dessinerListe();
  dessinerNote();
};
addEventListener("keydown", (e) => {
  const ctrl = e.ctrlKey || e.metaKey;
  if (ctrl && e.key.toLowerCase() === "n") { e.preventDefault(); nouvelle(); }
  else if (ctrl && e.key.toLowerCase() === "f") { e.preventDefault(); el.recherche.focus(); el.recherche.select(); }
  else if (e.key === "Escape" && document.activeElement === el.recherche) { el.recherche.value = ""; dessinerListe(); el.texte.focus(); }
});
// Les dates relatives (« il y a 3 min ») restent justes.
setInterval(dessinerListe, 60_000);

// --- Jour ou nuit, comme le thème de Holarch.
const apparence = (a) => document.documentElement.classList.toggle("jour", !a?.nuit);
apparence(holarch.apparence);
addEventListener("holarch:apparence", (e) => apparence(e.detail));

charger().then(() => {
  choisie = [...notes].sort((a, b) => b.modifie - a.modifie)[0]?.id ?? null;
  dessinerListe();
  dessinerNote();
  if (choisie) el.texte.focus();
});
