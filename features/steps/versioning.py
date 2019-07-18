import os

from behave import given, when, then, step
from behave4cmd0 import command_steps
from behave4cmd0 import textutil
from os.path import dirname, abspath
from datetime import date
import gitlab
import git

GITLAB_ACCESS_TOKEN = os.environ.get('GITLAB_TOKEN')

gl = gitlab.Gitlab('https://gitlab.groupeonepoint.com', private_token=GITLAB_ACCESS_TOKEN)
TODAY_DATE = date.today().strftime("%d-%m-%Y")

# todo very bad, change this (pytest conftest like)
# si project "autorelease-test-repo-" + TODAY_DATE existe, pas creer nouveau
for project in gl.projects.list():
    if project.name == "autorelease-test-repo-" + TODAY_DATE:
        gitlab_test_project = project
gitlab_test_project = gitlab_test_project or gl.projects.list(name="autorelease-test-repo-" + TODAY_DATE)
# todo very bad, change this (pytest conftest like)
features_test_folder = dirname(dirname(abspath(__file__)))


# todo very bad, change this (pytest conftest like)


@given('a starting repo at version "{version}", with a staged file and a changelog file with:')
def step_starting_repo_with_specific_change_log(context, version):
    assert context.text is not None, "REQUIRE: multiline text"

    git.Git(dirname(__file__)).clone(
        f"https://gitlab.groupeonepoint.com/m.kaabachi/autorelease-test-repo-{TODAY_DATE}.git")

    # changelog in the repo
    with open("Changelog.rst", 'w') as changelog:
        changelog.write('''
        """
        Anything I want
        """
        ''')

    repo = git.Repo(os.path.join(features_test_folder, "autorelease-test-repo-" + TODAY_DATE))

    repo.git.add("Changelog.rst")
    repo.index.commit("feat: add changelog.rst")
    repo.git.push()

    # a staged file
    open("staged_file", 'w')
    repo.git.add("tests/staged_file")

    # # todo     And a file named "Changelog.rst" should exist
    # #     And the file "Changelog.rst" should contain:
    # changelog = open(os.path.join(features_test_folder, 'Changelog.rst'), 'r').read()
    # # todo change place
    # assert changelog == '''
    #     """
    #     Anything I want
    #     """
    #     '''

    repo.create_tag(version)

    # todo trouver un endroit pour ça gitlab_test_project.delete()
    # gitlab_test_project.delete()
    # todo project.delete(), et supprimer les fichier les autre fichiers dans teardown
    # raise NotImplementedError(
    #     'STEP: Given a starting repo at version "{version}", with a staged file and a changelog file with:')


@given('a starting repo at version "{version}", with a staged file and a changelog file')
def step_starting_repo(context, version):
    context.text = "Anything I want"
    step_starting_repo_with_specific_change_log(context, version)


@then('a repo named "{repo_prefix}" ending with today\'s date should exist')
def step_repo_exists(context, repo_prefix):
    today_date = date.today().strftime("%d-%m-%Y")
    gl = gitlab.Gitlab('https://gitlab.groupeonepoint.com', private_token=GITLAB_ACCESS_TOKEN)
    # assert gl.projects.list(name=repo_prefix + today_date) is not None
    assert f'{repo_prefix}{today_date}' in [project.name for project in gl.projects.list()]
    # raise NotImplementedError(
    #     'STEP: Then I should have a repo named "autorelease-test-repo-" ending with today\'s date')


@then('the last commit should have label "{version}"')
def step_last_commit_labelled(context, version):
    root_dir = dirname(dirname(abspath(__file__)))
    repo = git.Repo(root_dir)
    assert repo.tags[-1] == version
    # raise NotImplementedError('STEP: Then I should have a git label "{version}" at the last commit')


@then('the file "{filename}" should be staged in git')
def step_file_staged(context, filename):
    root_dir = dirname(dirname(abspath(__file__)))
    repo = git.Repo(root_dir)
    staged_files = repo.index.diff("HEAD")
    assert 'staged_file' in [staged_file.a_blob.path.split('/')[-1] for staged_file in staged_files]
    # raise NotImplementedError('STEP: Then I should have a file named "staged_file" staged in git')


@given('I commit the staged file with commit message:')
def step_commit_with_message(context):
    assert context.text is not None, "REQUIRE: multiline text"
    raise NotImplementedError('STEP: Given I commit the staged file with commit message')


@when('I bump the version')
def step_bump_version(context):
    raise NotImplementedError('STEP: When I bump the version')


@when('the git label "{version}" should be on the last commit')
def step_label_should_be_on_last_commit(context, version):
    raise NotImplementedError('STEP: When I should have a git label "0.0.2" at the last commit')


@when('I generate the change log')
def step_generate_change_log(context):
    raise NotImplementedError('STEP: When I generate the change log')


@then('the file "{filename}" should contain (templated):')
def step_file_should_contain_multiline_text_templated(context, filename):
    assert context.text is not None, "REQUIRE: multiline text"
    expected_text = context.text
    if "{__TODAY__}" in context.text or "{__GIT_COMMITER__}" in context.text:
        expected_text = textutil.template_substitute(context.text,
                                                     __TODAY__=date.today(),
                                                     __GIT_COMMITER__="TO DO"
                                                     )
    command_steps.step_file_should_contain_text(context, filename, expected_text)


@given('the current branch is "{branch_name}"')
def step_current_branch_is(context, branch_name):
    raise NotImplementedError('STEP: Given the current branch is "pr_branch"')


@given('I create a PR from "{source_branch_name}" to "{target_branch_name}"')
def step_create_pr(context, source_branch_name, target_branch_name):
    raise NotImplementedError('STEP: Given I create a PR from "pr_branch" to "master"')


@step('I wait for the CI/CD pipeline to complete successfully')
def step_wait_for_pipeline_success(context):
    raise NotImplementedError('STEP: Given I wait for the CI/CD pipeline to complete successfully')


@when('I merge the PR')
def step_merge_pr(context):
    raise NotImplementedError('STEP: When I merge the PR')


@then('the file "{filename}" should have been changed in the last commit')
def step_file_should_have_change_in_last_commit(context, filename):
    raise NotImplementedError('STEP: Then the file "Changelog.rst" should have been changed in the last commit')


@then('a new version tag of format "{version_format}" should have been created on the last commit')
def step_new_version_should_be_on_last_commit(context, version_format):
    raise NotImplementedError(
        'STEP: Then a new version tag of format "x.x.x" should have been created on the last commit')
