from behave import given, when, then, step
from behave4cmd0 import command_steps
from behave4cmd0 import textutil


# -----------------------------------------------------------------------------
# STEPS: Behave4Cmd0 extension related steps
# TYPE: @given
# -----------------------------------------------------------------------------
@given('an executable file named "{filename}" with:')
@given('an executable file named "{filename}" with')
def step_an_executable_file_named_filename_with(context, filename):
    command_steps.step_a_file_named_filename_with(context, filename)
    command_steps.step_i_successfully_run_command(context, f"chmod +x {filename}")


# -----------------------------------------------------------------------------
# STEPS: Behave4Cmd0 extension related steps
# TYPE: @then
# -----------------------------------------------------------------------------
@then('the file "{filename}" should contain (templated):')
@then('the file "{filename}" should contain (templated)')
def step_file_should_contain_multiline_text_templated(context, filename):
    assert context.text is not None, "REQUIRE: multiline text"
    expected_text = context.text
    substitutes = ["{__TEST_RUN_START_DATE__}",
                   "{__GITLAB_PROJECT_URL__}",
                   "{__COMMIT_HEAD_SHA__}",
                   "{__COMMIT_HEAD_URL__}",
                   "{__COMMIT_HEAD_1_SHA__}",
                   "{__COMMIT_HEAD_1_URL__}",
                   ]
    if any(e in context.text for e in substitutes):
        repo = context.repo
        gitlab_project_url = context.gitlab_project.web_url
        commit_url_prefix = gitlab_project_url + "/commit/"
        commit_head_sha = repo.commit("HEAD").hexsha[:7]
        commit_head_url = commit_url_prefix + commit_head_sha
        commit_head_1_sha = repo.commit("HEAD~1").hexsha[:7]
        commit_head_1_url = commit_url_prefix + commit_head_1_sha


        expected_text = textutil.template_substitute(context.text,
                                                     __TEST_RUN_START_DATE__=f"{context.test_run_start_date}",
                                                     __GITLAB_PROJECT_URL__=f"{gitlab_project_url}",
                                                     __COMMIT_HEAD_SHA__=f"{commit_head_sha}",
                                                     __COMMIT_HEAD_URL__=f"{commit_head_url}",
                                                     __COMMIT_HEAD_1_SHA__=f"{commit_head_1_sha}",
                                                     __COMMIT_HEAD_1_URL__=f"{commit_head_1_url}",
                                                     )
    command_steps.step_file_should_contain_text(context, filename, expected_text)
