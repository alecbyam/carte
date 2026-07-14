# Carte — générateur de cartes de distribution CR80

Outil local pour générer des cartes bénéficiaire au format **CR80** (85,60 × 53,98 mm, norme carte bancaire/ID) pour des distributions de kits WASH/NFI : recto (identité + QR code) et verso (articles reçus + signatures).

## Confidentialité

**Toutes les données restent dans le navigateur de la personne qui les utilise.** Cette page ne contient aucun backend, aucune base de données, aucun envoi réseau : l'import Excel, la génération des QR codes, le logo et les cartes sont traités et stockés en local (`localStorage`), y compris lorsque la page est servie depuis Railway/GitHub Pages. Le fichier `index.html` publié dans ce dépôt démarre **volontairement vide** — aucune donnée de bénéficiaire réelle n'est commit ici.

## Utilisation

1. Ouvrir `index.html` (en local, en double-cliquant dessus, ou via l'URL Railway/GitHub Pages).
2. **Importer un fichier Excel** (`.xlsx`/`.xls`/`.csv`) contenant une ou plusieurs feuilles de distribution — les colonnes (Nom, Sexe, Village, Chefferie, Site, articles) sont détectées automatiquement même si leurs intitulés varient d'une feuille à l'autre. *Ou* ajouter des bénéficiaires un par un via le formulaire.
3. Chaque bénéficiaire obtient aussitôt sa carte CR80 recto/verso avec QR code.
4. Bouton **PDF** par carte, ou **Imprimer toutes les cartes** pour un lot — via "Enregistrer en PDF" dans la boîte d'impression du navigateur.
5. Logo : déposer un fichier `logo.png` à côté d'`index.html`, ou utiliser le bouton **Logo** dans la page.

## Développement local

```bash
python build.py                    # build public, liste vide -> index.html
python build.py --source data.tsv  # build pré-rempli à partir d'un TSV local (ne pas committer ce TSV s'il contient de vraies données)
```

`template.html` contient la page ; `vendor/` contient les librairies tierces embarquées (aucune dépendance réseau au runtime) :
- [qrcode-generator](https://github.com/kazuhikoarase/qrcode-generator) (MIT) — génération des QR codes.
- [SheetJS / xlsx](https://sheetjs.com) (Apache-2.0), build `core` — lecture des fichiers Excel.

## Déploiement Railway

Le dépôt contient un `package.json` minimal qui sert les fichiers statiques (`serve`). Railway détecte le projet Node et lance `npm start`.
