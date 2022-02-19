#!/bin/bash

# usage:
# Executable:
# ./test_scripts/run_unix.sh -e "./scripts/dist/WatermarkRemover-macos-0.4.0" -t 30; echo $?
# app:
# ./test_scripts/run_unix.sh -a "./scripts/dist/WatermarkRemover-macos-0.4.0.app/" -t 30; echo $?

helpFunction()
{
   echo ""
   echo "Usage: $0 -a macOSAppPath -e executablePath -t timeout"
   echo -e "\t-a macOS app"
   echo -e "\t-e executable (macOS and linux)"
   echo -e "\t-t timeout for success (in seconds)"
   exit 1 # Exit script after printing help
}

while getopts "a:e:t:" opt
do
   case "$opt" in
      a ) app="$OPTARG" ;;
      e ) executable="$OPTARG" ;;
      t ) timeout="$OPTARG" ;;
      ? ) helpFunction ;; # Print helpFunction in case parameter is non-existent
   esac
done

# set default timeout
if [ -z "$timeout" ]; then
   timeout=60
   echo "No timeout specified, using default timeout of $timeout seconds."
fi

# Print helpFunction in case parameters both empty
if [ -z "$app" ] && [ -z "$executable" ]
then
   echo "Only one parameter should be set, but none are set."
   helpFunction
fi

# Print helpFunction in case parameters are empty
if [ "$app" ] && [ "$executable" ]
then
   echo "Only one parameter should be set, but both are set."
   helpFunction
fi

echo "Current directory: $(pwd)."
# Begin script in case all parameters are correct
if [ "$app" ]
then
  echo "Opening app $app with timeout $timeout seconds..."
  timeout $timeout sh -c "open -n $app -W || exit 1" --preserve-status --kill-after 1
elif [ "$executable" ]
then
  echo "Running script $executable with timeout $timeout seconds..."
  timeout $timeout sh -c "$executable || exit 1" --preserve-status --kill-after 1
fi

status=$?
# Check if script and app were run
if [ $status -eq 124 ] || [ $status -eq 137 ] || [ $status -eq 9 ]
then
  echo "Success: timeout of $timeout seconds has been reached with code $status."
  if [ "$app" ]; then
    appname="$(basename -- $app)"
    echo "Closing app $appname..."
    osascript -e "quit app \"$appname\""
  fi
  exit 0
else
  if [ "$app" ]
  then
    echo "Failed => The .app has crashed."
    exit 1 # force failure
  elif [ "$executable" ]
  then
    fiecho "Failed => The script has crashed with code $status."
    exit $status # preserve exit status
  else
    exit 1 # force failure
  fi
fi