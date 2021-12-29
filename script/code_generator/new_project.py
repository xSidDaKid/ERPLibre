#!./.venv/bin/python
import argparse
import logging
import os
import sys

from git import Repo
from git.exc import InvalidGitRepositoryError, NoSuchPathError

CODE_GENERATOR_DIRECTORY = "./addons/TechnoLibre_odoo-code-generator-template/"
CODE_GENERATOR_DEMO_NAME = "code_generator_demo"
KEY_REPLACE_CODE_GENERATOR_DEMO = 'MODULE_NAME = "%s"'

logging.basicConfig(
    format=(
        "%(asctime)s,%(msecs)d %(levelname)-8s [%(filename)s:%(lineno)d]"
        " %(message)s"
    ),
    datefmt="%Y-%m-%d:%H:%M:%S",
    level=logging.INFO,
)
_logger = logging.getLogger(__name__)

# TODO Check if exist DONE
# TODO change name into code_generator_demo DONE
# TODO Create code generator empty module with demo DONE
# TODO revert code_generator_demo DONE
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
        help="Directory of the module, need to be a git root directory.",
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
        action="store_true",
        help="Force override directory and module.",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug output",
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

    def search_and_replace_file(self, filepath, lst_search_and_replace):
        """
        lst_search_and_replace is a list of tuple, first item is search, second is replace
        """
        with open(filepath, "r") as file:
            txt = file.read()
            for search, replace in lst_search_and_replace:
                if search not in txt:
                    self.msg_error = (
                        f"Cannot find '{search}' in file '{filepath}'"
                    )
                    _logger.error(self.msg_error)
                    return False
                txt = txt.replace(search, replace)
        with open(filepath, "w") as file:
            file.write(txt)
        return True

    @staticmethod
    def validate_path_ready_to_be_override(name, directory, path=""):
        if not path:
            path = os.path.join(directory, name)
        if not os.path.exists(path):
            return True
        # Check if in git
        try:
            git_repo = Repo(directory)
        except NoSuchPathError:
            _logger.error(f"Directory not existing '{directory}'")
            return False
        except InvalidGitRepositoryError:
            _logger.error(
                f"The path '{path}' exist, but no git repo, use force to"
                " ignore it."
            )
            return False

        status = git_repo.git.status(name, porcelain=True)
        if status:
            _logger.error(
                f"The directory '{path}' has git difference, use force to"
                " ignore it."
            )
            print(status)
            return False
        return True

    @staticmethod
    def restore_git_code_generator_demo(
        code_generator_demo_path, relative_path
    ):
        try:
            git_repo = Repo(code_generator_demo_path)
        except NoSuchPathError:
            _logger.error(
                f"Directory not existing '{code_generator_demo_path}'"
            )
            return False
        except InvalidGitRepositoryError:
            _logger.error(
                f"The path '{code_generator_demo_path}' exist, but no git repo"
            )
            return False

        git_repo.git.restore(relative_path)

    def generate_module(self):
        module_path = os.path.join(self.module_directory, self.module_name)
        if not self.force and not self.validate_path_ready_to_be_override(
            self.module_name, self.module_directory, path=module_path
        ):
            self.msg_error = f"Cannot generate on module path '{module_path}'"
            _logger.error(self.msg_error)
            return False

        cg_path = os.path.join(self.cg_directory, self.cg_name)
        if not self.force and not self.validate_path_ready_to_be_override(
            self.cg_name, self.cg_directory, path=cg_path
        ):
            self.msg_error = f"Cannot generate on cg path '{cg_path}'"
            _logger.error(self.msg_error)
            return False

        template_path = os.path.join(
            self.template_directory, self.template_name
        )
        if not self.force and not self.validate_path_ready_to_be_override(
            self.template_name, self.template_directory, path=template_path
        ):
            self.msg_error = (
                f"Cannot generate on template path '{template_path}'"
            )
            _logger.error(self.msg_error)
            return False

        # Validate code_generator_demo
        code_generator_demo_path = os.path.join(
            CODE_GENERATOR_DIRECTORY, CODE_GENERATOR_DEMO_NAME
        )
        code_generator_demo_hooks_py = os.path.join(
            code_generator_demo_path, "hooks.py"
        )
        code_generator_hooks_path_relative = os.path.join(
            CODE_GENERATOR_DEMO_NAME, "hooks.py"
        )
        if not os.path.exists(code_generator_demo_path):
            self.msg_error = (
                "code_generator_demo is not accessible"
                f" '{code_generator_demo_path}'"
            )
            _logger.error(self.msg_error)
            return False
        if not (
            self.validate_path_ready_to_be_override(
                CODE_GENERATOR_DEMO_NAME, CODE_GENERATOR_DIRECTORY
            )
            and self.search_and_replace_file(
                code_generator_demo_hooks_py,
                [
                    (
                        KEY_REPLACE_CODE_GENERATOR_DEMO
                        % CODE_GENERATOR_DEMO_NAME,
                        KEY_REPLACE_CODE_GENERATOR_DEMO % self.template_name,
                    ),
                    (
                        'value["enable_sync_template"] = False',
                        'value["enable_sync_template"] = True',
                    ),
                ],
            )
        ):
            return False
        cmd = "./script/db_restore.py --database code_generator"
        _logger.info(cmd)
        os.system(cmd)
        _logger.info("========= GENERATE code_generator_demo =========")
        cmd = (
            "./script/addons/install_addons_dev.sh code_generator"
            " code_generator_demo"
        )
        os.system(cmd)
        # Revert code_generator_demo
        self.restore_git_code_generator_demo(
            CODE_GENERATOR_DIRECTORY, code_generator_hooks_path_relative
        )

        # Execute all
        cmd = "./script/db_restore.py --database template"
        os.system(cmd)
        _logger.info(cmd)
        _logger.info(f"========= GENERATE {self.template_name} =========")
        cmd = (
            "./script/addons/install_addons_dev.sh template"
            f" {self.template_name}"
        )
        _logger.info(cmd)
        os.system(cmd)

        cmd = "./script/db_restore.py --database code_generator"
        _logger.info(cmd)
        os.system(cmd)
        _logger.info(f"========= GENERATE {self.cg_name} =========")

        cmd = (
            "./script/addons/install_addons_dev.sh code_generator"
            f" {self.cg_name}"
        )
        _logger.info(cmd)
        os.system(cmd)
        return True


def main():
    config = get_config()
    if config.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    project = ProjectManagement(
        config.module,
        config.directory,
        cg_name=config.code_generator_name,
        template_name=config.template_name,
        force=config.force,
    )
    if project.msg_error:
        return -1

    if not project.generate_module():
        return -1

    return 0


if __name__ == "__main__":
    sys.exit(main())
