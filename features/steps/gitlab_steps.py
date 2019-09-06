import time

from behave import given, when, then, step
from behave.step_registry import given
from steps.git_steps import _append_suffix_to_branch
from gitlab.exceptions import GitlabGetError

from hamcrest import *


# -----------------------------------------------------------------------------
# STEPS: Git related steps
# TYPE: @given
# -----------------------------------------------------------------------------

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


@given('I set on GitLab the GITLAB_TOKEN environment variable for the @semantic-release/gitlab plugin')
def step_set_env_variables_for_semantic_release_gitlab(context):
    try:
        variable = context.gitlab_project.variables.get("GITLAB_TOKEN")
        variable.value = context.gitlab_client.private_token
        variable.save()
    except GitlabGetError as e:
        if e.response_code == 404:
            context.gitlab_project.variables.create({
                "key": "GITLAB_TOKEN",
                "value": context.gitlab_client.private_token,
                "masked": "true"
            })
    # "GITLAB_TOKEN", context.gitlab_client.private_token)


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


@then('gitlab should have a release with tag name "{tag_name}"')
def step_gitlab_should_have_release(context, tag_name):
    assert_that([r.tag_name for r in context.gitlab_project.releases.list()], has_item(tag_name))


@then('I wait for the CI/CD pipeline to successfully complete')
def step_wait_ci_cd_successfully_complete(context):
    branch = context.repo.head.ref.name
    commit = context.repo.head.commit
    pipelines = []
    start_time = time.time()
    timeout = 10
    while not pipelines and time.time() < start_time + timeout:
        time.sleep(1.)
        pipelines = context.gitlab_project.pipelines.list(ref=branch, sha=commit)
    assert_that(pipelines, is_not(empty()), f"No pipelines found for branch '{branch}' at commit '{commit}' "
                                            f"after a timeout of {timeout} seconds.")
    assert_that(pipelines, has_length(1), "At checkpoint 1 of 2 : "
                                          f"Too many pipelines for branch '{branch}' at commit '{commit}': "
                                          "don't know how to deal with it. You will need to update the"
                                          "testing code => aborting.")
    while pipelines[0].status in ["running", "pending"]:
        time.sleep(1.)
        pipelines = context.gitlab_project.pipelines.list(ref=branch, sha=commit)
        assert_that(pipelines, has_length(1), "At checkpoint 2 of 2 : "
                                              f"Too many pipelines for branch '{branch}' at commit '{commit}': "
                                              "don't know how to deal with it. You will need to update the"
                                              "testing code => aborting.")
    assert_that(pipelines[0].status, equal_to('success'))
