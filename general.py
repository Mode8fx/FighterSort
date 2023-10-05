import os
from os import path
import sys
from getpass import getpass
import configparser
import tkinter as tk
from tkinter import messagebox, filedialog

###########
# General #
###########

directory = os.getcwd()

def quit_with_error(err):
	print(err)
	getpass("Press Enter to exit.")
	sys.exit()

def print_key_info_and_quit():
    print("Please create key.csv from the Excel document (all 10 columns) and put it in the character directory.")
    print("The Excel document can be found at the link below. Make a copy and edit it with info about your own mods.")
    print("PLACEHOLDER URL")
    quit_with_error("Fill out columns A-J (excluding F and G) manually, or run info_getter.py.")

##########
# Config #
##########

def set_config_path_var(path_name, temp_msg, temp_title, filetypes=None):
    global config
    try:
        assert path.exists(config["Paths"][path_name])
    except:
        messagebox.showinfo(root.title(), temp_msg)
        if filetypes is None:
            temp_input = filedialog.askdirectory(title=temp_title)
        else:
            temp_input = filedialog.askopenfilename(title=temp_title, filetypes=filetypes)
        if not (path.exists(temp_input)):
            quit_with_error(f"Invalid {temp_title}.")
        config["Paths"][path_name] = temp_input
        with open("sorter_config.ini", "w") as config_file:
            config.write(config_file)

root = tk.Tk()
root.title("Slot Sorter")
root.withdraw()
config = configparser.ConfigParser()
config.read("sorter_config.ini")
if "Paths" not in config:
    config["Paths"] = {}

path_name = "arc_export_dir"
temp_msg = "Select the directory that contains your ArcExplorer export.\n\nIt should contain the fighter directory, which is needed for swapping slots on certain mods (only fighter is needed).\n\nThis directory's path should be something like:\nC:/Smash Mods/ArcExplorer/export"
temp_title = "ArcExplorer export directory"
set_config_path_var(path_name, temp_msg, temp_title)

path_name = "msg_name_xmsbt"
temp_msg = "Select your msg_name.xmsbt file.\n\nThis file will be modified whenever a mod with a custom name or Boxing Ring title is sorted."
temp_title = "msg_name.xmsbt"
set_config_path_var(path_name, temp_msg, temp_title, filetypes=[("XMSBT Files", "*.xmsbt")])

path_name = "ui_chara_db_prcxml"
temp_msg = "Select your ui_chara_db.prcxml file.\n\nThis file will keep track of how many slots each fighter has."
temp_title = "ui_chara_db.prcxml"
set_config_path_var(path_name, temp_msg, temp_title, filetypes=[("PRCXML Files", "*.prcxml")])

arc_export_dir = config["Paths"]["arc_export_dir"]
msg_name_xmsbt = config["Paths"]["msg_name_xmsbt"]
ui_chara_db_prcxml = config["Paths"]["ui_chara_db_prcxml"]

##################
# Character Info #
##################

class Character:
    def __init__(self, name, fighter_names, ui_index, ui_name=None, has_article=False, alt_names=[]):
        self.name = name
        self.fighter_names = fighter_names
        if not isinstance(self.fighter_names, list):
            self.fighter_names = [self.fighter_names]
        self.ui_index = ui_index
        self.ui_name = ui_name
        if self.ui_name is None:
            self.ui_name = self.fighter_names[0]
        self.has_article = has_article
        self.alt_names = alt_names

def get_char_by_index(num):
    for char in chars:
        if char.ui_index == num:
            return char
    return None

chars = [
    Character("Mario", "mario", 1),
    Character("Donkey Kong", "donkey", 2),
    Character("Link", "link", 3),
    Character("Samus", "samus", 4),
    Character("Dark Samus", "samusd", 5, has_article=True),
    Character("Yoshi", "yoshi", 6),
    Character("Kirby", "kirby", 7),
    Character("Fox", "fox", 8),
    Character("Pikachu", "pikachu", 9),
    Character("Luigi", "luigi", 10),
    Character("Ness", "ness", 11),
    Character("Captain Falcon", "captain", 12),
    Character("Jigglypuff", "purin", 13),
    Character("Peach", "peach", 14),
    Character("Daisy", "daisy", 15),
    Character("Bowser", "koopa", 16),
    Character("Giga Bowser", "koopag", -1),
    Character("Ice Climbers", ["nana", "popo"], 17, ui_name="ice_climber", has_article=True),
    Character("Sheik", "sheik", 18),
    Character("Zelda", "zelda", 19),
    Character("Dr. Mario", "mariod", 20),
    Character("Pichu", "pichu", 21),
    Character("Falco", "falco", 22),
    Character("Marth", "marth", 23),
    Character("Lucina", "lucina", 24),
    Character("Young Link", "younglink", 25, has_article=True),
    Character("Ganondorf", "ganon", 26),
    Character("Mewtwo", "mewtwo", 27),
    Character("Roy", "roy", 28),
    Character("Chrom", "chrom", 29),
    Character("Mr.Game & Watch", "gamewatch", 30),
    Character("Meta Knight", "metaknight", 31),
    Character("Pit", "pit", 32),
    Character("Dark Pit", "pitb", 33, has_article=True),
    Character("Zero Suit Samus", "szerosuit", 34),
    Character("Wario", "wario", 35),
    Character("Snake", "snake", 36),
    Character("Ike", "ike", 37),
    # Character("Pokemon Trainer", ["ptrainer", "ptrainer_low", "pzenigame", "pfushigisou", "plizardon"], 38, has_article=True),
    Character("Pokemon Trainer", "ptrainer", 38),
    Character("Squitle", "pzenigame", 39),
    Character("Ivysaur", "pfushigisou", 40),
    Character("Charizard", "plizardon", 41),
    Character("Diddy Kong", "diddy", 42),
    Character("Lucas", "lucas", 43),
    Character("Sonic", "sonic", 44),
    Character("King Dedede", "dedede", 45, has_article=True),
    Character("Olimar", "pikmin", 46),
    Character("Lucario", "lucario", 47),
    Character("R.O.B.", "robot", 48),
    Character("Toon Link", "toonlink", 49),
    Character("Wolf", "wolf", 50),
    Character("Villager", "murabito", 51),
    Character("Mega Man", "rockman", 52),
    Character("Wii Fit Trainer", "wiifit", 53, has_article=True),
    Character("RosaLina and Luma", "rosetta", 54),
    Character("Little Mac", "littlemac", 55),
    Character("Greninja", "gekkouga", 56),
    Character("Palutena", "palutena", 57),
    Character("Pac-Man", "pacman", 58),
    Character("Robin", "reflet", 59),
    Character("Shulk", "shulk", 60),
    Character("Bowser Jr", "koopajr", 61),
    Character("Duck Hunt", "duckhunt", 62, has_article=True),
    Character("Ryu", "ryu", 63),
    Character("Ken", "ken", 64),
    Character("Cloud", "cloud", 65),
    Character("Corrin", "kamui", 66),
    Character("Bayonetta", "bayonetta", 67),
    Character("Richter", "richter", 68),
    Character("Inkling", "inkling", 69, has_article=True),
    Character("Ridley", "ridley", 70),
    Character("King K. Rool", "krool", 71, has_article=True),
    Character("Simon", "simon", 72),
    Character("Isabelle", "shizue", 73),
    Character("Incineroar", "gaogaen", 74),
    # Character("Mii", "mii", -1),
    Character("Mii Brawler", "miifighter", -1, has_article=True),
    Character("Mii Swordfighter", "miisword", -1, has_article=True),
    Character("Mii Gunner", "miigunner", -1, has_article=True),
    # Character("", 79),
    # Character("", 80),
    # Character("", 81),
    # Character("", 82),
    # Character("", 83),
    # Character("", 84),
    # Character("", 85),
    # Character("", 86),
    # Character("", 87),
    # Character("", 88),
    # Character("", 89),
    # Character("", 90),
    # Character("", 91),
    # Character("", 92),
    # Character("", 93),
    # Character("", 94),
    # Character("", 95),
    # Character("", 96),
    # Character("", 97),
    # Character("", 98),
    # Character("", 99),
    # Character("", 100),
    # Character("", 101),
    # Character("", 102),
    # Character("", 103),
    # Character("", 104),
    Character("Piranha Plant", "packun", 105, has_article=True),
    Character("Joker", "jack", 106),
    Character("Hero", "brave", 107, has_article=True),
    Character("Banjo & Kazooie", "buddy", 108),
    Character("Terry", "dolly", 109),
    Character("Byleth", "master", 110),
    Character("Min Min", "tantan", 111),
    Character("Steve", "pickel", 112),
    Character("Sephiroth", "edge", 113),
    # Character("Pyra and Mythra", ["eflame", "element", "elight"], 114, ui_name=["eflame_first", "eflame_only", "elight_first", "elight_only"]),
    Character("Pyra and Mythra", "element", 114),
    Character("Pyra", "eflame_first", 115, ui_name="eflame"),
    Character("Mythra", "elight_first", 116, ui_name="elight"),
    Character("Pyra", "eflame_only", 117, ui_name="eflame"),
    Character("Mythra", "elight_only", 118, ui_name="elight"),
    Character("Kazuya", "demon", 119),
    Character("Sora", "trail", 120)
]