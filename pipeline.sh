#!/bin/bash

usage() {
	echo "This script is dedicated to make alone the full pipeline for train or test roboh "
		echo "Usage : $0 [-h|--help] [-d|--dataset] [-a| --action] [-o| --output]"
		echo -e "\n\t-h --help\tprint this help\n\t-d --dataset\tpath to the dataset
		\n\t-o --output\tpath to directroy where files is tagged\t-a --action\action test by default (arg not mandatory)  \n\n"
		exit 1
}

ve2() { source ../bin/activate; }

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


RUNNER=$(ps auxf | grep analysisrunner | awk '{print $12}' | grep python)
if [ "$RUNNER" == "" ]
then
	# Activate first venv with python 2.7 and launch socket servor in a new bash process
	bash -c "source echo/bin/activate && cd ./echosocket && python ./analysisrunner.py | sed -e 's/^/ECHO TAGGING: \t/' &" 
else
	echo "RUNNER is already working";
fi

# Activate second venv with python 3.4
ve2
py_v=$(python --version)
#echo "$py_v"
echo "Wait a few moment... And be patient!!"
tag=$(python set_tag.py -d text -c $FILE -o $OUTPUT | sed -e "s/^/NERD TAGGING: \t/")
echo "$tag"

PIDS=$(ps auxf | grep analysisrunner | grep -v source | grep -v grep | awk '{print $2}' | head -n 1)
kill $PIDS

learn=$(python cr_learning.py -a $ACTION -s $FILE -t $OUTPUT | sed -e "s/^/RESULT: \t/")
echo "$learn"




