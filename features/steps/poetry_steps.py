from behave import *
from behave4cmd0 import command_steps


@given('there is no package of name "{name}" and version "{version}" on the pypi server')
def step_install_python_package_with_poetry(context, name, version):
    command = 'curl --form ":action=remove_pkg" ' \
              f'--form "name={name}" ' \
              f'--form "version={version}"  ' \
              'http://localhost:8080'
    command_steps.step_i_run_command(context, command)
    command_steps.step_i_run_command(context, command)


@given("I install the python package through poetry")
def step_install_python_package_with_poetry(context):
    command_steps.step_i_run_command(context, "poetry install")
