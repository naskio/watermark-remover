#!/bin/bash
# Build & test locally (unix: bash)
source ".env"
timeout=${1:-45} # default timeout 60s
appname=WatermarkRemover
platform=macos # or: linux
echo "Building for $platform version $VERSION:"
echo "cleaning ..."
python3 build.py --clean --debug=$DEBUG
echo "building ..."
python3 build.py --debug=$DEBUG --version=$VERSION --genenv --sentry_dsn=$SENTRY_DSN
echo "Build complete."
echo "----------------------------------------------------"
echo "Running CLI tests ..."
echo "renaming cli ..."
mv ./dist/$appname ./dist/$appname-$platform
echo "adding permission to cli ..."
chmod +x ./dist/$appname-$platform
echo "running cli ..."
./scripts/run_unix.sh -e "./dist/$appname-$platform" -t $timeout; echo $?
# if macOS, run tests of .app
if [ $platform = "macos" ]; then
  echo "----------------------------------------------------"
  echo "Running .app tests ..."
  echo "adding permission to .app ..."
  chmod +x ./dist/$appname.app/Contents/MacOS/$appname
  echo "running .app ..."
  ./scripts/run_unix.sh -a "./dist/$appname.app/" -t $timeout; echo $?
fi
