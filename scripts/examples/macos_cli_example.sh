#chmod +x ./scripts/run_unix.sh
chmod +x ./dist/WatermarkRemover-macos-cmd
./scripts/run_unix.sh -e "./dist/WatermarkRemover-macos-cmd" -t 30; echo $? # 20 is enough time
# not authorized => exit code 1
# authorize from System Preferences > Security & Privacy
# run again
# pop up window => click "Open"
# success => exit code 0