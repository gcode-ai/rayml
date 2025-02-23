allow_list=$(cat core-requirements.txt requirements.txt | grep -oE "^[a-zA-Z0-9]+[a-zA-Z0-9_\-]*" | paste -d "|" -s -)
echo "Allow list: ${allow_list}"
pip freeze | grep -v "rayml.git" | grep -E "${allow_list}" > "${DEPENDENCY_FILE_PATH}"
