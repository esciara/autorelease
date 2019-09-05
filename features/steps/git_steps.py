from behave import given, when, then, step
from hamcrest import *


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


@given('all files are added and committed to the repo with commit message:')
@given('all files are added and committed to the repo with commit message')
def step_add_all_and_commit_with_message(context):
    step_add_all_files_to_index(context)
    step_commit_with_message(context)


@step('a repo tag "{tag_name}" on the repo head')
def step_create_tag(context, tag_name):
    context.repo.create_tag(tag_name)


@when('I push the repo')
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
def step_head_commit_should_contain_file(context, filename):
    _head_commit_should_contain_files(context, [filename])


@then('the repo head commit should contain the files:')
@then('the repo head commit should contain the files')
def step_files_in_head_commit(context):
    assert context.table is not None, "REQUIRE: table"
    assert "filename" in context.table.headings, "REQUIRE: a 'filename' column"
    _head_commit_should_contain_files(context, [row['filename'] for row in context.table])


@then('the repo index should contain the file "{filename}"')
def step_index_should_contain_file(context, filename):
    _index_should_contain_files(context, [filename])


@then('the repo index should contain the files:')
@then('the repo index should contain the files')
def step_index_should_contain_files(context):
    assert context.table is not None, "REQUIRE: table"
    assert "filename" in context.table.headings, "REQUIRE: a 'filename' column"
    _index_should_contain_files(context, [row['filename'] for row in context.table])


# -----------------------------------------------------------------------------
# Utility functions
# -----------------------------------------------------------------------------
def _append_suffix_to_branch(context, branch_name):
    return f"{branch_name}{context.scenario_branches_suffix}"


def _head_commit_should_contain_files(context, filenames):
    assert_that(list(context.repo.head.commit.stats.files.keys()), has_items(*filenames))


def _index_should_contain_files(context, filenames):
    assert_that([item.a_path for item in context.repo.index.diff("HEAD")], has_items(*filenames))
