cd /home/hadoopuser/
ls
hdfs dfs -ls /
hdfs dfs -mkdir /sample_dir
hdfs dfs -ls /
hdfs dfs -put /home/hadoopuser/lorem_ipsum.txt /sample_dir/
hdfs dfs -ls /sample_dir
clear
hdfs dfs -ls /
hdfs dfsadmin -report
clear
cd /home/hadoopuser/
ls
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount /test /test/output
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount /sample_dir /sample_dir/output
hdfs dfs -cat /sample_dir/output/part-r-00000
cd /home/hadoopuser/
hdfs dfs -put lorem_ipsum.txt /sample_dir/
jps
exit
