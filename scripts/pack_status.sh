#!/bin/sh


if [ $1 ]; then
    FILE=$1
    sort -k2 -r -g $FILE > $FILE.sorted
else
    d=`date  '+%Y-%m-%d'`
    Y=`date '+%Y'`
    M=`date '+%m'`
    revstring1="$d"
    revstring2="$(($Y-1))-$M-01"
    file1=pack-$revstring1.tsv
    file2=pack-$revstring2.tsv
    git clone https://github.com/bioconda/bioconda-stats
    cd bioconda-stats
    git checkout `git rev-list -n 1 --first-parent --before="$revstring1" data`
    sort -k1 -t, package-downloads/anaconda.org/bioconda/packages.tsv > $file1
    git checkout `git rev-list -n 1 --first-parent --before="$revstring2" data`
    sort -k1 -t,  package-downloads/anaconda.org/bioconda/packages.tsv > $file2

    join -a 1 -t, $file1 $file2 | awk '{print($1,$2-$3)}' | sort -k2 -g > $file1.sorted
    
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

