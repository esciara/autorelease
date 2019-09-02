Feature: versioning of the project
  In order to automate the versioning of my project
  As a developer
  I want a pipeline to version and generate the changelog of my project


  Background:
    Given a new working directory
    And a starting repo with one initial commit containing a lorem_ipsum file
    And a file named "ChangeLog.rst" with:
      """
      0.0.1 (2019-06-12)
      ------------------

      New
      ~~~
      - something new. [Geronimo]
      """
    And the file "ChangeLog.rst" is added and committed to the repo with commit message:
      """
      Base commit for test.
      """
    And a repo tag "v0.0.1" on the repo head
    And the repo is pushed
    And a file named ".gitlab-ci.yaml" with:
      """
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
    And a file named "staged_file" with:
      """
      Lorem ipsum
      """
    And all files are added to the repo index

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
    And the repo head commit should be tagged "v0.0.2"
