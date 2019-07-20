from behave import given, when, then, step
from behave4cmd0 import command_steps
from behave4cmd0 import textutil
from behave4cmd0.pathutil import posixpath_normpath
import datetime
from git import Repo
from hamcrest import *


# -----------------------------------------------------------------------------
# STEPS: Git related steps
# TYPE: multiple (@step)
# -----------------------------------------------------------------------------
@step('I wait for the CI/CD pipeline to complete successfully')
def step_wait_for_pipeline_success(context):
    raise NotImplementedError('STEP: Given I wait for the CI/CD pipeline to complete successfully')


# -----------------------------------------------------------------------------
# STEPS: Git related steps
# TYPE: @given
# -----------------------------------------------------------------------------
@given('a starting repo at version "{version}", with a staged file and a changelog file with')
def step_starting_repo_with_specific_change_log(context, version):
    repo = context.repo = Repo.init(posixpath_normpath(context.workdir))

    command_steps.step_a_file_named_filename_with(context, "ChangeLog.rst")

    repo.git.add(["ChangeLog.rst"])

    repo.git.commit(m="pipo bingo")

    origin = repo.create_remote('origin', context.gitlab_project.http_url_to_repo)
    origin.push(repo.head.ref, force=True)

    # Make sure test branch is unprotected in GitLab, which protects first pushed
    # branches
    context.gitlab_project.branches.get(repo.head.ref.name).unprotect()

    repo.create_tag("0.0.1")

    context.surrogate_text = "Lorem ipsum"
    command_steps.step_a_file_named_filename_with(context, "staged_file")

    repo.git.add(["staged_file"])


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


@given('a repo branch named "{branch_name}"')
def step_set_current_branch(context, branch_name):
    context.repo.create_head(branch_name)


@given('the repo branch "{branch_name}" is checked out')
def step_set_current_branch(context, branch_name):
    context.repo.heads[branch_name].checkout()


@given('the staged files are committed with message:')
@given('the staged files are committed with message')
def step_commit_with_message(context):
    assert context.text is not None, "REQUIRE: multiline text"
    context.repo.index.commit(context.text)


@given('the repo is pushed')
def step_push_repo(context):
    # context.repo.git.push(f"{branch_name}:{branch_name}", force=True)
    # context.repo.git.push("origin", f"{branch_name}:{branch_name}", force=True)
    # context.repo.remotes.origin.push(set_upstream=True, force=True)
    # context.repo.git.push("--set-upstream", "origin", branch_name, force=True)
    # print(f"remote_name: {context.repo.head.ref.remote_name}")
    # origin = context.repo.remotes.origin
    # context.repo.create_head('master', origin.refs.master)
    # context.repo.remotes.origin.push(force=True)
    context.repo.git.push("--set-upstream",
                          context.repo.remotes.origin,
                          context.repo.head.ref,
                          force=True)



@given('I create a PR from "{source_branch_name}" to "{target_branch_name}"')
def step_create_pr(context, source_branch_name, target_branch_name):
    raise NotImplementedError('STEP: Given I create a PR from "pr_branch" to "master"')


# -----------------------------------------------------------------------------
# STEPS: Git related steps
# TYPE: @when
# -----------------------------------------------------------------------------
@when('I bump the version')
def step_bump_version(context):
    raise NotImplementedError('STEP: When I bump the version')


@when('the git label "{version}" should be on the last commit')
def step_label_should_be_on_last_commit(context, version):
    raise NotImplementedError('STEP: When I should have a git label "0.0.2" at the last commit')


@when('I generate the change log')
def step_generate_change_log(context):
    raise NotImplementedError('STEP: When I generate the change log')


@when('I merge the PR')
def step_merge_pr(context):
    raise NotImplementedError('STEP: When I merge the PR')


# -----------------------------------------------------------------------------
# STEPS: Git related steps
# TYPE: @then
# -----------------------------------------------------------------------------
@then('a local repo should exist')
def step_repo_exists(context):
    try:
        assert_that(context.repo, not_none(), "The repo should exist.")
    except AttributeError:
        assert False, "The repo should exist."


@then('a repo branch named "{branch_name}" should exist')
def step_repo_branch_exists(context, branch_name):
    assert_that([head.name for head in context.repo.heads], has_item(branch_name))


@then('the repo head should be "{branch_name}"')
def step_repo_head_should_be_branch(context, branch_name):
    assert_that(context.repo.head.ref.name, equal_to(branch_name))


@then('the local repo has for remote repo the GitLab project (autorelease-test-repo-[TODAY])')
def step_gitlab_repo_exists(context):
    assert_that(context.gitlab_project.http_url_to_repo, equal_to(next(context.repo.remotes.origin.urls)))


@then('the local repo should have "{num_of_commits:int}" commit')
def step_impl(context, num_of_commits):
    assert_that(list(context.repo.iter_commits()), has_length(num_of_commits))


@then('the last commit should have be tagged "{tag_name}"')
def step_last_commit_labelled(context, tag_name):
    assert_that(context.repo.tags[tag_name].commit, equal_to(context.repo.head.commit))


@then('the file "{filename}" should be in the last commit')
def step_file_in_head_commit(context, filename):
    assert_that(context.repo.head.commit.stats.files, has_key(filename))


@then('the file "{filename}" should be staged in git')
def step_file_staged(context, filename):
    assert_that([item.a_path for item in context.repo.index.diff("HEAD")], contains(filename))


@then('the file "{filename}" should contain (templated)')
def step_file_should_contain_multiline_text_templated(context, filename):
    assert context.text is not None, "REQUIRE: multiline text"
    expected_text = context.text
    if "{__TODAY__}" in context.text or "{__GIT_COMMITER__}" in context.text:
        expected_text = textutil.template_substitute(context.text,
                                                     __TODAY__=datetime.date.today(),
                                                     __GIT_COMMITER__="TO DO"
                                                     )
    command_steps.step_file_should_contain_text(context, filename, expected_text)


@then('the file "{filename}" should have been changed in the last commit')
def step_file_should_have_change_in_last_commit(context, filename):
    raise NotImplementedError('STEP: Then the file "Changelog.rst" should have been changed in the last commit')


@then('a new version tag of format "{version_format}" should have been created on the last commit')
def step_new_version_should_be_on_last_commit(context, version_format):
    raise NotImplementedError(
        'STEP: Then a new version tag of format "x.x.x" should have been created on the last commit')
