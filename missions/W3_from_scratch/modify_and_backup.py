import os
import shutil
import xml.etree.ElementTree as ET
import subprocess
import sys

def backup_and_modify_config(config_dir, changes):
    """
    Backs up the original configuration files and modifies the specified settings.
    """
    files = ["core-site.xml", "hdfs-site.xml", "yarn-site.xml", "mapred-site.xml"]
    
    for file in files:
        file_path = os.path.join(config_dir, file)
        backup_path = f"{file_path}.bak"

        if not os.path.exists(file_path):
            print(f"ERROR: {file} does not exist in {config_dir}. Skipping.")
            continue
        
        # Backup the file
        print(f"Backing up {file}...")
        shutil.copy(file_path, backup_path)

        # Modify the configuration
        print(f"Modifying {file}...")
        tree = ET.parse(file_path)
        root = tree.getroot()

        for property_name, new_value in changes.items():
            modified = False
            for prop in root.findall("property"):
                name = prop.find("name")
                value = prop.find("value")
                if name is not None and name.text == property_name:
                    value.text = new_value
                    modified = True
                    print(f"Updated {property_name} to {new_value} in {file}")
            if not modified:
                # Add new property if it doesn't exist
                property_element = ET.SubElement(root, "property")
                ET.SubElement(property_element, "name").text = property_name
                ET.SubElement(property_element, "value").text = new_value
                print(f"Added new property {property_name} with value {new_value} to {file}")

        # Save changes
        tree.write(file_path)
    
def restart_hadoop_services():
    """
    Stops and restarts Hadoop services.
    """
    print("Stopping Hadoop DFS...")
    subprocess.run(["stop-dfs.sh"], check=True)

    print("Stopping YARN...")
    subprocess.run(["stop-yarn.sh"], check=True)

    print("Starting Hadoop DFS...")
    subprocess.run(["start-dfs.sh"], check=True)

    print("Starting YARN...")
    subprocess.run(["start-yarn.sh"], check=True)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python modify_config.py <config_dir>")
        sys.exit(1)

    config_dir = sys.argv[1]
    if not os.path.isdir(config_dir):
        print(f"ERROR: {config_dir} is not a valid directory.")
        sys.exit(1)

    changes = {
        "fs.defaultFS": "hdfs://namenode:9000",
        "hadoop.tmp.dir": "/hadoop/tmp",
        "io.file.buffer.size": "131072"
    }

    backup_and_modify_config(config_dir, changes)
    restart_hadoop_services()
    print("Configuration changes applied and services restarted.")
