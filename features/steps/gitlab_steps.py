from behave import given, when, then, step
from behave.step_registry import given

from hamcrest import *


# -----------------------------------------------------------------------------
# STEPS: Git related steps
# TYPE: @when
# -----------------------------------------------------------------------------
@when('I merge the merge request')
def step_merge_pr(context):
    context.gitlab_project_mergerequest.merge()


# -----------------------------------------------------------------------------
# STEPS: GitLab related steps
# TYPE: @then
# -----------------------------------------------------------------------------
from steps.versioning import _append_suffix_to_branch


@then('gitlab should have a release with tag name "{tag_name}"')
def step_gitlab_should_have_release(context, tag_name):
    assert_that([r.tag_name for r in context.gitlab_project.releases.list()], has_item(tag_name))


@given('a merge request from "{source_branch_name}" to "{target_branch_name}"')
def step_create_pr(context, source_branch_name, target_branch_name):
    source_branch_name = _append_suffix_to_branch(context, source_branch_name)
    target_branch_name = _append_suffix_to_branch(context, target_branch_name)
    context.gitlab_project_mergerequest = context.gitlab_project.mergerequests.create(
        {
            'source_branch': source_branch_name,
            'target_branch': target_branch_name,
            'title': f'Created by `behave` for automated BDD testing on {context.scenario_branches_suffix[1:]}'
        }
    )