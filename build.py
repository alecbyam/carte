# -*- coding: utf-8 -*-
"""
Generateur de cartes CR80 (recto/verso, QR code, import Excel).
Produit un fichier HTML autonome, 100% local (aucune dependance reseau au runtime).

Usage:
  python build.py                                   -> index.html, liste vide (build public/demo)
  python build.py --source beneficiaires.tsv         -> index.html pre-rempli depuis un TSV local
  python build.py --source data.tsv --out sortie.html
"""
import argparse
import base64
import csv
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor")

ITEMS_SHORT = [
    "Bidon 20L", "Kit lave-mains", "Savon 800g", "Gobelet 700ml",
    "Etoffe wax", "Aquatabs", "Pot bebe", "Sac bailleur",
]


def code_village_part(*candidates):
    # Lettres uniquement (un village "6" ne doit pas donner TF6-...) ; repli village -> chefferie -> site.
    for cand in candidates:
        s = re.sub(r"[^A-Za-z]", "", cand or "").upper()
        if s:
            return s[:3]
    return "SIT"


def parse_tsv(path):
    rows = []
    village_counters = {}
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        for r in reader:
            if len(r) < 5 or not r[3].strip():
                continue
            village = r[1].strip()
            chefferie = r[2].strip()
            nom = r[3].strip().strip('"').replace("\n", " ").strip()
            sexe = r[4].strip()
            qtys = [r[i].strip() if i < len(r) else "" for i in range(5, 13)]
            vpart = code_village_part(village, chefferie)
            village_counters[vpart] = village_counters.get(vpart, 0) + 1
            num = f"TF{vpart}-{village_counters[vpart]:03d}"
            rows.append({
                "num": num, "nom": nom, "sexe": sexe,
                "village": village, "chefferie": chefferie, "site": "", "statut": "",
                "qtys": qtys,
            })
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", help="Fichier TSV local a pre-charger (optionnel). Sans cette option, l'app demarre vide.")
    ap.add_argument("--out", default=os.path.join(HERE, "index.html"), help="Chemin du fichier HTML genere.")
    ap.add_argument("--title", default="Cartes CR80 - Distribution WASH/NFI", help="Titre affiche dans la page.")
    args = ap.parse_args()

    rows = parse_tsv(args.source) if args.source else []

    seed_json = json.dumps(rows, ensure_ascii=False)
    items_json = json.dumps(ITEMS_SHORT, ensure_ascii=False)

    qr_lib = open(os.path.join(VENDOR, "qrcode.js"), encoding="utf-8").read()
    qr_utf8 = open(os.path.join(VENDOR, "qrcode_UTF8.js"), encoding="utf-8").read()
    xlsx_lib = open(os.path.join(VENDOR, "xlsx.core.min.js"), encoding="utf-8").read()
    html2canvas_lib = open(os.path.join(VENDOR, "html2canvas.min.js"), encoding="utf-8").read()
    jspdf_lib = open(os.path.join(VENDOR, "jspdf.umd.min.js"), encoding="utf-8").read()

    # Logo incorpore en data: URI directement dans le HTML : il s'affiche et s'exporte en PDF
    # partout, y compris quand le fichier est ouvert en local (file://), sans "tainted canvas".
    logo_data = ""
    logo_path = os.path.join(HERE, "logo.png")
    if os.path.exists(logo_path):
        logo_data = "data:image/png;base64," + base64.b64encode(open(logo_path, "rb").read()).decode()

    template_path = os.path.join(HERE, "template.html")
    template = open(template_path, encoding="utf-8").read()

    html_doc = (template
        .replace("__TITLE__", args.title)
        .replace("__COUNT__", str(len(rows)))
        .replace("__SEED_JSON__", seed_json)
        .replace("__ITEMS_JSON__", items_json)
        .replace("__QR_LIB__", qr_lib)
        .replace("__QR_UTF8__", qr_utf8)
        .replace("__XLSX_LIB__", xlsx_lib)
        .replace("__HTML2CANVAS_LIB__", html2canvas_lib)
        .replace("__JSPDF_LIB__", jspdf_lib)
        .replace("__LOGO_DATA__", logo_data)
    )

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html_doc)

    print(f"OK: {len(rows)} beneficiaire(s) -> {args.out}")
    print(f"Taille fichier: {os.path.getsize(args.out)/1024:.0f} Ko")


if __name__ == "__main__":
    main()
