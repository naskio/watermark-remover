#chmod +x ./scripts/run_unix.sh
chmod +x ./dist/WatermarkRemover-linux
./scripts/run_unix.sh -e "./dist/WatermarkRemover-linux" -t 15; echo $? # 10 is enough time