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
import csv
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
VENDOR = os.path.join(HERE, "vendor")

ITEMS_SHORT = [
    "Bidon 20L", "Kit lave-mains", "Savon 800g", "Gobelet 700ml",
    "Etoffe wax", "Aquatabs", "Pot bebe", "Sac bailleur",
]


def parse_tsv(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        reader = csv.reader(f, delimiter="\t")
        next(reader)
        running_num = 0
        for r in reader:
            if len(r) < 5 or not r[3].strip():
                continue
            running_num += 1
            num = r[0].strip() or f"{running_num:03d}"
            village = r[1].strip()
            chefferie = r[2].strip()
            nom = r[3].strip().strip('"').replace("\n", " ").strip()
            sexe = r[4].strip()
            qtys = [r[i].strip() if i < len(r) else "" for i in range(5, 13)]
            rows.append({
                "num": num, "nom": nom, "sexe": sexe,
                "village": village, "chefferie": chefferie, "site": "",
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
    )

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(html_doc)

    print(f"OK: {len(rows)} beneficiaire(s) -> {args.out}")
    print(f"Taille fichier: {os.path.getsize(args.out)/1024:.0f} Ko")


if __name__ == "__main__":
    main()
