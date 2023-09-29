# FighterSort

**[WORK IN PROGRESS]**

FighterSort aims to be a quick and easy way to batch organize character mods for Super Smash Bros. Ultimate. It is intended for users who have a very large number of mods (hundreds).

## How Does It Work?

Using a combination of Coolsonickirby's [ReslotterGUI](https://github.com/CSharpM7/reslotter), a spreadsheet that keeps track of your mod info, and your own [ArcExplorer](https://github.com/ScanMountGoat/ArcExplorer) export, FighterSort organizes all of your mods for a character, all at once, how you want them to be organized, ready to drag and drop onto your SD card. The output is in a new folder, so the original mods are unchanged. There's a decent amount of initial setup, but it's well worth it if you have a lot of mods since almost everything after this initial setup is automated for you. For more info, see the tutorial below.

### What It Can Do

- Change the slots of all your mods
- Export specific slots from a multi-slot mod (e.g. if a mod has 8 slots but you only want 3 of them)
- Handle extra slots above c07
- Fix normally-incompatible swaps (e.g. putting a female Inkling mod on a male Inkling slot) by copying the necessary model files from an ArcExplorer export
- (Re)generate config.json for each mod
- Edit msg_name.xmsbt to add a custom name and/or Boxing Ring title for each mod
- Edit ui_chara_db.prcxml to change the character's number of slots
- Handle all characters including Ice Climbers, Pokemon Trainer, and Pyra/Mythra (actually, Pyra/Mythra are still a work in progress)

### What It Can't Do (for now)

- Add new CSS character slots
- Add single-slot victory themes
- Add single-slot announcer calls

### What It Will Never Do
- Anything that doesn't involve characters (stages, etc.)

## Tutorial

First, organize your mods for each character. The directory names are important, as that is how the sorter will know what the mods are. Follow this structure:
```
/[Character] CHARACTER_NAME
    /[CHARACTER_NAME] MOD_NAME [THE ORIGINAL SLOT(S) AS IT WAS RELEASED]
        /fighter
        /ui
        ...
    ...
    key.csv
```
Here's an example for Captain Falcon:
```
/[Character] Captain Falcon
    /[Captain Falcon] Afro Falcon [c05]
        /fighter
        /ui
        ...
    /[Captain Falcon] Blaziken [c00-c07]
        /fighter
        /ui
        ...
    /[Captain Falcon] Retro Captain Falcon [c01,c03,c05,c07]
        /fighter
        /ui
        ...
    key.csv
```

Next, you may have noticed `key.csv`. Open the provided Google Sheets document and go to the sheet that matches your character. Fill in the info for your mod (columns F and G are determined by the other columns' values, H and I are optional, and J should be either "Echo Slot" or "New Character" if either of those is true). Finally, select columns A-J (excluding header) and copy+paste them into a file named `key.csv`. Save this CSV file in the same directory as your mods for the character in question, as shown above.

Now, open a command line window and navigate to the directory that contains FighterSort. Run `FighterSort.exe "CHARACTER_DIR"` (quotes included), where CHARACTER_DIR is your character mod directory (e.g. `C:/Smash Mods/[Character] Captain Falcon`). If this is your first time using FighterSort, it will ask you to select the directory of your ArcExplorer export.

Just wait a few seconds, and copy the contents of the new `output` directory to your SD card's mod directory. Also, copy the `CSS` folder to your mod directory; this contains `msg_name.xmsbt` and `ui_chara_db.prcxml`, which will both be altered every time you sort a new mod. And that's it!

## Credits
The following resources were originally made by other people:

#### reslotter.py
- Original code by [BluJay](https://github.com/blu-dev) and [Jozz](https://github.com/jozz024/ssbu-skin-reslotter)
- Modified by [Coolsonickirby](https://github.com/CSharpM7/reslotter) to add support for dir addition for ReslotterGUI
- Further modified by Mips96 for automation/integration with FighterSort

#### reslotterGUI.py
- Original code by [Coolsonickirby](https://github.com/CSharpM7/reslotter)
- Modified by Mips96 for automation/integration with FighterSort

#### dir_info_with_files_trimmed.json
- Original file by [Coolsonickirby](https://github.com/CSharpM7/reslotter)

#### Hashes.txt
- Original file by [Smash Ultimate Research Group](https://github.com/ultimate-research/archive-hashes)
