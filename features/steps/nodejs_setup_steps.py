import os
from distutils.dir_util import copy_tree
from behave import given, when, then, step

from behave4cmd0 import command_steps, command_util, pathutil, textutil
from hamcrest import assert_that, contains_string, any_of, contains_inanyorder, matches_regexp

from steps.git_steps import step_add_file_to_index
from re import search
import logging


# -----------------------------------------------------------------------------
# STEPS: NodeJS related steps
# TYPE: @given
# -----------------------------------------------------------------------------
@given(
    'I set the GITLAB_TOKEN, GITLAB_URL and GITLAB_PREFIX environment variables for the @semantic-release/gitlab plugin')
def step_set_env_variables_for_semantic_release_gitlab(context):
    command_steps.step_I_set_the_environment_variable_to(context, "GITLAB_TOKEN", context.gitlab_client.private_token)
    command_steps.step_I_set_the_environment_variable_to(context, "GITLAB_URL", context.gitlab_client.url)
    gitlab_prefix = context.gitlab_client.api_url.replace(context.gitlab_client.url.rstrip("/"), "")
    command_steps.step_I_set_the_environment_variable_to(context, "GITLAB_PREFIX", gitlab_prefix)


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


@given('the NodeJS package "{package_name}" is installed')
def step_nodejs_package_installed(context, package_name):
    command_steps.step_i_run_command(context, "npm list --depth=0")
    # TODO add the NodeJS pre-installed packages directory in the failure message
    assert_that(context.command_result.output, matches_regexp(_nodejs_package_name_output_regex(package_name)),
                f"NodeJS pre-installed packages must contain the `{package_name}` package.")


@given('the NodeJS following packages are installed')
@given('the NodeJS following packages are installed:')
def step_nodejs_packages_installed(context):
    assert context.table is not None, "REQUIRE: table"
    assert "package_name" in context.table.headings, "REQUIRE: a 'package_name' column"
    command_steps.step_i_run_command(context, "npm list --depth=0")
    # command_steps.step_it_should_pass(context)
    expected_package_names = [row["package_name"] for row in context.table]
    package_names_regex = [_nodejs_package_name_output_regex(package_name) for package_name in
                           expected_package_names]
    is_formatted_package_names_in_output = [bool(search(regex, context.command_result.output))
                                            for regex in package_names_regex]
    package_names_in_output = [a for a, b in zip(expected_package_names, is_formatted_package_names_in_output) if b]
    assert_that(package_names_in_output, contains_inanyorder(*expected_package_names),
                f"NodeJS pre-installed packages must contain the given packages.")


def _nodejs_package_name_output_regex(package_name):
    return r"(─|--) " + package_name + "@"


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
    npx_command = f"npx {command} --debug"
    logging.warning(f"npx_command: {npx_command}")
    command_steps.step_i_run_command(context, npx_command)


@when('I run semantic-release on current branch and with args "{args}"')
def step_i_run_semantic_release_current_branch_args(context, args):
    command = f"semantic-release --branch {context.repo.head.ref.name} {args}"
    if " --repository-url " not in args and " -r " not in args:
        command = f"{command} --repository-url {next(context.repo.remotes.origin.urls)}"
    step_i_run_local_nodejs_built_command(context, command)
