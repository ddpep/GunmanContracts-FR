# Gunman Contracts — Stand Alone: French translation

French text and subtitles for Gunman Contracts — Stand Alone. Voice acting remains in English.

Unofficial fan translation, not affiliated with the game's creators. Game assets
are not distributed here and remain the property of their respective rights holders.

[Français ci-dessous](#français)

## Install or update

On the PC where the game is installed, close the game and run these commands
from this repository's root directory:

```bash
python -m pip install -r requirements.txt
python apply_text.py --overwrite-de
python add_out_of_table_lines.py --apply
python apply_scene_hints.py --apply
```

Three steps, in this order. `apply_text.py` writes the main table.
`add_out_of_table_lines.py` then appends the rows the dubbing needs but the table
does not carry, so those subtitles exist at all. `apply_scene_hints.py` finally
translates the interaction hints the game reads from its **scenes** rather than
from the table. Running only the first step leaves both gaps in place. Each of
the last two also accepts `--dry-run`, which reports without writing.

The current game version offers **English** and **Deutsch**, but no selectable
French language. The command above writes French to both the FR and DE entries;
select **Options → Language → Deutsch** in the game to display the translation.
This replaces German text.

By default, the script looks for `resources.assets` in:

`C:/Program Files (x86)/Steam/steamapps/common/Gunman Contracts - Stand Alone/GunmanContracts_Data`

For another installation, pass the path to **GunmanContracts_Data** (not the
`resources.assets` file):

```bash
python apply_text.py --overwrite-de "C:\path\to\GunmanContracts_Data"
python add_out_of_table_lines.py --apply "C:\path\to\GunmanContracts_Data"
python apply_scene_hints.py --apply "C:\path\to\GunmanContracts_Data"
```

To update an already patched game, run the same command again. The script reads
translations from `fr_strings.json` and replaces existing FR values. DE is
changed **only** with `--overwrite-de`; keep the flag when updating a game that
displays French through Deutsch. Without it, earlier French text in DE is not
updated. A game update or Steam file verification may restore the original
asset, in which case you can run the command again.

Before writing, the script creates a timestamped
`resources.assets.orig-backup-<date>` file next to `resources.assets`. Each backup
contains the asset as it was **before that run**; later backups may therefore
contain an already patched asset. To restore, close the game and replace
`resources.assets` with the backup from the desired run. The script checks the
asset size and refuses to write if the output is unexpectedly small. On Windows
it also refuses to run if `GunmanContracts.exe` is detected; if the check cannot
run, it warns you to verify manually that the game is closed.

---

## Français

Traduction française des textes et sous-titres de Gunman Contracts — Stand Alone.
Le doublage reste en anglais.

Traduction non officielle, sans affiliation avec les créateurs du jeu. Les assets
du jeu ne sont pas distribués ici et restent la propriété de leurs ayants droit.

### Installer ou mettre à jour

Sur le PC où le jeu est installé, fermer le jeu et lancer ces commandes depuis
la racine du dépôt :

```bash
python -m pip install -r requirements.txt
python apply_text.py --overwrite-de
python add_out_of_table_lines.py --apply
python apply_scene_hints.py --apply
```

Trois étapes, dans cet ordre. `apply_text.py` écrit la table principale.
`add_out_of_table_lines.py` ajoute ensuite les lignes dont le doublage a besoin
mais que la table ne porte pas, sans quoi ces sous-titres n'existent pas.
`apply_scene_hints.py` traduit enfin les libellés d'interaction que le jeu lit
dans ses **scènes** et non dans la table. Ne lancer que la première étape laisse
ces deux manques en place. Les deux dernières acceptent aussi `--dry-run`, qui
signale sans écrire.

La version actuelle du jeu propose **English** et **Deutsch**, mais pas de
français sélectionnable. La commande ci-dessus écrit le français dans les
entrées FR et DE ; sélectionner **Options → Langue → Deutsch** dans le jeu pour
afficher la traduction. Le texte allemand est remplacé.

Par défaut, le script cherche `resources.assets` dans :

`C:/Program Files (x86)/Steam/steamapps/common/Gunman Contracts - Stand Alone/GunmanContracts_Data`

Pour une autre installation, passer le chemin du dossier **GunmanContracts_Data**
(et non celui du fichier `resources.assets`) :

```bash
python apply_text.py --overwrite-de "C:\chemin\vers\GunmanContracts_Data"
python add_out_of_table_lines.py --apply "C:\chemin\vers\GunmanContracts_Data"
python apply_scene_hints.py --apply "C:\chemin\vers\GunmanContracts_Data"
```

Pour mettre à jour un jeu déjà patché, relancer la même commande. Le script lit
`fr_strings.json` et remplace les valeurs FR existantes. DE n'est modifié
**qu'avec** `--overwrite-de` ; conserver cette option si le jeu affiche le
français via Deutsch. Sans elle, l'ancien texte français dans DE n'est pas
actualisé. Une mise à jour du jeu ou une vérification des fichiers Steam peut
rétablir l'asset d'origine ; relancer alors la commande.

Avant d'écrire, le script crée une sauvegarde horodatée
`resources.assets.orig-backup-<date>` à côté de `resources.assets`. Chaque
sauvegarde contient le fichier **tel qu'il était avant cette exécution** ; les
sauvegardes ultérieures peuvent donc contenir un fichier déjà patché. Pour
restaurer, fermer le jeu et remplacer `resources.assets` par la sauvegarde de
l'exécution souhaitée. Le script contrôle la taille de l'asset et refuse une
sortie anormalement petite. Sous Windows, il refuse aussi d'agir si
`GunmanContracts.exe` est détecté ; si ce contrôle est impossible, il demande
de vérifier manuellement que le jeu est fermé.
