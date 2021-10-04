#!/bin/bash
DESTINATION_DIR=${DESTINATION_DIR:-$PWD}
MODULE_DIR=${MODULE_DIR:-$PWD}
ZIPFILE_NAME=${ZIPFILE_NAME:-securityhubfindings-to-rocketchat}
TARGET_DIR=$DESTINATION_DIR/builds
echo "Module dir $MODULE_DIR"
echo "Destination dir $DESTINATION_DIR"
echo "Target dir $TARGET_DIR"
mkdir -p "$TARGET_DIR"
cp ../../lambdas/rocketchat-notification/src/index.py "$TARGET_DIR"
REQUIREMENTS_FILE_PATH=../../lambdas/rocketchat-notification/src/requirements.txt
#python3 "$MODULE_DIR"/requirements_creator.py --file_path "$REQUIREMENTS_FILE_PATH"
pip3 install -r "$REQUIREMENTS_FILE_PATH" -t "$TARGET_DIR"
(cd "$TARGET_DIR" && zip -r "$DESTINATION_DIR"/builds/"$ZIPFILE_NAME".zip ./* -x "*.dist-info*" -x "*__pycache__*" -x "*.egg-info*")


