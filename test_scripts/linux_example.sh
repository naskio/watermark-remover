#chmod +x ./test_scripts/run_unix.sh
chmod +x ./scripts/dist/WatermarkRemover-linux
./test_scripts/run_unix.sh -e "./scripts/dist/WatermarkRemover-linux" -t 15; echo $? # 10 is enough time