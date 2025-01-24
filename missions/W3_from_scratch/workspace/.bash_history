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
pwd
ls
ls -l
cd home
ls -l
exit
hdfs dfs -ls /
hdfs dfs -mkdir /M3
hdfs dfs -ls /
hadoop jar wc.jar WordCount /home/hadoopuser/1984.txt /M3/output
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount /home/hadoopuser/1984.txt /M3/output
pwd
/home/hadoopuser
cd home/hadoopuser
ls
pwd
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount /1984.txt /M3/output
hdfs dfs -put 1984.txt /M3
hdfs dfs -ls /M3
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount /M3/1984.txt /M3/output
hdfs dfs -ls /M3/output
hdfs dfs -cat /M3/output/part-r-00000
clear
hdfs dfs -pwd
hdfs dfs -rm /M3/output
hdfs dfs -ls /
hdfs dfs -ls /M3
hdfs dfs -rm /M3/output/
hdfs dfs -rmr /M3/output
hdfs dfs -rm -r /M3/output/
hdfs dfs -ls /M3
hadoop jar $HADOOP_HOME/share/hadoop/mapreduce/hadoop-mapreduce-examples-*.jar wordcount /M3/1984.txt /M3/output
hdfs dfs -cat /M3/output/part-r-00000
hdfs dfs -ls /M3/output
#
ls
pwd
cd
ls
cd ../
cd ../
pwd
cd usr/local/hadoop
ls
ls /lib
ls /etc
ls
ls /lib
cd tmp
ls
cd dfs
ls
cd name
ls
cd ../
cd ../
cd ../
ls
clear
cd /etc
ls
ls /hadoop
ls hadoop
cd /
cd $HADOOP_HOME
ls
ls etc
ls etc/hadoop
exit
