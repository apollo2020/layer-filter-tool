import os
import shutil
import subprocess
from getpass import getuser
from xml.dom.minidom import parse

def run_command(command):
    p = subprocess.Popen(command, shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT)
    p.wait()

profiles_root = r'\\fileserv\homes'
current_user = getuser()
user_profile = os.path.join(profiles_root, current_user)
addin_install_root = os.path.join(user_profile, r'ArcGIS\AddIns')
local_install_root = os.path.join(r'C:\Users', current_user, r'Documents\ArcGIS\AddIns')

try:
    makeaddin_path = os.path.join(os.getcwd(), 'makeaddin.py')
    run_command(makeaddin_path)
    print("Launched makeaddin.py")
except:
    print("Could not launch makeaddin.py")

print("")

try:
    esriaddin_path = os.path.join(os.getcwd(), 'layer-filter-tool.esriaddin')
    run_command(esriaddin_path)
    print("Launched .esriaddin file.")
except:
    print("Could not launch .esriaddin file.")

print("")

try:
    config_dom = parse('config.xml')
    addin_id = config_dom.getElementsByTagName('AddInID')[0].firstChild.nodeValue
    target_name = config_dom.getElementsByTagName('Target')[0].getAttribute('name')
    target_version = config_dom.getElementsByTagName('Target')[0].getAttribute('version')
    addin_install_dir = os.path.join(addin_install_root, target_name + target_version)
    local_install_dir = os.path.join(local_install_root, target_name + target_version)
    print("Parsed config.xml file.")
except:
    print("Could not parse config.xml file.")

print("")

try:
    if not os.path.isdir(local_install_dir):
        os.mkdir(local_install_dir)
    if addin_id in os.listdir(addin_install_dir):
        from_path = os.path.join(addin_install_dir, addin_id)
        to_path = os.path.join(local_install_dir, addin_id)
        if addin_id in os.listdir(local_install_dir):
            shutil.rmtree(to_path)
            shutil.copytree(from_path, to_path)
            shutil.rmtree(from_path)
        else:
            shutil.copytree(from_path, to_path)
            shutil.rmtree(from_path)
        print("Add-In file moved:")
        print("from: %s" % from_path)
        print("to: %s" % to_path)
        print("")
        print("Ensure the following path is included in your ArcMap additional Add-Ins list:".upper())
        print("path: %s" % local_install_dir)
    else:
        print("Could not find Add-In file.")
except:
    print("Could not move Add-In file.")

print("")

temp = raw_input("Press Enter to exit...")

os.startfile(r"\\fileserv\USA\GIS\David_Mangold\projects\148.Layer_Filter_Tool\maps\mxd\test2.mxd")
