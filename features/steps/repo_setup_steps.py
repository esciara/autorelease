from behave import given, when, then, step
from behave4cmd0 import command_steps, command_util
from behave4cmd0.pathutil import posixpath_normpath
from git import Repo
from git.exc import GitCommandError
from environment import raise_config_exception_git
from steps.versioning import step_repo_should_have_num_commits, step_head_commit_should_contain_file


@given('a starting repo with one initial commit containing a lorem_ipsum file')
def step_initialise_starting_repo(context):
    _clone_pre_initialised_repo_and_check_git_config(context)
    repo = context.repo

    _initialise_repo_content_if_empty(context)

    _cleanup_repo_from_previous_test_runs_conflicting_changes(context)

    # Create dedicated master branch for the scenario
    repo.create_head(f"master{context.scenario_branches_suffix}").checkout()

    # Push dedicated master branch to remote
    repo.git.push("--set-upstream",
                  repo.remotes.origin,
                  repo.head.ref)


@given('a starting repo at version "{version}", with a staged file and a changelog file with')
def step_starting_repo_with_specific_version(context, version):
    step_initialise_starting_repo(context)
    repo = context.repo

    command_steps.step_a_file_named_filename_with(context, "ChangeLog.rst")

    repo.git.add("--all")
    repo.git.commit(m=f"Base commit for {context.scenario_branches_suffix[1:]}")

    repo.create_tag(version)

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


@given('a starting repo at version "{version}", with a staged file and a changelog file')
def step_starting_repo(context, version):
    context.surrogate_text = """
0.0.1 (2019-06-12)
------------------

New
~~~
- something new. [Geronimo]
"""
    step_starting_repo_with_specific_version(context, version)


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------
def _initialise_repo_content_if_empty(context, filename="lorem_ipsum"):
    try:
        context.repo.head.commit
    except ValueError as e:
        if "does not exist" in e.args[0]:
            context.surrogate_text = "Lorem ipsum"
            command_steps.step_a_file_named_filename_with(context, filename)
            context.surrogate_text = None
            context.repo.git.add("--all")
            context.repo.git.commit(m="Initial commit")
            context.repo.git.push()
        else:
            raise e


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


def _clone_pre_initialised_repo_and_check_git_config(context):
    try:
        repo = Repo.clone_from(context.gitlab_project.http_url_to_repo, posixpath_normpath(context.workdir))
    except GitCommandError as e:
        if e.status == 128:
            raise_config_exception_git()
        else:
            raise e
    command_util.ensure_context_attribute_exists(context, "repo", repo)
