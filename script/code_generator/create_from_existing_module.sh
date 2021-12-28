# Create (2 modules) from existing module
# Parameters
MODULE_NAME="$1"
MODULE_DIRECTORY="$2"
if test "$#" -eq 3; then
  FORCE=true
else
  FORCE=false
fi

# TODO Check if exist, (A) master[template], (B) replicator[code_generator], (C) module
# TODO if force, recreate from C
# TODO if c is code_generator_demo with a different name, execute it.
# TODO if a exist, execute it, and execute b.
# TODO open commit view

# Ready to update it manually or with the interface
if [ "$FORCE" = true ]; then
  # exist
  echo "exist";
fi
