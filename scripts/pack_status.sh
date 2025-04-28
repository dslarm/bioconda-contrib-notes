#!/bin/sh

ORIG=$PWD

if [ $1 ]; then
    FILE=$1
    sort -k2 -r -g $FILE > $FILE.sorted
else
    DIR=`mktemp -d /tmp/conda-stats-XXXX`
    cd $DIR
    d=`date  '+%Y-%m-%d'`
    Y=`date '+%Y'`
    M=`date '+%m'`
    revstring1="$d"
    revstring2="$(($Y-1))-$M-01"
    file1=pack-$revstring1.tsv
    file2=pack-$revstring2.tsv
    git clone https://github.com/bioconda/bioconda-stats
    cd bioconda-stats
    git checkout data
    git checkout `git rev-list -n 1 --first-parent --before="$revstring1" --branches data`
    awk '{print ($1 "," $2)}' package-downloads/anaconda.org/bioconda/packages.tsv      | sort -k1 -t, > $file1
    git checkout `git rev-list -n 1 --first-parent --before="$revstring2" --branches data`
    awk '{print ($1 "," $2)}' package-downloads/anaconda.org/bioconda/packages.tsv      | sort -k1 -t, > $file2

    join -a 1 -t, $file1 $file2 | awk --field-separator=, '{print($1 ", " $2-$3)}' | sort -t, -k2 -g -r > $file1.sorted
    FILE=$file1
fi    

if [[ "$TEST" == "1" ]]; then exit 1 ; fi

rm -f packages.log.$d

c=0
echo $PWD
while read -r line; do
	c=$((c+1))
	package=`echo $line  | cut -f 1 -d','`
	conda install -d $package >> packages.log.$d 2>&1
	ERR=$?
	if [ $ERR = 1 ] ; then
		echo FAILED at $c with $line | tee -a $ORIG/pack-status-$file1
	else
		echo SUCCEEDED with $line| tee -a $ORIG/pack-status-$file1
	fi
	
done < $FILE.sorted

