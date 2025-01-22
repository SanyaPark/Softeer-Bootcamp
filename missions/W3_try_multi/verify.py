import subprocess

def run_command(cmd):
    """
    Runs a shell command and returns the output.
    """
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"FAIL: {cmd} -> {e.stderr.strip()}")
        return None

def verify_config():
    """
    Verifies the configuration settings.
    This function verifies configs of core-site.xml, hdfs-site.xml, yarn-site.xml
    """
    expected_settings_hdfs = {
        "fs.defaultFS": "hdfs://namenode:9000",
        "hadoop.tmp.dir": "/hadoop/tmp",
        "io.file.buffer.size": "131072",
        'dfs.replication': "2",
        'dfs.blocksize': "134217728",
        'dfs.namenode.name.dir': "/hadoop/dfs/name"
    }

    for key, expected in expected_settings_hdfs.items():
        cmd = ["hdfs", "getconf", "-confKey", key]
        value = run_command(cmd)
        if value == expected:
            print(f"PASS: {cmd} -> {value}")
        else:
            print(f"FAIL: {cmd} -> {value} (expected {expected})")

    expected_settings_mapred = {
        'mapreduce.framework.name': 'yarn',
        'mapreduce.job.tracker': 'namenode:9001',
        'mapreduce.task.io.sort.mb': '256'
    }

    for key, expected in expected_settings_mapred.items():
        cmd = ["hdfs", "getconf", "-confKey", key]
        value = run_command(cmd)
        if value == expected:
            print(f"PASS: {cmd} -> {value}")
        else:
            print(f"FAIL: {cmd} -> {value} (expected {expected})")

    expected_settings_yarn = {
        'yarn.resourcemanager.address': 'namenode:8032',
        'yarn.nodemanager.resource.memory-mb': '8192',
        'yarn.scheduler.minimum-allocation-mb': '1024'
    }

    for key, expected in expected_settings_yarn.items():
        cmd = ["hdfs", "getconf", "-confKey", key]
        value = run_command(cmd)
        if value == expected:
            print(f"PASS: {cmd} -> {value}")
        else:
            print(f"FAIL: {cmd} -> {value} (expected {expected})")
            
    if rep_factor := run_command(cmd := ["hdfs", "getconf", "-confKey", 'dfs.replication']) == '2':
        print(f"PASS: Replication factor is {rep_factor}")
    else:
        print(f"FAIL: Replication factor is {rep_factor} (expected 2)")

def test_hdfs():
    """
    Verifies HDFS functionality.
    """
    print("Testing HDFS functionality...")
    test_file = "/temp/lorem_ipsum.txt"
    hdfs_path = "/user/lorem_ipsum.txt"

    # Create a test file locally
    with open(test_file, "w") as f:
        f.write("Test file content.")

    # Copy the test file to HDFS
    run_command(["hdfs", "dfs", "-put", test_file, hdfs_path])

    # Verify the replication factor
    cmd = ["hdfs", "dfs", "-stat", "%r", hdfs_path]
    replication = run_command(cmd)
    if replication == "2":
        print(f"PASS: Replication factor is {replication}")
    else:
        print(f"FAIL: Replication factor is {replication} (expected 2)")

def test_mapreduce():
    """
    Runs a MapReduce job and checks for successful completion.
    """
    print("Testing MapReduce functionality...")
    # cmd = ["hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount /temp /temp/output"]

    cmd = ['./sample_mapred.sh']
    output = run_command(cmd)
    if output:
        print("PASS: MapReduce job completed successfully.")
    else:
        print("FAIL: MapReduce job failed.")



if __name__ == "__main__":
    # verify_config()
    # test_hdfs()
    test_mapreduce()
