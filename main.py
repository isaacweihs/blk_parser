from pathlib import Path
import sys
import os
from tkinter import Tk, messagebox
from tkinter import filedialog as fd
from tkinter import simpledialog as sd
import time as t
import json

import package.parse as blk_parser

#-- init --#
root = Tk()
root.withdraw()

messagebox.showinfo(title="Proceed with Caution", message="This script will duplicate your War Thunder user mission and make it available for ALL tanks/planes/boats in the game.\n\nPlease make a backup of your .blk file(s) in case anything aborts the script or if errors occur. I am not responsible for corrupt files or incorrect usage of this script.\n\nVersion: release 2.1")

openfile = messagebox.askokcancel("Select file?", "Please select your .blk file")

if openfile == True:
    source = fd.askopenfile(title="File Selection", filetypes=[("War Thunder Block Files", "*.blk")])
    source_raw = Path(source.name)
    source.close()
else:
    sys.exit()

#-- open mission file --#
print("Initalizing mission...")
try: 
    source_raw.rename(source_raw.with_suffix(".txt"))
    source_txt = source.name.strip(".blk") + ".txt" 
except FileExistsError:
    messagebox.showerror(title="File Already Exists", message="A .txt file with the same name as the .blk file was found.\n\nPlease delete the .txt file and try again.")

with open(source_txt, "r") as mission:
    parsed_blk, parsed_blk_length = blk_parser.parse_blk_to_dict(''.join(mission))

NATIONS = {
    "cn": "CHINA",
    "fr": "FRANCE",
    "germ": "GERMANY",
    "il": "ISRAEL",
    "it": "ITALY",
    "jp": "JAPAN",
    "sw": "SWEDEN",
    "uk": "UNITED KINGDOM",
    "us": "USA",
    "ussr": "USSR_RUSSIA",
}

#-- obtain mission parameters --#
print("Obtaining mission parameters...")
loc_name = blk_parser.find_value_by_path(parsed_blk, ["mission_settings", "mission", "locName"])
wing = blk_parser.find_value_by_path(parsed_blk, ["mission_settings", "player", "wing"])

try:
    if blk_parser.find_element_by_value(parsed_blk, wing, "tankModels", path_is_index=True) != None:
        player_unit_path = blk_parser.find_element_by_value(parsed_blk, wing, "tankModels", path_is_index=True)
        player_model_type = "tankModels"
    elif blk_parser.find_element_by_value(parsed_blk, wing, "armada", path_is_index=True) != None:
        player_unit_path = blk_parser.find_element_by_value(parsed_blk, wing, "armada", path_is_index=True)
        player_model_type = "armada"
    elif blk_parser.find_element_by_value(parsed_blk, wing, "ships", path_is_index=True) != None:
        player_unit_path = blk_parser.find_element_by_value(parsed_blk, wing, "ships", path_is_index=True)
        player_model_type = "ships"
    else:
        messagebox.showerror("Invalid Player Type", "No valid class of vehicles for the player could be found. Is the player unit of type 'tankModels', 'armada', or 'ships'?")
        sys.exit()
except:
    messagebox.showerror("Unexpected Error", "An unexpected error has occured while trying to find which class of vehicles the player unit belongs to.")
    sys.exit()

player_unit_path_parent = blk_parser.closest_parent_by_path(parsed_blk, player_unit_path)

if player_unit_path_parent != None:
    player_model = blk_parser.find_value_by_path(parsed_blk, player_unit_path_parent + ["unit_class"])
else:
    messagebox.showerror("Unexpected Error", "An unexpected error has occured while trying to path to the player unit.")
    sys.exit()                         

_c = messagebox.askokcancel("Initialization Successful", "All necessary information in the .blk file could be found.\n\nPressing OK will start patching the mission.")
if not _c:
    sys.exit()

#-- create export directory --#
print("Creating export directory...")
export_dir = os.path.abspath(os.curdir + "//export//" + loc_name)

if not os.path.exists(export_dir):
    os.makedirs(export_dir)

#-- get all vehicle names --#
print("Obtaining vehicle names...")
vehicles = os.listdir(os.curdir + "//data//vehicles//" + player_model_type + '//')
vehicle_names = []

for vehicle in vehicles:
    vehicle_name = vehicle.replace(".blkx", "", 1)
    vehicle_names.append(vehicle_name)

#-- convert .blkx to .json --#
print("Converting .blkx to .json...")
for vehicle in vehicle_names:
    try:
        os.rename(f"{os.curdir}//data//vehicles//{player_model_type}//{vehicle}.blkx", f"{os.curdir}//data//vehicles//{player_model_type}//{vehicle}.json")
    except FileNotFoundError:
        print("Conversion of .blkx to .json failed -- can be disregarded if files are already converted.")
        break 

#-- add modifications --#
_c = messagebox.askokcancel("Add modifications", "Would you like to add all available modifcations to the player's vehicle?\n\nPressing 'cancel' will result in the player's vehicle condiction being unchanged from the source mission.")
if _c:
    print("Adding modifications...")
    parsed_blk = blk_parser.modify_value_by_path(parsed_blk, player_unit_path_parent + ["applyAllMods"], True)

#-- write to new missions --#
messagebox.showinfo("Ammunition Information", "The script will do its best to transfer the same amount of ammunition that is available in the original mission to the new missions.\n\nThis may not work well for certain vehicles with specific ammo varieties and/or ammo capacities. If so is the case, please adjust this manually afterwards.")
print("Transferring weaponry to new vehicles and creating missions...")
no_include_vehicles = []
for vehicle in vehicle_names:
    with open(f"{os.curdir}//data//vehicles//{player_model_type}//{vehicle}", "r") as source_veh_json:
        source_veh = json.load(source_veh_json)

        try:
            weapon = source_veh["weapon_presets"]["preset"]["name"]
            parsed_blk = blk_parser.modify_value_by_path(parsed_blk, player_unit_path_parent + ["weapons"], weapon)
        except KeyError:
            print(f"Found no weapon for unit: {vehicle.replace(".json", "")} - Patcher will not make a mission for this vehicle...")
            no_include_vehicles.append(vehicle)

        caliber = ""
        if vehicle not in no_include_vehicles:
            try:
                caliber_source = source_veh["commonWeapons"]["Weapon"][0]["blk"][::-1]
            except KeyError:
                try:
                    caliber_source = source_veh["commonWeapons"]["Weapon"]["blk"][::-1]
                except:
                    print(f"No weapon caliber found for {vehicle.replace(".json", "")} - Patcher will not change ammo configuration for this vehicle...")
            if not any(char.isdigit() for char in caliber_source):
                print(f"No valid caliber found for {vehicle.replace(".json", "")} - Patcher will not change ammo configuration for this vehicle...")
                caliber_source = None

            if caliber_source:
                caliber_chars = []
                for char in caliber_source:
                    if char == "/":
                        break
                    else:
                        caliber_chars.append(char)
                
                caliber_chars = ''.join(caliber_chars)[::-1]
                for char in caliber_chars:
                    if char == "_" and not caliber_chars[caliber_chars.index(char) + 1].isnumeric():
                        break
                    elif char == "_" and caliber_chars[caliber_chars.index(char) - 1].isalpha():
                        break
                    elif len(caliber) > 5:
                        break
                    else:
                        caliber += char

                ammo_types = []
                for k, v in source_veh["modifications"].items():
                    if caliber in k and "ammo_pack" not in k and len(ammo_types) < 4:
                        ammo_types.append(k)
                    elif caliber in ["12_7mm", "13_2mm"] and "ammo_pack" not in k and len(ammo_types) < 4:
                        if caliber[0:2] in k:
                            ammo_types.append(k)
                    elif caliber in ["7_62mm", "7_92mm"] and "ammo_pack" not in k and len(ammo_types) < 4:
                        if caliber[0:1] in k:
                            ammo_types.append(k)

                for i in range(0, 4):
                    if blk_parser.find_value_by_path(parsed_blk, player_unit_path_parent + [f"bulletsCount{i}"]) > 0 and i < len(ammo_types):
                        parsed_blk = blk_parser.modify_value_by_path(parsed_blk, player_unit_path_parent + [f"bullets{i}"], ammo_types[i])
                    else:
                        parsed_blk = blk_parser.modify_value_by_path(parsed_blk, player_unit_path_parent + [f"bullets{i}"], '')

#-- create missions --#
    if vehicle not in no_include_vehicles:
        nation = ""
        for k, v in NATIONS.items():
            if k in vehicle[0:4] and vehicle.replace(k, "", 1)[0] == '_':
                nation = NATIONS[k]

        mission_name = f"{nation} {vehicle.replace(".json", "")} {loc_name}.blk"
        parsed_blk = blk_parser.modify_value_by_path(parsed_blk, ["mission_settings", "mission", "locName"], mission_name)
        parsed_blk = blk_parser.modify_value_by_path(parsed_blk, player_unit_path_parent + ["unit_class"], vehicle.replace(".json", ""))

        with open(f"{export_dir}//{vehicle.replace(".json", ".txt")}", "w") as new_mission:
            content = blk_parser.parse_dict_to_blk(parsed_blk)
            new_mission.write(content)
        
        os.rename(f"{export_dir}//{vehicle.replace(".json", ".txt")}", f"{export_dir}//{mission_name}")

os.rename(f"{source_raw.with_suffix(".txt")}" ,f"{source_raw.with_suffix(".blk")}")

print("Done!")
messagebox.showinfo(title="Success", message=f"Success!\n\nYou will find your missons in this directory:\n\n{export_dir}")
sys.exit()