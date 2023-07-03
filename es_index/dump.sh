#!/bin/sh
files_list=$(ls)
for file in $files_list;
do index=$(echo "$file" | cut -d . -f 1) ;
type=$(echo "$file" | cut -d . -f 3) ;
elasticdump --input="$file" --output=http://es:9200/"$index" --type="$type" ;
done