from behave import given, when, then, step
from behave4cmd0 import command_steps, command_util
from behave4cmd0 import textutil
from behave4cmd0.pathutil import posixpath_normpath
import datetime
from git import Repo
from git.exc import GitCommandError
from hamcrest import *
from environment import raise_config_exception_git
from steps.versioning import step_repo_should_have_num_commits, step_head_commit_should_contain_file


@given('a starting repo with one initial commit containing a file named "{filename}"')
def step_starting_repo_with_specific_change_log(context, filename):
    _clone_pre_initialised_repo_and_check_git_config(context)
    repo = context.repo

    _initialise_repo_content_if_empty(context)

    step_repo_should_have_num_commits(context, 1)
    step_head_commit_should_contain_file(context, filename)

    _cleanup_repo_from_previous_test_runs_conflicting_changes(context)

    repo.create_head(f"master{context.scenario_branches_suffix}").checkout()

    repo.git.push("--set-upstream",
                  repo.remotes.origin,
                  repo.head.ref)


def _cleanup_repo_from_previous_test_runs_conflicting_changes(context):
    _cleanup_repo_gitlab_releases(context.gitlab_project)
    _cleanup_repo_tags(context.repo)


def _cleanup_repo_tags(repo):
    for tag in repo.tags:
        repo.delete_tag(tag)
        repo.git.push("--delete",
                      repo.remotes.origin,
                      tag)


def _cleanup_repo_gitlab_releases(gitlab_project):
    for release in gitlab_project.releases.list():
        gitlab_project.releases.delete(release.tag_name)


@given('a starting repo at version "{version}", with a staged file and a changelog file with')
def step_starting_repo_with_specific_change_log(context, version):
    # repo = context.repo = Repo.init(posixpath_normpath(context.workdir))
    _clone_pre_initialised_repo_and_check_git_config(context)
    repo = context.repo

    _initialise_repo_content_if_empty(context)

    repo.create_head(f"master{context.scenario_branches_suffix}").checkout()

    command_steps.step_a_file_named_filename_with(context, "ChangeLog.rst")

    repo.git.add("--all")
    repo.git.commit(m=f"Base commit for {context.scenario_branches_suffix[1:]}")

    repo.create_tag("0.0.1")

    repo.git.push("--set-upstream",
                  context.repo.remotes.origin,
                  context.repo.head.ref)
    # Make sure test branch is unprotected in GitLab, which protects first pushed
    # branches
    context.gitlab_project.branches.get(repo.head.ref.name).unprotect()

    context.surrogate_text = """
stages:
  - test
  - versioning
  - release
  
test:
  image: alpine:latest
  stage: test
  script:
    - echo "Simulate test passing"
  only:
    - merge_requests
  
versioning:
  image: python:3.6
  stage: versioning
  script:
    - echo "Simulate versioning stage successful"
  only:
    - master

release:
  image: python:3.6
  stage: release
  script:
    - echo "Simulate release stage successful"
  only:
    - tags
"""
    command_steps.step_a_file_named_filename_with(context, ".gitlab-ci.yml")

    context.surrogate_text = "Lorem ipsum"
    command_steps.step_a_file_named_filename_with(context, "staged_file")

    repo.git.add("--all")


def _clone_pre_initialised_repo_and_check_git_config(context):
    try:
        repo = Repo.clone_from(context.gitlab_project.http_url_to_repo, posixpath_normpath(context.workdir))
    except GitCommandError as e:
        if e.status == 128:
            raise_config_exception_git()
        else:
            raise e
    command_util.ensure_context_attribute_exists(context, "repo", repo)


def _initialise_repo_content_if_empty(context):
    try:
        context.repo.head.commit
    except ValueError as e:
        if "does not exist" in e.args[0]:
            context.surrogate_text = "Lorem ipsum"
            command_steps.step_a_file_named_filename_with(context, "lorem_ipsum")
            context.surrogate_text = None
            context.repo.git.add("--all")
            context.repo.git.commit(m="Initial commit")
            context.repo.git.push()
        else:
            raise e


@given('a starting repo at version "{version}", with a staged file and a changelog file')
def step_starting_repo(context, version):
    context.surrogate_text = """
0.0.1 (2019-06-12)
------------------

New
~~~
- something new. [Geronimo]
"""
    step_starting_repo_with_specific_change_log(context, version)
