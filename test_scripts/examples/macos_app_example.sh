#chmod +x ./test_scripts/run_unix.sh
# uncompress zip file
# move to the directory
./test_scripts/run_unix.sh -a "./scripts/dist/WatermarkRemover.app/" -t 30; echo $? # 20 is enough time
# not authorized => Failure with exit code 0 (we force to exit code 1)
# authorize from System Preferences > Security & Privacy
# run again
# pop up window => click "Open"
# success => exit code 0