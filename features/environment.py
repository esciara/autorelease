# -*- coding: UTF-8 -*-

#
# Copied straight from behave's repos at
# https://github.com/behave/behave/blob/master/features/environment.py
#

from behave.tag_matcher import ActiveTagMatcher, setup_active_tag_values
from behave4cmd0.setup_command_shell import setup_command_shell_processors4behave
import platform
import sys
import six
import gitlab
import datetime

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
    # -- SETUP GitLab project:
    setup_gitlab_project(context)


def before_feature(context, feature):
    if active_tag_matcher.should_exclude_with(feature.tags):
        feature.skip(reason=active_tag_matcher.exclude_reason)


def before_scenario(context, scenario):
    if active_tag_matcher.should_exclude_with(scenario.effective_tags):
        scenario.skip(reason=active_tag_matcher.exclude_reason)


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
    For this setup to work, proper credentials for using git and for using the
    GitLab API must be present on your system.

    PREREQUISITE

    You must first create an access token on your GitLab instance. See
    https://docs.gitlab.com/ee/user/profile/personal_access_tokens.html for
    instructions. You might or might not want to give full access to the token
    (I did and have not looked at what is the minimal requirement.

    CREDENTIALS FOR GIT

    Please refer to https://git-scm.com/book/en/v2/Git-Tools-Credential-Storage
    for more info. The approach we used is the following:

    - use the 'store' mode by running:
      `git config --global credential.helper 'store --file ~/.git-credentials'`
    - update your `~/.git-credentials` with:
      ```
      https://username:access_token@your.gitlab-server.com
      ```

    CREDENTIALS FOR GITLAB API

    Credentials must be written in the `secrets/gitlab-python.cfg`, which has
    been added to the `.gitignore` file (so it is excluded from the repo).
    Please refer to
    https://python-gitlab.readthedocs.io/en/stable/cli.html#content , which
    details the content needed in this file.
    """
    # Initialise variables
    gl = gitlab.Gitlab.from_config(config_files=["secrets/gitlab-python.cfg"])
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
        target_project = gl.projects.create({"name": project_name})
    # Unprotect the master branch
    target_project.branches.get('master').unprotect()
    # Make project available in context
    context.gitlab_project = target_project
