import os
from distutils.dir_util import copy_tree
from behave import given, when, then, step

from behave4cmd0 import command_steps, command_util, pathutil, textutil
from hamcrest import assert_that, equal_to, contains_string, contains_inanyorder

from steps.versioning import step_add_file_to_index


# -----------------------------------------------------------------------------
# STEPS: NodeJS related steps
# TYPE: @given
# -----------------------------------------------------------------------------
@given('the pre-installed NodeJS packages are copied to the working directory')
def step_copy_pre_installed_nodejs_packages(context):
    resources_path = os.path.join(context.config.base_dir, "resources")
    os.symlink(os.path.join(resources_path, "node_modules"),
               os.path.join(context.workdir, "node_modules"),
               target_is_directory=True)
    # os.symlink(os.path.join(resources_path, "package.json"),
    #            os.path.join(context.workdir, "package.json"))
    # os.symlink(os.path.join(resources_path, "package-lock.json"),
    #            os.path.join(context.workdir, "package-lock.json"))


#     command_util.ensure_workdir_exists(context)
#     filename = ".gitignore"
#     filepath = os.path.join(context.workdir, filename)
#     text_to_use = """node_modules/
# node_modules
# package.json
# package-lock.json
# """
#     pathutil.create_textfile_with_contents(filepath, text_to_use)
#     step_add_file_to_index(context, filename)


@given('the NodeJS package "{package_name}" is installed')
def step_nodejs_package_installed(context, package_name):
    command_steps.step_i_run_command(context, "npm list --depth=0")
    # TODO add the NodeJS pre-installed packages directory in the failure message
    assert_that(context.command_result.output, contains_string(package_name),
                f"NodeJS pre-installed packages must contain the `{package_name}` package.")


# -----------------------------------------------------------------------------
# STEPS: NodeJS related steps
# TYPE: @when
# -----------------------------------------------------------------------------
@when('I run the local NodeJS built command "{command}"')
def step_i_run_local_nodejs_built_command(context, command):
    if "semantic-release" in command:
        command = textutil.template_substitute(command,
                                               __TEST_MASTER_BRANCH__=f"master{context.scenario_branches_suffix}",
                                               )
    print(f"command: {command}")
    new_command = f"npx {command}"
    print(f"new_command: {new_command}")
    # new_command = os.path.join("node_modules", ".bin", command)
    command_steps.step_i_run_command(context, new_command)

@when('I run semantic-release on current branch and with args "{args}"')
def step_i_run_semantic_release_current_branch_args(context, args):
    command = f"semantic-release --branch {context.repo.head.ref.name} {args}"
    if " --repository-url " not in args and " -r " not in args:
        command = f"{command} --repository-url {next(context.repo.remotes.origin.urls)}"
    if " --gitlab-url " not in args:
        command = f"{command} --gitlab-url http://localhost:1000"
    step_i_run_local_nodejs_built_command(context, command)
