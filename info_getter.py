# Run this script from a character directory to generate part of a character page for the spreadsheet.

import os
import re
from getpass import getpass

# Directory containing the mod directories
directory = os.getcwd()
output = []
f = open("output.txt", "w")

# Function to extract slot values from a slot string
def extract_slot_values(slot_string):
    slot_values = []
    slot_string = "c"+slot_string.strip('[]')

    if '-' in slot_string:
        slot_values = [val for val in range(int(slot_string[1:3]), int(slot_string[5:7]) + 1)]
    else:
        slot_values = [int(val[1:3]) for val in slot_string.split(",")]

    return slot_values

# Iterate over each file in the directory
for dir_name in os.listdir(directory):
    mod_path = os.path.join(directory, dir_name)

    if os.path.isdir(mod_path):
        # Extract the mod name from the file name
        try:
            mod_name = re.search(r'\](.*?)\[c', dir_name).group(1).strip().replace("[Echo Slot] ", "").replace("[New Character] ", "")
            # Extract the slot string from the mod name
            slot_string = re.search(r'\[c(.*?)\]', dir_name).group(1)
            # Extract the slot values from the slot string
            slot_values = extract_slot_values(slot_string)
            # Check if the mod contains a "sound" folder
            voice = "TRUE" if "sound" in os.listdir(mod_path) else "FALSE"
            # Check if the mod contains a "stream" folder
            victory = "TRUE" if "stream;" in os.listdir(mod_path) else "FALSE"
        except:
            continue

        # Print the values for each slot value
        for i, slot in enumerate(slot_values):
            if len(slot_values) > 1:
                slot_name = mod_name + ' ' + str(i+1)
            else:
                slot_name = mod_name
            output.append(f'{slot_name}\t{slot}\t{voice}\t{victory}')
            f.write(f'{slot_name}\t{slot}\t{voice}\t{victory}\n')

if len(output) == 0:
    print("No mods found in the current directory.")
else:
    for line in output:
        print(line)
    print("\nOutput written to output.txt.")
    print("Copy the contents of output.txt (not the above output!) into your character's page on the spreadsheet.")

# f.close()
getpass("\nPress Enter to exit.")