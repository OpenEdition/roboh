#!/bin/bash

usage() {
	echo "Check response when set a wrong args in CORE API"
		echo "Usage : $0 [-h|--help] [-d|--dataset] [-a| --action] [-o| --output]"
		echo -e "\n\t-h --help\tprint this help\n\t-d --dataset\tpath to the dataset
		\n\t-o --output\tpath to directroy where files is tagged\taction test by default (arg not mandatory)  \n\n"
		exit 1
}

ACTION='test'
OUTPUT='tmp/tag'
while :
do
	case "$1" in
		-h|--help)
			usage
			exit 0
			;;  
		-d|--dataset)
			FILE="$2"
			shift 2
			;;  
		-o|--output)
			OUTPUT="$2"
			shift 2
			;;  
		-a|--action)
			ACTION="$2"
			shift 2
			;;  
		-*|--*=) # unsupported flags
			echo "Error: Unsupported flag $1" >&2
			exit 1
			;;  
		*)  # No more options
			break
			;;  
	esac
done

ve2() { source ../bin/activate; }

/bin/bash -x annotator.sh > annotator.txt &

ve2
echo `python --version`
#echo `python set_tag.py -d text -c $FILE -o $OUTPUT` 1>&3 | $output 1>&2 | cat 3&>1
echo `python set_tag.py -d text -c $FILE -o $OUTPUT`
echo `python cr_learning.py -a $ACTION -s $FILE -t $OUTPUT`

