import os

from behave import given, when, then, step
from behave4cmd0 import command_steps
from behave4cmd0 import textutil
from behave4cmd0.pathutil import posixpath_normpath
import datetime
from git import Repo
from git.exc import GitCommandError
from hamcrest import *
from environment import raise_config_exception_git
import logging


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
@given('a repo branch named "{branch_name}"')
def step_create_branch(context, branch_name):
    branch_name = _append_suffix_to_branch(context, branch_name)
    context.repo.create_head(branch_name)


@given('the repo branch "{branch_name}" is checked out')
@when('I checkout the "{branch_name}" branch')
def step_checkout_branch(context, branch_name):
    branch_name = _append_suffix_to_branch(context, branch_name)
    context.repo.heads[branch_name].checkout()


@given('the file "{filename}" is added to the repo index')
def step_add_file_to_index(context, filename):
    context.repo.index.add([filename])


@given('all files are added to the repo index')
def step_add_all_files_to_index(context, ):
    context.repo.git.add("--all")


@given('the repo index is committed with message:')
@given('the repo index is committed with message')
def step_commit_with_message(context):
    assert context.text is not None, "REQUIRE: multiline text"
    context.repo.index.commit(context.text)


@given('the file "{filename}" is added and committed to the repo with commit message:')
@given('the file "{filename}" is added and committed to the repo with commit message')
def step_add_file_and_commit_with_message(context, filename):
    step_add_file_to_index(context, filename)
    step_commit_with_message(context)


@step('a repo tag "{tag_name}" on the repo head')
def step_create_tag(context, tag_name):
    context.repo.create_tag(tag_name)


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
                          context.repo.head.ref)
    # force=True)


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


def _append_suffix_to_branch(context, branch_name):
    return f"{branch_name}{context.scenario_branches_suffix}"


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


@when('I merge the merge request')
def step_merge_pr(context):
    context.gitlab_project_mergerequest.merge()


@step('I pull the repo')
@step('the repo is pulled')
def step_pull_repo(context):
    context.repo.git.pull()


# -----------------------------------------------------------------------------
# STEPS: Git related steps
# TYPE: @then
# -----------------------------------------------------------------------------
@then('a repo should exist')
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


@then('the repo has for remote repo the GitLab project (autorelease-test-repo-[TODAY])')
def step_gitlab_repo_exists(context):
    assert_that(context.gitlab_project.http_url_to_repo, equal_to(next(context.repo.remotes.origin.urls)))


@then('the repo should have "{num_of_commits:int}" commit')
@then('the repo should have "{num_of_commits:int}" commits')
def step_repo_should_have_num_commits(context, num_of_commits):
    assert_that(list(context.repo.iter_commits()), has_length(num_of_commits))


@then('the repo tag "{tag_name}" should exist')
def step_tag_should_exits(context, tag_name):
    assert_that([tag.name for tag in context.repo.tags], has_items(*[tag_name]), "The tag should exist.")


@then('the repo head commit should be tagged "{tag_name}"')
def step_head_commit_should_be_tagged_with(context, tag_name):
    step_tag_should_exits(context, tag_name)
    assert_that(context.repo.tags[tag_name].commit, equal_to(context.repo.head.commit),
                "Commits for HEAD and tag should be the same.")


@then('the repo head commit should contain the file "{filename}"')
def step_file_in_head_commit(context, filename):
    _files_in_head_commit(context, [filename])


@then('the repo head commit should contain the files:')
@then('the repo head commit should contain the files')
def step_files_in_head_commit(context):
    assert context.table is not None, "REQUIRE: table"
    assert "filename" in context.table.headings, "REQUIRE: a 'filename' column"
    _files_in_head_commit(context, [row['filename'] for row in context.table])


def _files_in_head_commit(context, filenames):
    assert_that(list(context.repo.head.commit.stats.files.keys()), has_items(*filenames))


@then('the repo index should contain the file "{filename}"')
def step_file_staged(context, filename):
    _files_in_index(context, [filename])


@then('the repo index should contain the files:')
@then('the repo index should contain the files')
def step_files_in_head_commit(context):
    assert context.table is not None, "REQUIRE: table"
    assert "filename" in context.table.headings, "REQUIRE: a 'filename' column"
    _files_in_index(context, [row['filename'] for row in context.table])


def _files_in_index(context, filenames):
    assert_that([item.a_path for item in context.repo.index.diff("HEAD")], has_items(*filenames))


@then('the file "{filename}" should contain (templated):')
@then('the file "{filename}" should contain (templated)')
def step_file_should_contain_multiline_text_templated(context, filename):
    assert context.text is not None, "REQUIRE: multiline text"
    expected_text = context.text
    if "{__TODAY__}" in context.text:
        expected_text = textutil.template_substitute(context.text,
                                                     __TODAY__=f"{datetime.date.today()}",
                                                     )
    command_steps.step_file_should_contain_text(context, filename, expected_text)


@then('a new version tag of format "{version_format}" should have been created on the last commit')
def step_new_version_should_be_on_last_commit(context, version_format):
    raise NotImplementedError(
        'STEP: Then a new version tag of format "x.x.x" should have been created on the last commit')
