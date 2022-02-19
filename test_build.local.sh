#!/bin/bash
# Build & test locally (unix: bash)

version=0.4.0
timeout=35
appname=WatermarkRemover
platform=macos # or: linux

echo "Building for $platform version $version ..."
echo "cleaning ..."
rm -r build
rm -r dist
rm "$appname-$platform-$version.spec"
python3 ./scripts/build.py
echo "Build complete."
echo "----------------------------------------------------"
echo "Running CLI tests ..."
echo "renaming cli ..."
mv ./dist/$appname-$platform-$version ./dist/$appname-$platform
echo "adding permission to cli ..."
chmod +x ./dist/$appname-$platform
echo "running cli ..."
./test_scripts/run_unix.sh -e "./dist/$appname-$platform" -t $timeout; echo $?
# if macOS, run tests of .app
if [ $platform = "macos" ]; then
  echo "----------------------------------------------------"
  echo "Running .app tests ..."
  echo "renaming .app ..."
  mv ./dist/$appname-$platform-$version.app ./dist/$appname.app
  echo "adding permission to .app ..."
  chmod +x ./dist/$appname.app/Contents/MacOS/$appname-$platform-$version
  echo "running .app ..."
  ./test_scripts/run_unix.sh -a "./dist/$appname.app/" -t $timeout; echo $?
fi
