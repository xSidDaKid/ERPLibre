#!./.venv/bin/python
import argparse
import logging
import os
import sys

logging.basicConfig(
    format=(
        "%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d]"
        " %(message)s"
    ),
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.DEBUG,
)
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
        Create new project for a single module with code generator suite.
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
        "--module",
        required=True,
        help="Module name to create",
    )
    parser.add_argument(
        "--directory_code_generator",
        help="The directory of the code_generator to use.",
    )
    parser.add_argument(
        "--code_generator_name",
        help="The name of the code_generator to use.",
    )
    parser.add_argument(
        "--directory_template_name",
        help="The directory of the template to use.",
    )
    parser.add_argument(
        "--template_name",
        help="The name of the template to use.",
    )
    parser.add_argument(
        "-f",
        "--force",
        help="Force override directory and module.",
    )
    args = parser.parse_args()
    return args


class ProjectManagement:
    def __init__(
        self,
        module_name,
        module_directory,
        cg_name="",
        cg_directory="",
        template_name="",
        template_directory="",
        force=False,
    ):
        self.force = force
        self.msg_error = ""

        self.module_directory = module_directory
        if not os.path.exists(self.module_directory):
            self.msg_error = (
                f"Path directory '{self.module_directory}' not exist."
            )
            _logger.error(self.msg_error)
            return

        self.cg_directory = cg_directory if cg_directory else module_directory
        if not os.path.exists(self.cg_directory):
            self.msg_error = (
                f"Path cg directory '{self.cg_directory}' not exist."
            )
            _logger.error(self.msg_error)
            return

        self.template_directory = (
            template_directory if template_directory else module_directory
        )
        if not os.path.exists(self.template_directory):
            self.msg_error = (
                f"Path template directory '{self.template_directory}' not"
                " exist."
            )
            _logger.error(self.msg_error)
            return

        if not module_name:
            self.msg_error = "Module name is missing."
            _logger.error(self.msg_error)
            return

        # Get module name
        self.module_name = module_name
        # Get code_generator name
        self.cg_name = self._generate_cg_name(default=cg_name)
        # Get template name
        self.template_name = self._generate_template_name(
            default=template_name
        )

    def _generate_cg_name(self, default=""):
        if default:
            return default
        return f"code_generator_{self.module_name}"

    def _generate_template_name(self, default=""):
        if default:
            return default
        return f"code_generator_template_{self.module_name}"

    @staticmethod
    def validate_path_ready_to_be_override(path):
        if not os.path.exists(path):
            return True
        # Check if in git
        pass

    def generate_module(self):
        module_path = os.path.join(self.module_directory, self.module_name)
        if not self.force and self.validate_path_ready_to_be_override(
            module_path
        ):
            self.msg_error = f"Cannot generate on module path '{module_path}'"
            _logger.error(self.msg_error)
            return False

        cg_path = os.path.join(self.cg_directory, self.cg_name)
        if not self.force and self.validate_path_ready_to_be_override(cg_path):
            self.msg_error = f"Cannot generate on cg path '{cg_path}'"
            _logger.error(self.msg_error)
            return False

        template_path = os.path.join(
            self.template_directory, self.template_name
        )
        if not self.force and self.validate_path_ready_to_be_override(
            template_path
        ):
            self.msg_error = (
                f"Cannot generate on template path '{template_path}'"
            )
            _logger.error(self.msg_error)
            return False


def main():
    config = get_config()
    project = ProjectManagement(
        config.module,
        config.directory,
        cg_name=config.code_generator_name,
        template_name=config.template_name,
        force=config.force,
    )
    if project.msg_error:
        return -1

    if project.generate_module():
        return -1

    return 0


if __name__ == "__main__":
    sys.exit(main())
