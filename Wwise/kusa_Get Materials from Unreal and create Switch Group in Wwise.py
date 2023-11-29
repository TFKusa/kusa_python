import os
import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from waapi import WaapiClient, CannotConnectToWaapiException

def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory()
    return folder_path

def ask_switch_group_name():
    root = tk.Tk()
    root.withdraw()
    switch_group_name = simpledialog.askstring("Input", "Enter the name for the Switch Group:", parent=root)
    return switch_group_name

def find_config_file(folder_path):
    config_path = os.path.join(folder_path, "Config", "DefaultEngine.ini")
    if os.path.isfile(config_path):
        return config_path
    else:
        return None

def parse_file(file_path):
    surface_names = []
    with open(file_path, 'r') as file:
        for line in file:
            if "+PhysicalSurfaces=" in line:
                name_part = line.split('Name="')[-1]
                surface_name = name_part.split('"')[0]
                surface_names.append(surface_name)
    return surface_names

def create_switch_group_in_waapi(surface_names, switch_group_name):
    try:
        with WaapiClient() as client:
            switch_group_args = {
                "name": switch_group_name,
                "type": "SwitchGroup",
                "parent": "\\Switches\\Default Work Unit",
            }
            switch_group = client.call("ak.wwise.core.object.create", switch_group_args)
            switch_group_id = switch_group['id']

            for surface_name in surface_names:
                switch_args = {
                    "name": surface_name,
                    "type": "Switch",
                    "parent": switch_group_id,
                }
                client.call("ak.wwise.core.object.create", switch_args)

            print(f"Switch Group '{switch_group_name}' with switches created successfully.")
    except CannotConnectToWaapiException:
        print("Could not connect to Wwise via WAAPI.")


def main():
    folder_path = select_folder()
    if folder_path:
        config_file_path = find_config_file(folder_path)
        if config_file_path:
            surface_names = parse_file(config_file_path)
            print("Surface Names:", surface_names)

            switch_group_name = ask_switch_group_name()
            if switch_group_name:
                create_switch_group_in_waapi(surface_names, switch_group_name)
            else:
                print("Switch Group creation cancelled.")
        else:
            print("DefaultEngine.ini file not found in the Config folder.")
    else:
        print("No folder was selected.")

if __name__ == "__main__":
    main()
