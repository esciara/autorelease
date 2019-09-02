from behave import given, when, then, step
from behave4cmd0 import command_steps
from behave4cmd0 import textutil
from behave4cmd0.pathutil import posixpath_normpath
import datetime
from git import Repo
from git.exc import GitCommandError
from hamcrest import *


# -----------------------------------------------------------------------------
# STEPS: GitLab related steps
# TYPE: @then
# -----------------------------------------------------------------------------

@then('gitlab should have a release with tag name "{tag_name}"')
def step_gitlab_should_have_release(context, tag_name):
    assert_that([r.tag_name for r in context.gitlab_project.releases.list()], has_item(tag_name))


