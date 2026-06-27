#Adapted to my project from the tutorial

# Check if exactly two parameters were provided
if [ $# -ne 2 ]; then
    echo "Usage: $0 <source_folder> <destination_folder>"
    echo "  <source_folder> is the folder containing the files to be copied."
    echo "  <destination_folder> is the folder where the files will be copied."
    exit 1
fi

# Assign parameters to variables
SOURCE=$1
DEST=$2

# Verify that source folder exists
if [ ! -d "$SOURCE" ]; then
    echo "Error: Source folder '$SOURCE' does not exist."
    exit 1
fi

# Create the destination folder structure
mkdir -p "$DEST/static"
mkdir -p "$DEST/templates"

# Create app.py in the destination folder
touch "$DEST/app.py"

# Copy files from the source folder to the destination/static folder

#All the PWA files
cp "$SOURCE/style.css" "$DEST/static/"
cp "$SOURCE/script.js" "$DEST/static/"
cp "$SOURCE/bigIcon.png" "$DEST/static/"
cp "$SOURCE/favicon.ico" "$DEST/static/"
cp "$SOURCE/manifest.json" "$DEST/static/"
cp "$SOURCE/service-worker.js" "$DEST/static/"

#All the images

#All the templates
cp "$SOURCE/charsheets.html" "$DEST/templates/"
cp "$SOURCE/create_event.html" "$DEST/templates/"
cp "$SOURCE/create_notices.html" "$DEST/templates/"
cp "$SOURCE/dice.html" "$DEST/templates/"
cp "$SOURCE/edit_profile.html" "$DEST/templates/"
cp "$SOURCE/index.html" "$DEST/templates/"
cp "$SOURCE/login.html" "$DEST/templates/"
cp "$SOURCE/notes.html" "$DEST/templates/"
cp "$SOURCE/notices.html" "$DEST/templates/"
cp "$SOURCE/profile.html" "$DEST/templates/"
cp "$SOURCE/signup.html" "$DEST/templates/"
cp "$SOURCE/timetable.html" "$DEST/templates/"
cp "$SOURCE/view_chars.html" "$DEST/templates/"

echo "Files have been successfully copied from '$SOURCE' to '$DEST'."
