#chmod +x ./test_scripts/run_unix.sh
chmod +x ./scripts/dist/WatermarkRemover-macos-cmd
./test_scripts/run_unix.sh -e "./scripts/dist/WatermarkRemover-macos-cmd" -t 30; echo $? # 20 is enough time
# not authorized => exit code 1
# authorize from System Preferences > Security & Privacy
# run again
# pop up window => click "Open"
# success => exit code 0