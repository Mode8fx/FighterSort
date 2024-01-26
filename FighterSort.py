import os
from os import path, listdir
import shutil
import sys
import csv
import re
from getpass import getpass
import reslotterGUI
import oneslotnamer
from general import *

# Config is initialized in general.py

def get_mod_folder_of_name(char, mod_name):
    # Just the name
    for folder in listdir(char_folder):
        if path.basename(folder).startswith(f"[{char}] {mod_name} [c"):
            return path.join(char_folder, folder), f"[{char}] {mod_name}"
    # Remove the suffix number (and preceding space) from the mod name, if it exists
    match = re.search(r' \d+$', mod_name)
    if match is not None:
        mod_name = mod_name[:-len(match.group())]
    for folder in listdir(char_folder):
        if path.basename(folder).startswith(f"[{char}] {mod_name} [c"):
            return path.join(char_folder, folder), f"[{char}] {mod_name}"
    return None, None

def populate_fighter_hashes():
    global fighter_hashes
    with open("Hashes_models.txt", "r") as hash_file:
        for line in hash_file.readlines():
            line = line.strip()
            if line.startswith("fighter/"):
                try:
                    hash_char = line.split("/")[1]
                    if fighter_hashes.get(hash_char) is None:
                        fighter_hashes[hash_char] = []
                    fighter_hashes[hash_char].append(line)
                except:
                    continue

def main(argv):
    global char_folder
    global fighter_hashes
    char_folder = ""
    ui_only = False
    for arg in argv:
        if arg == "-h":
            print("usage: python FighterSort.py <character folder>\nadd -u for ui-only (only change msg_name, do not sort+copy mods)")
            sys.exit()
        elif arg == "-u":
            ui_only = True
        else:
            char_folder = arg.replace("/", "\\")
    if char_folder == "":
        print("usage: python FighterSort.py <character folder>\nadd -u for ui-only (only change msg_name, do not sort+copy mods)")
        sys.exit()
    if not path.isdir(char_folder):
        quit_with_error("Invalid character folder.")
    fighter_hashes = {}
    # Get current character + id
    char = None
    char_names = None
    dir_character_name = path.basename(char_folder).replace("[Character] ", "").lower()
    for c in chars:
        if dir_character_name == c.name.lower():
            char = c
            char_names = c.fighter_names
            break
    char_names = list(set(char_names))
    if char is None:
        quit_with_error("Character folder must be named either \"CHARACTER_NAME\" or \"[Character] CHARACTER_NAME\"")
    print(f"\nCharacter: {char.name} {char_names}")

    # Get character key (created from spreadsheet)
    mods_info = []
    key_csv = path.join(char_folder, "key.csv")
    try:
        with open(key_csv) as file:
            mods_info_csv = csv.reader(file, delimiter="\t")
            for row in mods_info_csv:
                assert len(row) >= 10
                mods_info.append(row)
    except:
        print_key_info_and_quit()
    output_dir_root = path.join(char_folder, "output")
    if not (path.isdir(output_dir_root) or ui_only):
        os.mkdir(output_dir_root)
    new_ui_num = 0 # for setting the UI number of new characters/echo slots
    curr_new_ui_name = None
    # For each mod in csv...
    for i, row in enumerate(mods_info):
        # Get info about mod
        mod_name = row[0] # Mod Name
        curr_alt = row[1] # Default Slot
        curr_alt_str = f"c{int(curr_alt):02}"
        target_alt = row[4] # Final Slot
        if target_alt == "X":
            continue
        target_alt_str = f"c{int(target_alt):02}"
        simple_config = row[5] == "TRUE" # Can use simple config
        need_model_copy = (not simple_config) # and int(target_alt) <= 7 # If True, then missing model files need to be copied from share slot
        is_extra_slot = int(target_alt) > 7
        need_share = (not simple_config) and is_extra_slot
        new_char_name = row[7] # Slot Name (may be empty)
        is_new_slot = (row[9] in ["New Character", "Echo Slot"]) # Does character have their own CSS slot?
        print(f"\nMod #{i+1}: {mod_name}")
        print(f"{curr_alt_str} -> {target_alt_str}")
        # Get mod directory
        mod_folder, mod_folder_name = get_mod_folder_of_name(char.name, mod_name)
        if not path.isdir(mod_folder):
            print("Missing mod folder. Skipping.")
            continue
        # Set output directory
        output_dir = path.join(output_dir_root, f"{mod_folder_name} ({target_alt_str})")
        # Reslot the desired mod
        if is_new_slot:
            new_ui = new_char_name.lower().replace(' ', '_').replace('&', 'and').replace('_and_', '_')
            if new_ui == curr_new_ui_name:
                new_ui_num += 1
            else:
                new_ui_num = 0
                curr_new_ui_name = new_ui
        else:
            new_ui = ""
        if not ui_only:
            reslotterGUI.run_with_func([curr_alt_str], [target_alt_str], char_names[0], mod_folder, output_dir, share=need_share, new_ui_name=new_ui, new_ui_num=new_ui_num) # only use the first char_id since reslotterGUI already handles characters with multiple IDs
            if need_model_copy:
                if not fighter_hashes:
                    populate_fighter_hashes()
                for name in char_names:
                    if fighter_hashes.get(name) is None:
                        continue
                    num_copied = 0
                    for sub_path in fighter_hashes[name]:
                        try:
                            sub_path_split = sub_path.split("/")
                            assert sub_path_split[-2] == curr_alt_str
                            assert sub_path_split[-1] in ["model.numatb", "model.numdlb", "model.numshb", "model.nusktb"]
                            # assert sub_path_split[-1] != ""
                        except:
                            continue
                        new_sub_path = sub_path.replace(curr_alt_str, target_alt_str)
                        new_model_path = path.join(output_dir, new_sub_path)
                        new_model_dir = path.dirname(new_model_path)
                        if (not path.isfile(new_model_path)) and (new_sub_path in fighter_hashes[name]) and path.isdir(new_model_dir):
                            original_model_path = path.join(arc_export_dir, sub_path)
                            # os.makedirs(new_model_dir, exist_ok=True)
                            shutil.copy(original_model_path, new_model_path)
                            num_copied += 1
                            # print(f"Copied: {new_model_path}")
                    if num_copied > 0:
                        print(f"Copied {num_copied} missing model file{'s' if num_copied > 1 else ''} from original {curr_alt_str}")
                if "ptrainer" in char_names:
                    old_num_copied = num_copied
                    for sub_path in fighter_hashes["ptrainer_low"]:
                        try:
                            sub_path_split = sub_path.split("/")
                            assert sub_path_split[-2] == curr_alt_str
                        except:
                            continue
                        new_sub_path = sub_path.replace(curr_alt_str, target_alt_str)
                        new_model_path = path.join(output_dir, new_sub_path)
                        new_model_dir = path.dirname(new_model_path)
                        if (not path.isfile(new_model_path)):
                            original_model_path = path.join(arc_export_dir, sub_path)
                            os.makedirs(new_model_dir, exist_ok=True)
                            shutil.copy(original_model_path, new_model_path)
                            num_copied += 1
                    if num_copied > old_num_copied:
                        print(f"Copied missing ptrainer_low from original {curr_alt_str}")
        original_plugin_path = path.join(mod_folder, "plugin.nro")
        if path.isfile(original_plugin_path):
            new_plugin_path = path.join(output_dir, "plugin.nro")
            shutil.copy(original_plugin_path, new_plugin_path)
            print(f"Copied plugin.nro from original {curr_alt_str}")
    if char.name == "Pokemon Trainer":
        oneslotnamer.run_with_func("ptrainer", 38, True, mods_info, char_folder)
        oneslotnamer.run_with_func("pzenigame", 39, False, mods_info, char_folder)
        oneslotnamer.run_with_func("pfushigisou", 40, False, mods_info, char_folder)
        oneslotnamer.run_with_func("plizardon", 41, False, mods_info, char_folder)
    elif char.name == "Pyra and Mythra":
        oneslotnamer.run_with_func("element", 114, False, mods_info, char_folder)
        oneslotnamer.run_with_func("eflame_first", 115, False, mods_info, char_folder)
        oneslotnamer.run_with_func("elight_first", 116, False, mods_info, char_folder)
        oneslotnamer.run_with_func("eflame_only", 117, False, mods_info, char_folder)
        oneslotnamer.run_with_func("elight_only", 118, False, mods_info, char_folder)
    else:
        oneslotnamer.run_with_func(char.ui_name, char.ui_index, char.has_article, mods_info, char_folder)

    print("\n\nSorting complete.")
    getpass("\nPress Enter to exit.")

if __name__ == "__main__":
	main(sys.argv[1:])