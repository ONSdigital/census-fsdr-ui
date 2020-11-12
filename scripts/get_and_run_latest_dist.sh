# Get code fromthe branch specified as environment variable
git clone --branch $BRANCH http://github.com/ONSDigital/census-fsdr-ui /opt/repo
cp -a /opt/repo/fsdr-ui/* .

# Install  local python dependancies
pipenv install --deploy --system

# Run the UI
python3 run.py

