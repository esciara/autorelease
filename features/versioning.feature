Feature: versioning of the project
  In order to automate the versioning of my project
  As a developer
  I want a pipeline to version and generate the changelog of my project


  Background:
    Given a new working directory
    And a starting repo at version "0.0.1", with a staged file and a changelog file

  Scenario: Bumping the version
    Given I commit the staged file with commit message
      """
      fix: this is a fix.
      """
    When I bump the version
    And the git label "0.0.2" should be on the last commit


#  Scenario: Generating the change log
#    Given I commit the staged file with commit message
#      """
#      fix: this is a fix.
#      """
#    When I generate the change log
#    Then the file "Changelog.rst" should contain (templated)
#      """
#      0.0.2 ({__TODAY__})
#      ------------------
#
#      Fix
#      ~~~
#      - this is a fix. [{__GIT_COMMITER__}]
#      """
#
#  Scenario: Generate change logs and update version following a PR merge to master
#    Given the current branch is "pr_branch"
#    And I commit the staged file with commit message
#      """
#      fix: this is a fix.
#      """
#    And I create a PR from "pr_branch" to "master"
#    And I wait for the CI/CD pipeline to complete successfully
#    When I merge the PR
#    And I wait for the CI/CD pipeline to complete successfully
#    Then the file "Changelog.rst" should have been changed in the last commit
#    And a new version tag of format "x.x.x" should have been created on the last commit
