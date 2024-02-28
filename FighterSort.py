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
from datetime import datetime

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

def copy_file_generic(mod_folder, output_dir, file):
    original_path = path.join(mod_folder, file)
    if path.isfile(original_path):
        new_path = path.join(output_dir, file)
        os.makedirs(path.dirname(new_path), exist_ok=True)
        shutil.copy(original_path, new_path)
        print(f"Copied {file}")

def copy_other_files(mod_folder, output_dir, char_names, target_alt_str):
    original_effect_path = path.join(mod_folder, "effect", "fighter", char_names[0], f"ef_{char_names[0]}.eff")
    if path.isfile(original_effect_path):
        new_effect_path = path.join(output_dir, "effect", "fighter", char_names[0], f"ef_{char_names[0]}_{target_alt_str}.eff")
        if not path.isfile(new_effect_path):
            os.makedirs(path.dirname(new_effect_path), exist_ok=True)
            shutil.copy(original_effect_path, new_effect_path)
            print(f"Copied ef_{char_names[0]}.eff from original {target_alt_str} and made it one-slot")
    copy_file_generic(mod_folder, output_dir, "plugin.nro")
    copy_file_generic(mod_folder, output_dir, "config_param.toml")

def debug_wait(string=""):
    if debug_mode:
        getpass(f"Wait! - {string}")

def main(argv):
    global char_folder
    global fighter_hashes
    global debug_mode
    char_folders = ""
    ui_only = False
    force_extra = False
    forced_target_slot = -1
    force_vanilla = False
    force_no_echo = False
    debug_mode = False
    copy_all_vanilla_files = False
    copy_no_vanilla_files = False
    for arg in argv:
        if arg in ["-h", "--help"]:
            print(
"""usage: python FighterSort.py <character folder>

-u: ui-only (only change msg_name and ui_chara_db, do not sort+copy mods)
-e: force extra slots (ignore the target slots in the key file and put enabled mods in slot c08, c09, c10, ...)
-v: vanilla slots only (ignore any slots above c07)
-nc: no new characters (ignore mods that use new CSS slots)

--copy-all: copy all mode (copy ALL vanilla files from the original slot, not just models)
--copy-none: copy none mode (no vanilla files will be copied from the original slot)
--debug: debug mode (print debug strings and pause at certain points)
-c: view credits"""
            )
            sys.exit()
        elif arg in ["-u", "--ui-only"]:
            ui_only = True
            print("- UI only mode enabled. Mods will not be sorted or copied, and only msg_name and ui_chara_db will be created/modified.")
        elif arg in ["-e", "--force-extra", "--extra-only"]:
            force_extra = True
            print("- Extra slots forced. The target slots from each character's key.tsv will be ignored, and mods will be put in extra slots. Disabled mods are still ignored.")
        elif arg in ["-v", "--force-vanilla", "--vanilla-only"]:
            force_vanilla = True
            print("- Vanilla slots only. Any mods with target slots above c07 will be ignored.")
        elif arg in ["-nc", "--no-char"]:
            force_no_echo = True
            print("- No new characters forced. Mods that use new CSS slots (i.e. are marked as \"New Character\" or \"Echo Slot\") will be ignored.")
        elif arg in ["--debug"]:
            debug_mode = True
            print("- Debug mode enabled. This will pause the sorter at certain points and wait for the user to press Enter before continuing.")
        elif arg in ["--copy-all"]:
            copy_all_vanilla_files = True
            print("- Copy all enabled. When model copying is needed, this will copy ALL vanilla files from the original slot, not just models.")
        elif arg in ["--copy-none"]:
            copy_no_vanilla_files = True
            print("- Copy none enabled. No vanilla files will be copied from the original slot.")
        elif arg in ["-c", "--credits"]:
            print(
"""Fighter Sort v0.94

Created by Mode8fx
https://github.com/Mode8fx/FighterSort

Other Resources Used:

reslotter.py
Original code by BluJay and Jozz
Modified by Coolsonickirby to add support for dir addition for ReslotterGUI
Further modified by Mode8fx for automation/integration with FighterSort

ReslotterGUI
Original code by Coolsonickirby
Modified by Mode8fx for automation/integration with FighterSort

dir_info_with_files_trimmed.json
Original file by Coolsonickirby

Hashes.txt
Original file by Smash Ultimate Research Group"""
            )
            sys.exit()
        else:
            char_folders = arg.replace("/", "\\")
    if force_extra and force_vanilla:
        quit_with_error("Cannot have both -e and -v flags enabled at the same time.")
    if copy_all_vanilla_files and copy_no_vanilla_files:
        quit_with_error("Cannot have both --copy-all and --copy-none flags enabled at the same time.")
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
        if force_extra:
            forced_target_slot = 8

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
                        if force_vanilla and row[4].isdigit() and int(row[4]) > 7:
                            continue
                        if force_no_echo and row[8] in ["New Character", "Echo Slot"]:
                            continue
                        if not (row[4].isdigit() and int(row[4]) >= 0):
                            continue
                        if force_extra and not (row[8] in ["New Character", "Echo Slot"]):
                            row[4] = str(forced_target_slot)
                            forced_target_slot += 1
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
            target_alt_str = f"c{int(target_alt):02}"
            is_extra_slot = int(target_alt) > 7
            simple_config = (row[5] == "TRUE") and not is_extra_slot # Can use simple config
            need_model_copy = (not simple_config) and (int(curr_alt) <= 7) and (not copy_no_vanilla_files) # and int(target_alt) <= 7 # If True, then missing model files need to be copied from share slot
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
                    # Only use the first char_id since reslotterGUI already handles characters with multiple IDs
                    suffix = "-" + (''.join(random.choices(string.ascii_lowercase, k=8)))
                    debug_wait("Before first reslot")
                    reslotterGUI.run_with_func([curr_alt_str], [curr_alt_str], char_names[0], mod_folder, output_dir+suffix, share=need_share, new_ui_name=new_ui, new_ui_num=new_ui_num, replace=False)
                    debug_wait("Before model copy")
                    if not fighter_hashes:
                        populate_fighter_hashes()
                    for name in char_names:
                        if fighter_hashes.get(name) is None:
                            continue
                        num_copied = 0
                        for sub_path in fighter_hashes[name]:
                            try:
                                sub_path_split = sub_path.split("/")
                                if copy_all_vanilla_files:
                                    assert curr_alt_str in sub_path_split
                                else:
                                    assert sub_path_split[-2] == curr_alt_str
                                    assert sub_path_split[-1] in model_files
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
                            if copy_all_vanilla_files:
                                print(f"Copied {num_copied} missing file{'s' if num_copied > 1 else ''} from original {curr_alt_str}")
                            else:
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
                            old_model_path = path.join(mod_folder, sub_path)
                            old_model_dir = path.dirname(old_model_path)
                            if (not path.isfile(new_model_path)) and ((new_sub_path in fighter_hashes[name]) or is_extra_slot) and path.isdir(old_model_dir):
                                original_model_path = path.join(arc_export_dir, sub_path)
                                os.makedirs(new_model_dir, exist_ok=True)
                                shutil.copy(original_model_path, new_model_path)
                                num_copied += 1
                        if num_copied > old_num_copied:
                            print(f"Copied missing ptrainer_low from original {curr_alt_str}")
                    # Ropy all-slots effect (one-slot is already handled) and plugin.nro
                    copy_other_files(output_dir+suffix, output_dir, char_names, target_alt_str)
                    # Run reslotter a second time; once to prepare for model copying, and once to actually reslot
                    debug_wait("Before second reslot")
                    reslotterGUI.run_with_func([curr_alt_str], [target_alt_str], char_names[0], output_dir+suffix, output_dir, share=need_share, new_ui_name=new_ui, new_ui_num=new_ui_num, replace=True)
                else:
                    # Copy all-slots effect (one-slot is already handled) and plugin.nro
                    copy_other_files(mod_folder, output_dir, char_names, target_alt_str)
                    debug_wait("Before reslot")
                    reslotterGUI.run_with_func([curr_alt_str], [target_alt_str], char_names[0], mod_folder, output_dir, share=need_share, new_ui_name=new_ui, new_ui_num=new_ui_num, replace=False)
                    debug_wait("After reslot")
                # Check for unexpected slot dependencies (situations where a mod's config pulls file(s) from slots other than the one it's sharing from)
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
                                            # Now we know that this mod may contain an unexpected dependency; we need to check the mod(s) in the other slot to see if they contain the specific files that this mod is dependent on
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
        # Now generate msg_name.xmsbt and update ui_chara_db.prcxml (or generate it if it doesn't already exist)
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
    log_file = None
    if len(warnings) + len(skipped_mods) > 0:
        log_file = path.join(path.dirname(sys.executable), "Logs", f"FighterSort_Log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.txt")
        os.makedirs(path.dirname(log_file), exist_ok=True)
        with open(log_file, "w") as log:
            pass
    if len(warnings) > 0:
        print("\nWarnings:")
        with open(log_file, "a") as log:
            log.write("Warnings:\n")
        for warning in warnings:
            warning_list = ", ".join(list(warning[3]))
            print(f"{warning[0]}: Mod in {warning[2]} ({warning[1]}) has dependencies which conflict with the mod(s) in {warning_list}")
            print(f"    Recommendation: Don't put a mod in {warning_list}")
            # append to log_file
            with open(log_file, "a") as log:
                log.write(f"{warning[0]}: Mod in {warning[2]} ({warning[1]}) has dependencies which conflict with the mod(s) in {warning_list}\n")
                log.write(f"    Recommendation: Don't put a mod in {warning_list}\n")
    if len(skipped_mods) > 0:
        print("\nSkipped mods:")
        with open(log_file, "a") as log:
            log.write("\nSkipped mods:\n")
        for mod in skipped_mods:
            print(mod)
            with open(log_file, "a") as log:
                log.write(f"{mod}\n")
        print("")
    print("")
    if log_file is not None:
        print(f"Warning log written to {log_file}.")
    getpass("Press Enter to exit.")

if __name__ == "__main__":
	main(sys.argv[1:])