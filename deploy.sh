#!/bin/bash
# A simple variable example
login="guily-22"
remoteFolder="/tmp/$login/"
fileName="ShuffleServerProgram"
fileExtension=".py"
computers=("tp-3a209-10.enst.fr tp-1a201-04.enst.fr tp-1a201-06.enst.fr")
#computers=("tp-1a226-01")
for c in ${computers[@]}; do
  command0=("ssh" "$login@$c" "lsof -ti | xargs kill -9")
  command1=("ssh" "$login@$c" "rm -rf $remoteFolder;mkdir $remoteFolder")
  command2=("scp" "$fileName$fileExtension" "$login@$c:$remoteFolder$fileName$fileExtension")
  command3=("ssh" "$login@$c" "cd $remoteFolder;python3 $fileName$fileExtension")
  echo ${command0[*]}
  "${command0[@]}"
  echo ${command1[*]}
  "${command1[@]}"
  echo ${command2[*]}
  "${command2[@]}"
  echo ${command3[*]}
  "${command3[@]}" &
done