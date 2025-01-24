import os, json
import shutil
import subprocess
import xml.etree.ElementTree as ET

def backup_and_modify_config( hadoop_config_dir, changes:json):
    # 변경사항은 { property : value }형식의 json 파일로 주어지고 기존 값을 value로 교체한다고 가정
    try:
        # Step 1: 백업 생성
        backup_dir = os.path.join(hadoop_config_dir, "backup")
        os.makedirs(backup_dir, exist_ok=True)

        for config_file in ["core-site.xml", "hdfs-site.xml", "mapred-site.xml", "yarn-site.xml"]:
            original_file = os.path.join(hadoop_config_dir, config_file)
            backup_file = os.path.join(backup_dir, config_file)
            if os.path.exists(original_file):
                shutil.copy2(original_file, backup_file)
                print(f"Backing up {config_file}...\n")

        # Step 2: 설정 수정
        for config_file in ["core-site.xml", "hdfs-site.xml", "mapred-site.xml", "yarn-site.xml"]:
            print(f"Modifying {config_file}...")
            file_path = os.path.join(hadoop_config_dir, config_file)
            if os.path.exists(file_path):
                tree = ET.parse(file_path)
                root = tree.getroot()

                for prop, value in changes.items():
                    found = False
                    # 
                    for property_tag in root.findall("property"):
                        name = property_tag.find("name") 
                        if name is not None and name.text == prop: # check <name> == name
                            value_tag = property_tag.find("value")
                            if value_tag is not None: # change value
                                value_tag.text = value
                                found = True
                                print(f"Updated {prop} in {config_file} to {value}")
                    
                    # property가 현재 xml 파일에 없다면?            
                    if not found:
                        # 새 property 추가
                        new_property = ET.SubElement(root, "property")
                        ET.SubElement(new_property, "name").text = prop
                        ET.SubElement(new_property, "value").text = value
                        print(f"Added {prop} in {config_file} with value {value}")

                tree.write(file_path)

        # Step 3: Hadoop 서비스 재시작
        print("Stopping Hadoop DFS...")
        subprocess.run(["$HADOOP_HOME/sbin/stop-dfs.sh"], shell=True, check=True)
        print("Stopping Yarn...")
        subprocess.run(["$HADOOP_HOME/sbin/stop-yarn.sh"], shell=True, check=True)
        
        print("Starting Hadoop DFS...")
        subprocess.run(["$HADOOP_HOME/sbin/start-dfs.sh"], shell=True, check=True)
        print("Starting Yarn...")
        subprocess.run(["$HADOOP_HOME/sbin/start-yarn.sh"], shell=True, check=True)
        
        # subprocess.run(["$HADOOP_HOME/sbin/stop-all.sh"], shell=True, check=True)
        # subprocess.run(["$HADOOP_HOME/sbin/start-all.sh"], shell=True, check=True)        
        print("Configuration changes applied and services restarted.")

    except Exception as e:
        print(f"Error: {e}")

# 예시 사용법
if __name__ == "__main__":
    hadoop_config_dir = "/usr/local/hadoop/etc/hadoop"  # $HADOOP_HOME/etc/hadoop
    changes = {"dfs.replication": "2", 
               "mapreduce.framework.name": "yarn"}
    backup_and_modify_config(hadoop_config_dir, changes)
