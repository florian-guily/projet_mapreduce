#!/bin/bash
# A simple variable example
login="guily-22"
remoteFolder="/tmp/$login/"
bridge="$login@ssh.enst.fr"
fileName="ShuffleClientProgram"
fileExtension=".py"
objFolderName="obj"
sample="sample1.txt"
computers=("tp-1a201-01.enst.fr")
#computers=("tp-1a226-01")
for c in ${computers[@]}; do
  command0=("ssh" "-J" "$bridge" "$login@$c" "lsof -ti | xargs kill -9")
  command1=("ssh" "-J" "$bridge" "$login@$c" "rm -rf $remoteFolder;mkdir $remoteFolder")
  command2=("scp" "-J" "$bridge" "$fileName$fileExtension" "$login@$c:$remoteFolder$fileName$fileExtension")
  command3=("scp" "-J" "$bridge" "$sample" "$login@$c:$remoteFolder$sample")
  command4=("scp" "-J" "$bridge" "-r" "$objFolderName" "$login@$c:$remoteFolder$objFolderName")
  command5=("ssh" "-J" "$bridge" "$login@$c" "cd $remoteFolder;python3 $fileName$fileExtension")
  echo ${command0[*]}
  "${command0[@]}"
  echo ${command1[*]}
  "${command1[@]}"
  echo ${command2[*]}
  "${command2[@]}"
  echo ${command3[*]}
  "${command3[@]}"
  echo ${command4[*]}
  "${command4[@]}"
  echo ${command5[*]}
  "${command5[@]}" &
done