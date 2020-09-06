#!./.venv/bin/python
import os
import sys
import argparse
import logging

new_path = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(new_path)

from script.git_tool import GitTool

_logger = logging.getLogger(__name__)
CST_EL_GITHUB_TOKEN = "EL_GITHUB_TOKEN"


def get_config():
    """Parse command line arguments, extracting the config file name,
    returning the union of config file and command line arguments

    :return: dict of config file settings and command line arguments
    """
    config = GitTool.get_project_config()

    # TODO update description
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''\
''',
        epilog='''\
'''
    )
    parser.add_argument('-d', '--dir', dest="dir", default="./",
                        help="Path of repo to change remote, including submodule.")
    parser.add_argument('--organization', dest="organization", default="ERPLibre",
                        help="Choose organization to fork and change all repo.")
    parser.add_argument('--github_token', dest="github_token",
                        default=config.get(CST_EL_GITHUB_TOKEN),
                        help="GitHub token generated by user")
    args = parser.parse_args()
    return args


def main():
    config = get_config()
    github_token = config.github_token
    git_tool = GitTool()

    if not github_token:
        raise ValueError("Missing github_token")

    organization_name = config.organization
    lst_repo = git_tool.get_source_repo_addons(repo_path=config.dir, add_repo_root=True)
    lst_repo_organization = [git_tool.get_transformed_repo_info_from_url(
        a.get("url"), repo_path=config.dir, organization_force=organization_name,
        is_submodule=a.get("is_submodule"), sub_path=a.get("sub_path"),
        revision=a.get("revision"), clone_depth=a.get("clone_depth"))
        for a in lst_repo]

    url_not_found_count = 0
    url_found_count = 0

    i = 0
    total = len(lst_repo_organization)
    for repo in lst_repo_organization:
        i += 1
        print(f"Nb element {i}/{total} - {repo.project_name}")
        url = repo.url

        status = git_tool.get_pull_request_repo(upstream_url=url,
                                                github_token=github_token,
                                                organization_name=organization_name)
        if status is False:
            url_not_found_count += 1
        else:
            url_found_count += len(status)

    print(f"Repository not found: {url_not_found_count}")
    print(f"URL found: {url_found_count}")


if __name__ == '__main__':
    main()
