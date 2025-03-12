#!/bin/sh
d=`date  '+%Y-%m-%d'`
if [ $1 ]; then
    FILE=$1
    sort -k2 -r -g $FILE > $FILE.sorted
else
    FILE=packages.$d.tsv
    wget - https://raw.githubusercontent.com/bioconda/bioconda-stats/data/package-downloads/anaconda.org/bioconda/packages.tsv -O $FILE
    tail -n+2 $FILE |sort -k2 -r -g > $FILE.sorted
fi    
rm packages.log.$d
c=0
while read -r line; do
	c=$((c+1))
	package=`echo $line  | cut -f 1 -d' '`
	conda install -d $package >> packages.log.$d 2>&1
	ERR=$?
	if [ $ERR = 1 ] ; then
		echo FAILED at $c with $line
	else
		echo SUCCEEDED with $line
	fi
	
done < $FILE.sorted

