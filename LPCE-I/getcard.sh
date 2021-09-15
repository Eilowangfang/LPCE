i=0
while read line
do
	((i=i+1))
	echo "Query $i" 
	echo $line
	python3 parser.py "${line}"
	time3=$(date "+%Y-%m-%d %H:%M:%S")
	echo $time3
	echo ""
done < ./8join_test.sql
