#!./.venv/bin/python
import argparse
import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

# TODO Check if exist
# TODO change name into code_generator_demo
# TODO Create code generator empty module with demo
# TODO revert code_generator_demo
# TODO execute create_code_generator_from_existing_module.sh with force option
# TODO open web interface on right database already selected locally with make run


def get_config():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
        Create new project 
""",
        epilog="""\
""",
    )
    parser.add_argument(
        "-d",
        "--directory",
        required=True,
        help="Directory of the module.",
    )
    parser.add_argument(
        "-m",
        "--module_name",
        required=True,
        help="Module name to create",
    )
    parser.add_argument(
        "-f",
        "--force",
        required=True,
        help="Force override directory and module.",
    )
    args = parser.parse_args()
    return args


def main():
    config = get_config()
    if not os.path.exists(config.directory):
        _logger.error(f"Path directory {config.directory} not exist.")
        return -1

    return 0


if __name__ == "__main__":
    sys.exit(main())
