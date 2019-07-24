# -*- coding: UTF-8 -*-

#
# Copied straight from behave's repos at
# https://github.com/behave/behave/blob/master/features/environment.py
#

from behave.tag_matcher import ActiveTagMatcher, setup_active_tag_values
from behave4cmd0.setup_command_shell import setup_command_shell_processors4behave
import platform
import sys
import os
import six
import gitlab
import datetime
import time

# -- MATCHES ANY TAGS: @use.with_{category}={value}
# NOTE: active_tag_value_provider provides category values for active tags.
python_version = "%s.%s" % sys.version_info[:2]
active_tag_value_provider = {
    "python2": str(six.PY2).lower(),
    "python3": str(six.PY3).lower(),
    "python.version": python_version,
    # -- python.implementation: cpython, pypy, jython, ironpython
    "python.implementation": platform.python_implementation().lower(),
    "pypy": str("__pypy__" in sys.modules).lower(),
    "os": sys.platform,
}
active_tag_matcher = ActiveTagMatcher(active_tag_value_provider)


# -----------------------------------------------------------------------------
# HOOKS:
# -----------------------------------------------------------------------------
def before_all(context):
    # -- SETUP ACTIVE-TAG MATCHER (with userdata):
    # USE: behave -D browser=safari ...
    setup_active_tag_values(active_tag_value_provider, context.config.userdata)
    setup_python_path()
    setup_context_with_global_params_test(context)
    setup_command_shell_processors4behave()
    # -- SETUP Logging:
    context.config.setup_logging()
    # -- SETUP GitLab project:
    setup_gitlab_project(context)


def before_feature(context, feature):
    if active_tag_matcher.should_exclude_with(feature.tags):
        feature.skip(reason=active_tag_matcher.exclude_reason)


def before_scenario(context, scenario):
    if active_tag_matcher.should_exclude_with(scenario.effective_tags):
        scenario.skip(reason=active_tag_matcher.exclude_reason)
    delete_all_opened_gitlab_project_mergerequests(context)
    # TODO: refactor to use a fixture
    # -- SETUP prefix for branches
    context.scenario_branches_suffix = f"_scenario_at_{datetime.datetime.now().strftime('%H_%M_%S_%f')}"


# -----------------------------------------------------------------------------
# SPECIFIC FUNCTIONALITY:
# -----------------------------------------------------------------------------
def setup_context_with_global_params_test(context):
    context.global_name = "env:Alice"
    context.global_age = 12


def setup_python_path():
    # -- NEEDED-FOR: formatter.user_defined.feature
    import os
    PYTHONPATH = os.environ.get("PYTHONPATH", "")
    os.environ["PYTHONPATH"] = "." + os.pathsep + PYTHONPATH


def setup_gitlab_project(context):
    """
    All instructions can be found in ``gitlab-access-setup.txt``
    """
    # Initialise variables
    gl = _gitlab_client_from_config()
    project_name_prefix = "autorelease-test-repo-"
    project_name = f"{project_name_prefix}{datetime.date.today()}"
    # Look for project if exists and delete old/deprecated ones
    projects = gl.projects.list(owned=True, search=project_name_prefix)
    target_project = None
    for project in projects:
        if project_name_prefix in project.name:
            if project.name == project_name:
                target_project = project
            else:
                project.delete()
    # Create new project if none found
    if target_project is None:
        # In case the num of projects is limited to 2 per user (this what I found
        # in a company), wait until projects are effectively deleted
        while len(gl.projects.list(owned=True, search=project_name_prefix)) > 0:
            time.sleep(1.)
        target_project = gl.projects.create({"name": project_name})
    # Unprotect all protected branches
    for branch in target_project.protectedbranches.list():
        target_project.branches.get(branch.name).unprotect()
    # Make project available in context
    context.gitlab_project = target_project
    # Handle special case where gitlab is run on local host using docker-compose and
    # https://github.com/jeshan/gitlab-on-compose
    context.http_url_to_repo = context.gitlab_project.http_url_to_repo.replace("http://gitlab/",
                                                                               "http://localhost:1000/")


def _gitlab_client_from_config():
    local_gitlab_python_config = "secrets/gitlab-python.cfg"
    if os.path.isfile(local_gitlab_python_config):
        gl = gitlab.Gitlab.from_config(config_files=[local_gitlab_python_config])
    else:
        try:
            gl = gitlab.Gitlab.from_config()
        except gitlab.config.GitlabConfigMissingError:
            raise_config_exception_gitlab()
    return gl


def raise_config_exception_git():
    _raise_config_exception("GIT credentials not setup/configured.")


def raise_config_exception_gitlab():
    _raise_config_exception("GITLAB credentials not setup/configured.")


class AutoreleaseConfigMissingError(Exception):
    pass


def _raise_config_exception(message):
    with open('gitlab-access-setup.txt', 'r') as f:
        raise AutoreleaseConfigMissingError(f"\n\n##### {message} #####\n\n"
                                            f"READ INSTRUCTIONS BELOW\n\n{f.read()}")


def delete_all_opened_gitlab_project_mergerequests(context):
    for mr in context.gitlab_project.mergerequests.list(state="opened"):
        mr.delete()
