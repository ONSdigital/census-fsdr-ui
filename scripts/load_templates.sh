#!/usr/bin/env bash

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd "${DIR}"/.. || exit

DESIGN_SYSTEM_VERSION="14.3.0"

LOCAL_DIR="fsdr-ui/templates"
TEMP_DIR=$(mktemp -d)

mkdir ${LOCAL_DIR}
curl -L --url "https://github.com/ONSdigital/design-system/releases/download/$DESIGN_SYSTEM_VERSION/templates.zip" --output ${TEMP_DIR}/templates.zip
unzip ${TEMP_DIR}/templates.zip -d ${TEMP_DIR}/templates
rm -rf ${LOCAL_DIR}/layout
rm -rf ${LOCAL_DIR}/components
mv ${TEMP_DIR}/templates/templates/* ${LOCAL_DIR}/
rm -rf ${TEMP_DIR}

