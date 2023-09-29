from os import path
import sys
import csv
import getopt
from getpass import getpass
import xml.etree.ElementTree as ET
from xml.dom import minidom
from general import *

# TODO: ui_names[0] is a lazy fix and doesn't work for Pokemon Trainer or Pyra/Mythra
# TODO [never mind - can't be automated at this time]: Handle new CSS slots

curr_char = None

def quit_with_error(err):
    print(err)
    if verbose: getpass("Press Enter to exit.")
    sys.exit()

def save_xml(root, file_name, encoding):
    xml_str = ET.tostring(root, encoding=encoding)
    xml_parsed = minidom.parseString(xml_str)
    pretty_xml_str = xml_parsed.toprettyxml(indent="  ", encoding=encoding)
    with open(file_name, "wb") as file:
        file.write(pretty_xml_str)

def run_with_cmd(argv):
    global verbose
    global ui_name
    global key_csv
    verbose = False
    ui_name = None
    key_csv = None
    opts, args = getopt.getopt(argv,"hvc:k:",["char=", "key="])
    for opt, arg in opts:
        if opt == "-h":
            print("usage: python oneslotnamer.py --char <character id> --key <key.csv>")
            sys.exit()
        elif opt == "-v":
            verbose = True
        elif opt in ("-c", "--char"):
            ui_name = arg
        elif opt in ("-k", "--key"):
            key_csv = arg
    try:
        if ui_name is None:
            ui_name = args[0]
        if key_csv is None:
            key_csv = args[1]
    except:
        pass
    result = verify_and_run()
    return result

def run_with_func(_ui_name, _key_csv, _verbose=False):
    global verbose
    global ui_name
    global key_csv
    verbose = _verbose
    ui_name = _ui_name
    key_csv = _key_csv
    result = verify_and_run()
    return result

def verify_and_run():
    global curr_char
    for c in chars:
        if ui_name in c.ui_names:
            curr_char = c
            break
    try:
        assert curr_char is not None
    except:
        quit_with_error("Invalid character name.")
    try:
        assert path.isfile(key_csv)
    except:
        quit_with_error("Invalid key.csv")

    name_slots()
    return True

def split_title(title, max_len=19):
    lines = []
    words = title.split()
    curr_line = ""
    for word in words:
        if len(curr_line) + len(word) < max_len: # not <= since space also needs to be added
            if curr_line:
                curr_line += " "
            curr_line += word
        else:
            if curr_line:
                lines.append(curr_line)
            curr_line = word
    if curr_line:
        lines.append(curr_line)
    return "\n".join(lines)

def create_elem(parent, tag, key, val, elem_text=None):
    global xmsbt_new_root
    global curr_elem

    if parent is None:
        curr_elem = ET.Element(tag)
    else:
        curr_elem = ET.SubElement(parent, tag)
    if tag == "text":
        curr_elem.text = val
    else:
        curr_elem.set(key, val)
    if elem_text is not None:
        curr_elem.text = elem_text
    return curr_elem

def create_text_elem(val):
    global curr_elem

    curr_elem = ET.SubElement(curr_elem, "text")
    curr_elem.text = val
    return curr_elem

def make_pretty(root, tag):
    attributes = root.attrib
    root_pretty = root
    try:
        sorted_subelements = sorted(root_pretty, key=lambda element: int(element.get(tag)))
    except:
        sorted_subelements = sorted(root_pretty, key=lambda element: element.get(tag))
    root_pretty.clear()
    root.attrib = attributes
    for subelement in sorted_subelements:
        root_pretty.append(subelement)
    return root_pretty

def label_sort(entry):
    parts = entry.get("label").replace("stage_name", "stagename").split("_")
    if len(parts) == 5:
        parts = parts[:3] + ["".join(parts[3:])]
    return (parts[3], parts[2], parts[1])



def name_slots():
    global xmsbt_new_root
    global curr_elem

    # Parse msg_name.xmsbt
    xmsbt_tree = ET.parse(msg_name_xmsbt)
    xmsbt_root = xmsbt_tree.getroot()
    # Parse ui_chara_db.prcxml
    prcxml_tree = ET.parse(ui_chara_db_prcxml)
    prcxml_root = prcxml_tree.getroot()
    # Get character key (created from spreadsheet)
    mods_info = []
    try:
        with open(path.join(key_csv)) as file:
            mods_info_csv = csv.reader(file, delimiter="\t")
            for row in mods_info_csv:
                mods_info.append(row)
    except:
        quit_with_error("Please create key.csv from the Excel document (all 10 columns) and put it in the same directory as this script.")
    # Prepare xmsbt element
    xmsbt_new_root = ET.Element("xmsbt")
    # Prepare prcxml element
    prcxml_new_struct = create_elem(None, "struct", "index", str(curr_char.ui_index))
    # Number of colors
    prcxml_color_num_elem = ET.SubElement(curr_elem, "byte")
    prcxml_color_num_elem.set("hash", "color_num")
    prcxml_color_num_elem.text = "8"
    # For each mod in csv...
    # TODO: handle trainer and pyra/mythra
    for i, row in enumerate(mods_info):
        # Get info about mod
        if row[4] == "X":
            continue
        slot = int(row[4]) # Final Slot
        name = row[7] # Slot Name (may be empty, meaning default)
        title = row[8] # Boxing Ring Title (may be empty, meaning default)
        is_new_slot = (row[9] in ["New Character", "Echo Slot"]) # Does character have their own CSS slot
        # Update xmsbt
        if name != "":
            create_elem(xmsbt_new_root, "entry", "label", f"nam_chr1_{slot:02}_{curr_char.ui_names[0]}")
            create_text_elem(name)
            create_elem(xmsbt_new_root, "entry", "label", f"nam_chr2_{slot:02}_{curr_char.ui_names[0]}")
            create_text_elem(name.upper())
        if title != "":
            create_elem(xmsbt_new_root, "entry", "label", f"nam_stage_name_{slot:02}_{curr_char.ui_names[0]}")
            create_text_elem(split_title(title))
        # CSS slot name + number of slots
        if is_new_slot:
            create_elem(xmsbt_new_root, "entry", "label", f"nam_chr3_00_{name}")
            create_text_elem(name.upper())
        else:
            prcxml_color_num_elem.text = str(max(int(prcxml_color_num_elem.text), slot + 1))
        # Update prcxml
        if name != "":
            create_elem(prcxml_new_struct, "byte", "hash", f"n{slot:02}_index", elem_text=str(slot))
            new_ui_name = name.lower().replace(' ', '_').replace('&', 'and').replace('_and_', '_')
            create_elem(prcxml_new_struct, "hash40", "hash", f"characall_label_c{slot:02}", elem_text=f"vc_narration_characall_{new_ui_name}")
            if curr_char.has_article:
                create_elem(prcxml_new_struct, "hash40", "hash", f"characall_label_article_c{slot:02}", elem_text=f"vc_narration_characall_{new_ui_name}_article")
    # Finalize files
    # Edit msg_name.xmsbt
    for entry in xmsbt_new_root.findall("entry"):
        xmsbt_existing_entry = xmsbt_root.find(".//entry[@label='" + entry.get("label") + "']")
        if xmsbt_existing_entry is not None:
            xmsbt_root.remove(xmsbt_existing_entry)
        xmsbt_root.insert(0, entry)
    make_pretty(xmsbt_root, "label")
    sorted_entries = sorted(xmsbt_root.findall(".//entry"), key=label_sort)
    xmsbt_root.clear()
    for entry in sorted_entries:
        xmsbt_root.append(entry)
    ET.indent(xmsbt_tree, "  ")
    xmsbt_tree.write(msg_name_xmsbt, encoding="utf-16", xml_declaration=True)
    # Edit ui_chara_db
    prcxml_list_element = prcxml_root.find(".//list[@hash='db_root']")
    prcxml_existing_struct = prcxml_root.find(f".//struct[@index='{curr_char.ui_index}']")
    if prcxml_existing_struct is not None:
        prcxml_list_element.remove(prcxml_existing_struct)
    prcxml_list_element.insert(0, prcxml_new_struct)
    make_pretty(prcxml_list_element, "index")
    ET.indent(prcxml_tree, "  ")
    prcxml_tree.write(ui_chara_db_prcxml, encoding="utf-8", xml_declaration=True)

if __name__ == "__main__":
    run_with_cmd(sys.argv[1:])
    if verbose: getpass("\nPress Enter to exit.")