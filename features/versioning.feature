Feature: versioning of the project
  In order to automate the versioning of my project
  As a developer
  I want a pipeline to version and generate the changelog of my project


  Background:
    Given a new working directory
    And a starting repo at version "0.0.1", with a staged file and a changelog file

#  Scenario: Bumping the version
#    Given I commit the staged file with commit message
#      """
#      fix: this is a fix.
#      """
#    When I bump the version
#    And the git label "0,0,2" should be on the last commit
#
#
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
  Scenario: Generate change logs and update version following a PR merge to master
    Given a repo branch named "pr_branch"
    And the repo branch "pr_branch" is checked out
    And the repo index is committed with message:
      """
      fix: this is a fix.
      """
    And the repo is pushed
    And a merge request from "pr_branch" to "master"
    When I merge the merge request
#    And I wait for the CI/CD pipeline to complete successfully
    And I pull the repo
    And I checkout the "master" branch
    Then the repo head commit should contain the file "ChangeLog.rst"
    And the repo head commit should be tagged "0.0.2"
