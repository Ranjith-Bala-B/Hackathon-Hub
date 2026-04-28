import shutil
import sys

source = r"C:\Users\ranji\.gemini\antigravity\brain\e9a134cf-d446-4f38-9c4a-8d5f2759938f\robot_assistant_1777177744652.png"
dest = r"d:\My Projects\hackathon-hub 2\robot.png"

shutil.copyfile(source, dest)
print("Copied")
