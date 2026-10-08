# Gunman Contracts — Stand Alone: French translation

French text and subtitles for Gunman Contracts — Stand Alone, plus a **Français**
entry in the game's language menu. Voice acting remains in English.

Unofficial fan translation, not affiliated with the game's creators. Game assets
are not distributed here and remain the property of their respective rights holders.

[Français ci-dessous](#français)

## Install

Close the game, then from this repository's root directory:

```bash
python -m pip install -r requirements.txt
python install.py
```

`install.py` runs, in order: `tools/apply_text.py` (writes the main text table),
`tools/add_out_of_table_lines.py` (adds the subtitles the table has no row for),
`tools/apply_scene_hints.py` (translates the interaction hints baked into the
scenes), then the menu patch (below) so **Français** is selectable in the game.

Options: `--dry-run` (report only), `--no-menu` (texts only), `--overwrite-de`
(the fallback below), `--restore` (undo the menu patch and restore the `.orig` files), and a custom install
path: `python install.py "D:/Games/Gunman Contracts - Stand Alone"` (the game
folder, or its `GunmanContracts_Data` subfolder). The Steam library path is the
default.

## The language menu

The stock game only offers **English** and **Deutsch**. The install adds
**Français** as a third entry through the loaderless patch (`tools/apply_french_patch.py`):
three byte edits in existing game files, no mod loader, nothing running
alongside the game — the game's mod detector stays silent and Steam highscores
keep working. Apply or undo it on its own with `tools/install_patch.bat` /
`tools/restore_patch.bat`.

**Fallback, without touching game binaries**: `python install.py --overwrite-de`
writes French over the Deutsch entry as well; select **Options → Language →
Deutsch** to display the translation. This replaces the German text.

If you used an earlier version of these scripts (French displayed through
Deutsch): run Steam's "verify integrity" to restore the original files, run
`python install.py` again — Français becomes selectable and the German text
comes back.

## Updating

Run `python install.py` again after a game update or a Steam file verification
(both restore the original files). The translation text lives in
`data/fr_strings.json`; `--overwrite-de` is only for the fallback path.

## Backup and restore

The first time a tool rewrites a game file it keeps the untouched copy as
`<file>.orig` (for example `resources.assets.orig`); every run also leaves a
timestamped `<file>.orig-backup-<date>` (the file as it was before that run).
Each file is written next to the original and read back before it replaces it.
The menu patch saves its original bytes to `GC-FR-patch-backup.json` in the game
folder. `python install.py --restore` undoes the menu patch and puts every
`.orig` back. After a game update, delete the `.orig` files before reinstalling:
they belong to the previous version. All tools refuse to run while
`GunmanContracts.exe` is running (the check warns when it cannot run).

## Tools

| Tool | Purpose |
| --- | --- |
| `install.py` | One-command install: texts + menu entry. |
| `tools/apply_text.py` | Write the main text table (FR column; DE only with `--overwrite-de`; `--apply` / `--dry-run`). |
| `tools/add_out_of_table_lines.py` | Add subtitles whose clip names the table lacks (`--apply` / `--dry-run`). |
| `tools/apply_scene_hints.py` | Translate the interaction hints baked into the scenes (`--apply` / `--dry-run`). |
| `tools/find_missing_keys.py` | Find where a displayed string comes from: the table or a baked asset. |
| `tools/fix_broken_rows.py` | Repair table rows split by a bare line feed. |
| `tools/verify_game_text.py` | Read the installed table back and compare it with this repository (DE too with `--overwrite-de`). |
| `tools/apply_french_patch.py` | The loaderless menu patch (apply / check / restore). |
| `tools/common.py` | Shared helpers: game location, running guard, backups, verified writes. |
| `data/` | The translation itself: `fr_strings.json`, the out-of-table lines, the scene hints. |

## Limits

- Voice acting stays in English; only text and subtitles are translated.
- A game update or Steam file verification reverts everything: re-run `python install.py`.
- The menu patch targets game version 0.3.1.1; on another version it refuses to
  touch unrecognised bytes and says so.
- `tools/verify_game_text.py` compares only the keys of `data/fr_strings.json` that
  the table already carries; the out-of-table lines and the scene hints have
  their own reports.

---

## Français

Traduction française des textes et sous-titres de Gunman Contracts — Stand Alone,
avec une entrée **Français** dans le menu des langues du jeu. Le doublage reste
en anglais.

Traduction non officielle, sans affiliation avec les créateurs du jeu. Les assets
du jeu ne sont pas distribués ici et restent la propriété de leurs ayants droit.

### Installer

Fermer le jeu, puis depuis la racine du dépôt :

```bash
python -m pip install -r requirements.txt
python install.py
```

`install.py` exécute, dans l'ordre : `tools/apply_text.py` (écrit la table
principale), `tools/add_out_of_table_lines.py` (ajoute les sous-titres dont la
table n'a pas de ligne), `tools/apply_scene_hints.py` (traduit les libellés
d'interaction écrits dans les scènes), puis le patch du menu (ci-dessous) pour
que **Français** soit sélectionnable dans le jeu.

Options : `--dry-run` (signale sans écrire), `--no-menu` (textes seulement),
`--overwrite-de` (repli ci-dessous), `--restore` (annule le patch du menu et remet les `.orig`), et un
chemin personnalisé : `python install.py "D:/Games/Gunman Contracts - Stand Alone"`
(le dossier du jeu, ou son sous-dossier `GunmanContracts_Data`). Le chemin Steam
est utilisé par défaut.

### Le menu des langues

Le jeu de base ne propose que **English** et **Deutsch**. L'installation ajoute
**Français** comme troisième entrée via le patch sans mod loader
(`tools/apply_french_patch.py`) : trois modifications d'octets dans les fichiers du jeu,
aucun mod loader, rien qui tourne à côté — la détection de mods du jeu reste
muette et les highscores Steam continuent de fonctionner. Application ou
annulation seules : `tools/install_patch.bat` / `tools/restore_patch.bat`.

**Repli, sans toucher aux binaires du jeu** : `python install.py --overwrite-de`
écrit aussi le français dans l'entrée Deutsch ; sélectionner **Options →
Language → Deutsch** pour afficher la traduction. Le texte allemand est alors
remplacé.

Si vous avez utilisé une version antérieure de ces scripts (français affiché via
Deutsch) : lancer « vérifier l'intégrité des fichiers » dans Steam pour restaurer
les fichiers d'origine, relancer `python install.py` — Français devient
sélectionnable et le texte allemand revient.

### Mettre à jour

Relancer `python install.py` après une mise à jour du jeu ou une vérification des
fichiers Steam (les deux restaurent les fichiers d'origine). Le texte de la
traduction vit dans `data/fr_strings.json` ; `--overwrite-de` ne sert qu'au
repli.

### Sauvegarde et restauration

La première fois qu'un outil réécrit un fichier du jeu, il en garde la copie
intacte sous `<fichier>.orig` (par exemple `resources.assets.orig`) ; chaque
exécution laisse aussi une sauvegarde horodatée `<fichier>.orig-backup-<date>`.
Chaque fichier est écrit à côté de l'original et relu avant de le remplacer. Le
patch du menu sauvegarde ses octets d'origine dans `GC-FR-patch-backup.json`
(dossier du jeu). `python install.py --restore` annule le patch du menu et remet
tous les `.orig` en place. Après une mise à jour du jeu, supprimer les `.orig`
avant de réinstaller : ils appartiennent à la version précédente. Tous les outils refusent de tourner
si `GunmanContracts.exe` est en cours d'exécution (le contrôle prévient quand il
ne peut pas s'exécuter).

### Outils

Voir le tableau de la section anglaise : `install.py` orchestre tout ; tous les
scripts (pipeline et patch du menu) vivent dans `tools/` ; les données de
traduction dans `data/`.

### Limites

- Le doublage reste en anglais ; seuls les textes et sous-titres sont traduits.
- Une mise à jour du jeu ou une vérification Steam rétablit tout : relancer
  `python install.py`.
- Le patch du menu cible la version 0.3.1.1 du jeu ; sur une autre version, il
  refuse de toucher aux octets non reconnus et le signale.
- `tools/verify_game_text.py` ne compare que les clés de `data/fr_strings.json` que la
  table porte déjà ; les lignes hors table et les libellés de scènes ont leurs
  propres rapports.
