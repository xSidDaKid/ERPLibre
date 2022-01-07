#!./.venv/bin/python
import argparse
import asyncio
import logging
import os
import sys
import uuid
from typing import Tuple

from colorama import Fore

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(__name__)

LOG_FILE = "./.venv/make_test.log"


def get_config():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="""\
        Run code generator test in parallel.
""",
        epilog="""\
""",
    )
    args = parser.parse_args()
    return args


lst_ignore_warning = [
    "have the same label:",
    "odoo.addons.code_generator.extractor_module_file: Ignore next error about"
    " ALTER TABLE DROP CONSTRAINT.",
]

lst_ignore_error = [
    "fetchmail_notify_error_to_sender",
    'odoo.sql_db: bad query: ALTER TABLE "db_backup" DROP CONSTRAINT'
    ' "db_backup_db_backup_name_unique"',
    'ERROR: constraint "db_backup_db_backup_name_unique" of relation'
    ' "db_backup" does not exist',
    'odoo.sql_db: bad query: ALTER TABLE "db_backup" DROP CONSTRAINT'
    ' "db_backup_db_backup_days_to_keep_positive"',
    'ERROR: constraint "db_backup_db_backup_days_to_keep_positive" of relation'
    ' "db_backup" does not exist',
    "odoo.addons.code_generator.extractor_module_file: Ignore next error about"
    " ALTER TABLE DROP CONSTRAINT.",
]


def check_result(task_list, tpl_result):
    lst_error = []
    lst_warning = []

    for i, result in enumerate(tpl_result):
        lst_log = result[0].split("\n") + result[1].split("\n")
        for log_line in lst_log:
            is_ignore_error = False
            if "error" in log_line.lower():
                # Remove ignore error
                for ignore_error in lst_ignore_error:
                    if ignore_error in log_line:
                        is_ignore_error = True
                        break
                if not is_ignore_error:
                    lst_error.append(log_line)

            is_ignore_warning = False
            if "warning" in log_line.lower():
                # Remove ignore warning
                for ignore_warning in lst_ignore_warning:
                    if ignore_warning in log_line:
                        is_ignore_warning = True
                        break
                if not is_ignore_warning:
                    lst_warning.append(log_line)
        if result[2]:
            lst_error.append(
                f"Return status error for test {task_list[i].cr_code.co_name}"
            )

    if lst_warning:
        print(f"{Fore.YELLOW}{len(lst_warning)} WARNING{Fore.RESET}")
        i = 0
        for warning in lst_warning:
            i += 1
            print(f"[{i}]{warning}")

    if lst_error:
        print(f"{Fore.RED}{len(lst_error)} ERROR{Fore.RESET}")
        i = 0
        for error in lst_error:
            i += 1
            print(f"[{i}]{error}")

    if lst_error or lst_warning:
        str_result = (
            f"{Fore.RED}{len(lst_error)} ERROR"
            f" {Fore.YELLOW}{len(lst_warning)} WARNING"
        )
    else:
        str_result = f"{Fore.GREEN}SUCCESS 🍰"

    print(f"{Fore.BLUE}Summary TEST {str_result}{Fore.RESET}")


def print_log(lst_task, tpl_result):
    if len(lst_task) != len(tpl_result):
        _logger.error("Different length for log... What happen?")
        return
    with open(LOG_FILE, "w") as f:
        for i, task in enumerate(lst_task):
            result = tpl_result[i]
            status_str = "PASS" if not result[2] else "FAIL"
            f.write(
                f"\nTest execution {i + 1} - {status_str} -"
                f" {task.cr_code.co_name}\n\n"
            )
            if result[0]:
                f.write(result[0])
                f.write("\n")
            if result[1]:
                f.write(result[1])
                f.write("\n")
    print(f"Log file {LOG_FILE}")


async def run_command(*args):
    # Create subprocess
    process = await asyncio.create_subprocess_exec(
        *args,
        # stdout must a pipe to be accessible as process.stdout
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    # Wait for the subprocess to finish
    stdout, stderr = await process.communicate()
    # Return stdout, stderr, returncode
    str_out = stdout.decode().strip() if stdout else ""
    str_err = stderr.decode().strip() if stderr else ""
    return str_out, str_err, process.returncode


async def test_exec(
    path_module_check: str,
    module_to_install=None,
    module_to_generate=None,
    search_class_module=None,
    script_after_init_check=None,
    lst_init_module_name=None,
) -> Tuple[str, str, int]:

    res = ""
    err = ""
    status = 0

    if lst_init_module_name:
        for module_name in lst_init_module_name:
            res1, err1, status1 = await run_command(
                "./script/code_generator/check_git_change_code_generator.sh",
                path_module_check,
                module_name,
            )
            res += (
                "\nTest"
                " ./script/code_generator/check_git_change_code_generator.sh"
                f" {path_module_check} {module_name}"
            )
            res += "\n" + res1 if res1 else ""
            err += "\n" + err1 if err1 else ""
            status += status1

    if module_to_generate:
        res1, err1, status1 = await run_command(
            "./script/code_generator/check_git_change_code_generator.sh",
            path_module_check,
            module_to_generate,
        )
        res += (
            "\nTest"
            " ./script/code_generator/check_git_change_code_generator.sh"
            f" {path_module_check} {module_to_generate}"
        )
        res += "\n" + res1 if res1 else ""
        err += "\n" + err1 if err1 else ""
        status += status1

    # Leave when detect anomaly
    if status:
        return res, err, status

    if script_after_init_check and not status:
        res2, err2, status = await run_command(script_after_init_check)
        res += "\n" + res2 if res2 else ""
        err += "\n" + err2 if err2 else ""

    is_db_create = False
    unique_database_name = f"test_demo_{uuid.uuid4()}"[:63]
    if not status:
        res2, err2, status = await run_command(
            "./script/db_restore.py", "--database", unique_database_name
        )
        res += (
            f"\nTest ./script/db_restore.py --database {unique_database_name}"
        )
        res += "\n" + res2 if res2 else ""
        err += "\n" + err2 if err2 else ""
        is_db_create = not status

    if not status and lst_init_module_name:
        # Parallel execution here

        # No parallel execution here
        str_test = ",".join(lst_init_module_name)
        script_name = (
            "./script/addons/install_addons_dev.sh"
            if module_to_generate
            else "./script/addons/install_addons.sh"
        )
        res_app, err_app, status = await run_command(
            script_name,
            unique_database_name,
            str_test,
        )
        res += f"\nTest {script_name} {unique_database_name} {str_test}"
        res += "\n" + res_app if res_app else ""
        err += "\n" + err_app if err_app else ""

    if not status and search_class_module and module_to_install:
        path_template_to_generate = os.path.join(
            path_module_check, module_to_generate
        )
        path_module_to_generate = os.path.join(
            path_module_check, search_class_module
        )
        # Parallel execution here

        # No parallel execution here
        res_app, err_app, status = await run_command(
            "./script/code_generator/search_class_model.py",
            "--quiet",
            "-d",
            path_module_to_generate,
            "-t",
            path_template_to_generate,
        )
        res += (
            "\nTest ./script/code_generator/search_class_model.py --quiet -d"
            f" {path_module_to_generate} -t {path_template_to_generate}"
        )
        res += "\n" + res_app if res_app else ""
        err += "\n" + err_app if err_app else ""

    if not status and module_to_generate and module_to_install:
        # Parallel execution here

        # No parallel execution here
        res_app, err_app, status = await run_command(
            "./script/code_generator/install_and_test_code_generator.sh",
            unique_database_name,
            module_to_generate,
            path_module_check,
            module_to_install,
        )
        res += (
            "\nTest"
            " ./script/code_generator/install_and_test_code_generator.py"
            f" {unique_database_name} {module_to_generate} {path_module_check} {module_to_install}"
        )
        res += "\n" + res_app if res_app else ""
        err += "\n" + err_app if err_app else ""

    if is_db_create:
        res3, err3, status_db = await run_command(
            "./.venv/bin/python3",
            "./odoo/odoo-bin",
            "db",
            "--drop",
            "--database",
            unique_database_name,
        )
        res += f"\nTest drop database {unique_database_name}"
        res += "\n" + res3 if res3 else ""
        err += "\n" + err3 if err3 else ""
        status = status if status else status_db

    return res, err, status


async def run_demo_test() -> Tuple[str, str, int]:
    lst_test_name = [
        "demo_helpdesk_data",
        "demo_internal",
        "demo_internal_inherit",
        "demo_mariadb_sql_example_1",
        "demo_portal",
        "demo_website_data",
        "demo_website_leaflet",
        "demo_website_snippet",
    ]
    res, err, status = await test_exec(
        "./addons/TechnoLibre_odoo-code-generator-template",
        lst_init_module_name=lst_test_name,
    )

    return res, err, status


async def run_mariadb_test() -> Tuple[str, str, int]:
    res = ""
    err = ""
    status = 0
    # Migrator
    res1, err1, status1 = await test_exec(
        "./addons/TechnoLibre_odoo-code-generator-template",
        module_to_install="demo_mariadb_sql_example_1",
        module_to_generate=(
            "code_generator_migrator_demo_mariadb_sql_example_1"
        ),
        script_after_init_check=(
            "./script/database/restore_mariadb_sql_example_1.sh"
        ),
        lst_init_module_name=[
            "code_generator_portal",
        ],
    )
    res += "\n" + res1 if res1 else ""
    err += "\n" + err1 if err1 else ""
    status += status1
    # Template
    res2, err2, status2 = await test_exec(
        "./addons/TechnoLibre_odoo-code-generator-template",
        module_to_install="code_generator_demo_mariadb_sql_example_1",
        module_to_generate=(
            "code_generator_template_demo_mariadb_sql_example_1"
        ),
        search_class_module="demo_mariadb_sql_example_1",
        lst_init_module_name=[
            "code_generator_portal",
            "demo_mariadb_sql_example_1",
        ],
    )
    res += "\n" + res2 if res2 else ""
    err += "\n" + err2 if err2 else ""
    status += status2
    # Code generator
    res3, err3, status3 = await test_exec(
        "./addons/TechnoLibre_odoo-code-generator-template",
        module_to_install="demo_mariadb_sql_example_1",
        module_to_generate="code_generator_demo_mariadb_sql_example_1",
    )
    res += "\n" + res3 if res3 else ""
    err += "\n" + err3 if err3 else ""
    status += status3

    return res, err, status


async def run_helloworld_test() -> Tuple[str, str, int]:
    res, err, status = await run_command(
        "./test/code_generator/hello_world.sh",
    )

    return res, err, status


def print_summary_task(task_list):
    for task in task_list:
        print(task.cr_code.co_name)


def run_all_test() -> None:
    task_list = []

    # task_list.append(run_demo_test())
    # task_list.append(run_helloworld_test())
    task_list.append(run_mariadb_test())

    print_summary_task(task_list)

    loop = asyncio.get_event_loop()
    commands = asyncio.gather(*task_list)
    tpl_result = loop.run_until_complete(commands)
    loop.close()
    print_log(task_list, tpl_result)
    check_result(task_list, tpl_result)


def main():
    config = get_config()

    run_all_test()

    return 0


if __name__ == "__main__":
    sys.exit(main())
