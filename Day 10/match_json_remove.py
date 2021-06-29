from pathlib import Path
import os

fileTest = r"C:\Users\a9132\Desktop\白咕咕\match.json"

def fileremove_match_json():
    try:
        os.remove(fileTest)
    except OSError as e :
        print(e)
    else:
        print("File is delete successfully")

def filecreate_match_json():
    match_json_file = Path("match.json")
    match_json_file.touch(exist_ok = True)
    File = open(match_json_file)
    file = open("match.json", "w+")
    file.write("{}")