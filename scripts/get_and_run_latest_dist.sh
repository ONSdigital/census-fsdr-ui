# Get code fromthe branch specified as environment variable
git clone http://github.com/ONSDigital/census-fsdr-ui .
git checkout -b $BRANCH

# Install  local python dependancies
pipenv install --deploy --system

# Run the UI
python3 run.py

