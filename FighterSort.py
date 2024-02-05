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
import random
import string
import json

# Config is initialized in general.py

model_files = ["model.numatb", "model.numdlb", "model.numshb", "model.nusktb"]

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

def model_path_contains_mod(mod_model_dir):
    for mf in model_files:
        if path.isfile(path.join(mod_model_dir, mf)):
            return True
    return False

def main(argv):
    global char_folder
    global fighter_hashes
    char_folders = ""
    ui_only = False
    for arg in argv:
        if arg in ["-h", "--help"]:
            print("usage: python FighterSort.py <character folder>\nadd -u for ui-only (only change msg_name, do not sort+copy mods)")
            sys.exit()
        elif arg in ["-u", "--ui-only"]:
            ui_only = True
        elif arg in ["-c", "--credits"]:
            print("Fighter Sort v0.9")
            print("\nCreated by Mode8fx")
            print("https://github.com/Mode8fx/FighterSort")
            print("\nOther Resources Used:")
            print("\nreslotter.py")
            print("Original code by BluJay and Jozz")
            print("Modified by Coolsonickirby to add support for dir addition for ReslotterGUI")
            print("Further modified by Mode8fx for automation/integration with FighterSort")
            print("\nReslotterGUI")
            print("Original code by Coolsonickirby")
            print("Modified by Mode8fx for automation/integration with FighterSort")
            print("\ndir_info_with_files_trimmed.json")
            print("Original file by Coolsonickirby")
            print("\nHashes.txt")
            print("Original file by Smash Ultimate Research Group")
        else:
            char_folders = arg.replace("/", "\\")
    if char_folders == "":
        messagebox.showinfo(root.title(), "Select the folder containing your mods for a specific character. This folder should be named [Character], followed by the name of your character.\n\nExample: \"[Character] Toon Link\"\n\nYou can also select a parent folder containing multiple character folders.")
        char_folders = filedialog.askdirectory(title="Character's Mod Directory")
    if not path.isdir(char_folders):
        quit_with_error("Invalid character folder.")
    fighter_hashes = {}
    if "[Character] " in char_folders:
        char_folders = [char_folders]
    else:
        char_folders = [path.join(char_folders, folder) for folder in listdir(char_folders) if path.isdir(path.join(char_folders, folder)) and folder.startswith("[Character] ")]
        sort_all = messagebox.askyesno(root.title(), f"The selected folder contains {len(char_folders)} character folder{"" if len(char_folders) == 1 else "s"}. Would you like to sort all of them?")
        if not sort_all:
            quit_with_error("Sorting cancelled.")
    skipped_mods = []
    warnings = []
    for char_folder in char_folders:
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
            print("Character folder must be named either \"CHARACTER_NAME\" or \"[Character] CHARACTER_NAME\"")
            continue
        if len(char_names) == 0:
            print(f"Invalid character: {char}. Skipping.")
            continue
        print(f"\nCharacter: {char.name} {char_names}")

        # Get character key (created from spreadsheet)
        mods_info = []
        mods_info_by_target_slot = {}
        key_csv = path.join(char_folder, "key.tsv")
        try:
            with open(key_csv) as file:
                mods_info_csv = csv.reader(file, delimiter="\t")
                next(mods_info_csv) # skip the header row
                for row in mods_info_csv:
                    if len(row) >= 9 and row[0] != "":
                        mods_info.append(row[:9])
        except:
            print_key_info_and_quit()
        new_ui_num = 0 # for setting the UI number of new characters/echo slots
        curr_new_ui_name = None
        # For each mod in csv...
        for i, row in enumerate(mods_info):
            # Get info about mod
            mod_name = row[0] # Mod Name
            curr_alt = row[1] # Default Slot
            curr_alt_str = f"c{int(curr_alt):02}"
            target_alt = row[4] # Final Slot
            if not (target_alt.isdigit() and int(target_alt) >= 0):
                continue
            target_alt_str = f"c{int(target_alt):02}"
            simple_config = row[5] == "TRUE" # Can use simple config
            need_model_copy = (not simple_config) and int(curr_alt) <= 7 # and int(target_alt) <= 7 # If True, then missing model files need to be copied from share slot
            is_extra_slot = int(target_alt) > 7
            need_share = (not simple_config) and is_extra_slot
            new_char_name = row[6] # Slot Name (may be empty)
            is_new_slot = (row[8] in ["New Character", "Echo Slot"]) # Does character have their own CSS slot?
            print(f"\nMod #{i+1}: {mod_name}")
            print(f"{curr_alt_str} -> {target_alt_str}")
            # Get mod directory
            mod_folder, mod_folder_name = get_mod_folder_of_name(char.name, mod_name)
            if mod_folder is None or (not path.isdir(mod_folder)):
                print("Missing mod folder. Skipping.")
                skipped_mods.append(f"{mod_name}")
                continue
            # Set output directory
            output_dir = path.join(root_output_dir, f"{mod_folder_name} ({target_alt_str})")
            # Store output directory (used for checking for unexpected slot dependencies)
            if mods_info_by_target_slot.get(target_alt_str) is None:
                mods_info_by_target_slot[target_alt_str] = []
            mods_info_by_target_slot[target_alt_str].append((mod_name, output_dir))
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
                if need_model_copy:
                    # only use the first char_id since reslotterGUI already handles characters with multiple IDs
                    suffix = "-" + (''.join(random.choices(string.ascii_lowercase, k=8)))
                    reslotterGUI.run_with_func([curr_alt_str], [curr_alt_str], char_names[0], mod_folder, output_dir+suffix, share=need_share, new_ui_name=new_ui, new_ui_num=new_ui_num, replace=False)
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
                                assert sub_path_split[-1] in model_files
                                # assert sub_path_split[-1] != ""
                            except:
                                continue
                            # new_sub_path = sub_path.replace(curr_alt_str, target_alt_str)
                            new_sub_path = sub_path
                            new_model_path = path.join(output_dir+suffix, new_sub_path)
                            new_model_dir = path.dirname(new_model_path)
                            old_model_path = path.join(mod_folder, sub_path)
                            old_model_dir = path.dirname(old_model_path) # to get around some model-related issues for new slots, copy the needed model files to the output BEFORE reslotting
                            if (not path.isfile(new_model_path)) and ((new_sub_path in fighter_hashes[name]) or is_extra_slot) and path.isdir(old_model_dir): # and model_path_contains_mod(old_model_dir)
                                original_model_path = path.join(arc_export_dir, sub_path)
                                os.makedirs(new_model_dir, exist_ok=True)
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
                            # new_sub_path = sub_path.replace(curr_alt_str, target_alt_str)
                            new_sub_path = sub_path
                            new_model_path = path.join(output_dir+suffix, new_sub_path)
                            new_model_dir = path.dirname(new_model_path)
                            if (not path.isfile(new_model_path)):
                                original_model_path = path.join(arc_export_dir, sub_path)
                                os.makedirs(new_model_dir, exist_ok=True)
                                shutil.copy(original_model_path, new_model_path)
                                num_copied += 1
                        if num_copied > old_num_copied:
                            print(f"Copied missing ptrainer_low from original {curr_alt_str}")
                    # run reslotter a second time; once to prepare for model copying, and once to actually reslot
                    reslotterGUI.run_with_func([curr_alt_str], [target_alt_str], char_names[0], output_dir+suffix, output_dir, share=need_share, new_ui_name=new_ui, new_ui_num=new_ui_num, replace=True)
                else:
                    reslotterGUI.run_with_func([curr_alt_str], [target_alt_str], char_names[0], mod_folder, output_dir, share=need_share, new_ui_name=new_ui, new_ui_num=new_ui_num, replace=False)
            original_plugin_path = path.join(mod_folder, "plugin.nro")
            if path.isfile(original_plugin_path):
                new_plugin_path = path.join(output_dir, "plugin.nro")
                shutil.copy(original_plugin_path, new_plugin_path)
                print(f"Copied plugin.nro from original {curr_alt_str}")
            # Check for unexpected slot dependencies
            if need_share:
                unexpected_dependencies = set()
                assumed_share_slot = f"c{reslotterGUI.GetAssumedShareSlot(int(curr_alt), char_names[0]):02}"
                config_json_path = path.join(output_dir, "config.json")
                if path.isfile(config_json_path):
                    with open(config_json_path, "r") as config_json_file:
                        config_json = json.load(config_json_file)
                        config_share_to_vanilla = config_json.get("share-to-vanilla")
                        if config_share_to_vanilla is not None:
                            # possible_slots represents all slots that COULD be an unexpected dependency
                            possible_slots = ["c00", "c01", "c02", "c03", "c04", "c05", "c06", "c07"]
                            if assumed_share_slot in possible_slots:
                                possible_slots.remove(assumed_share_slot)
                            possible_slots = list(set(possible_slots) & set(["c0"+r[4] for r in mods_info]))
                            possible_slots.sort()
                            for key in config_share_to_vanilla:
                                for slot in possible_slots:
                                    if f"/{slot}/" in key:
                                        # unexpected_dependencies.add(slot)
                                        # now we know that this mod may contain an unexpected dependency; we need to check the mod(s) in the other slot to see if they contain the specific files that this mod is dependent on
                                        for other_mod in mods_info_by_target_slot[slot]:
                                            other_output_dir = other_mod[1]
                                            if path.isfile(path.join(other_output_dir, key)):
                                                unexpected_dependencies.add(slot)
                                                break
                if len(unexpected_dependencies) > 0:
                    print(f"WARNING: This mod, when used as an extra slot, is also dependent on {", ".join(list(unexpected_dependencies))}.")
                    if len(unexpected_dependencies) > 1:
                        print("    The mods you have in those slots conflict, so this mod may not work right.")
                    else:
                        print("    The mod you have in that slot conflicts, so this mod may not work right.")
                    warnings.append((char.name, mod_name, target_alt_str, unexpected_dependencies))
        if char.name == "Pokemon Trainer":
            oneslotnamer.run_with_func("ptrainer", 38, True, mods_info, char_folder)
            oneslotnamer.run_with_func("pzenigame", 39, False, mods_info, char_folder)
            oneslotnamer.run_with_func("pfushigisou", 40, False, mods_info, char_folder)
            oneslotnamer.run_with_func("plizardon", 41, False, mods_info, char_folder)
            # ui_index_string = "38 (Pokemon Trainer), 39 (Squirtle), 40 (Ivysaur), and 41 (Charizard)"
        elif char.name == "Pyra and Mythra":
            oneslotnamer.run_with_func("element", 114, False, mods_info, char_folder)
            oneslotnamer.run_with_func("eflame_first", 115, False, mods_info, char_folder)
            oneslotnamer.run_with_func("elight_first", 116, False, mods_info, char_folder)
            oneslotnamer.run_with_func("eflame_only", 117, False, mods_info, char_folder)
            oneslotnamer.run_with_func("elight_only", 118, False, mods_info, char_folder)
            # ui_index_string = "114 (Pyra and Mythra), 115 (Pyra), 116 (Mythra), 117 (Pyra only), and 118 (Mythra only)"
        else:
            oneslotnamer.run_with_func(char.ui_name, char.ui_index, char.has_article, mods_info, char_folder)
            # ui_index_string = f"{char.ui_index} ({char.ui_name})"

    print("\n\nSorting complete.")
    if len(warnings) > 0:
        print("\nWarnings:")
        for warning in warnings:
            warning_list = ", ".join(list(warning[3]))
            print(f"{warning[0]}: Mod in {warning[2]} ({warning[1]}) has dependencies which conflict with the mod(s) in {warning_list}")
            print(f"    Recommendation: Don't put a mod in {warning_list}")
    if len(skipped_mods) > 0:
        print("\nSkipped mods:")
        for mod in skipped_mods:
            print(mod)
        print("")
    getpass("\nPress Enter to exit.")

if __name__ == "__main__":
	main(sys.argv[1:])