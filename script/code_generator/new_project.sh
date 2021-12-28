# Create a new module with code
# Parameters
MODULE_NAME="$1"
MODULE_DIRECTORY="$2"
if test "$#" -eq 3; then
  FORCE=true
else
  FORCE=false
fi

# TODO Check if exist
# TODO change name into code_generator_demo
# TODO Create code generator empty module with demo
# TODO revert code_generator_demo
# TODO execute create_code_generator_from_existing_module.sh with force option
# TODO open web interface on right database already selected locally with make run

if [ "$FORCE" = true ]; then
  # exist
  echo "exist";
fi
