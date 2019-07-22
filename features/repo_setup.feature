Feature: Shared steps for repo setup
  In order to test the features
  As a developer
  I want to create starting repos

  Scenario: Reused step: creation of a starting repo with specific change log
    Given a new working directory
    And a starting repo at version "0.0.1", with a staged file and a changelog file with
      """
      Anything I want
      """
    Then a repo should exist
    And the repo has for remote repo the GitLab project (autorelease-test-repo-[TODAY])
    And a file named "ChangeLog.rst" should exist
    And the file "ChangeLog.rst" should contain:
      """
      Anything I want
      """
    And a file named ".gitlab-ci.yml" should exist
    And the file ".gitlab-ci.yml" should contain:
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
    And a file named "staged_file" should exist
    And the repo should have "1" commit
    And the repo head commit should contain the files:
      | filename       |
      | ChangeLog.rst  |
    And the repo index should contain the files:
      | filename       |
      | staged_file    |
      | .gitlab-ci.yml |
    And the repo tag "0.0.1" should exist
    And the repo head commit should be tagged "0.0.1"

  Scenario: Reused step: creation of a starting repo
    Given a new working directory
    And a starting repo at version "0.0.1", with a staged file and a changelog file
    Then a repo should exist
    And the repo has for remote repo the GitLab project (autorelease-test-repo-[TODAY])
    And a file named "ChangeLog.rst" should exist
    And the file "ChangeLog.rst" should contain:
      """
      0.0.1 (2019-06-12)
      ------------------

      New
      ~~~
      - something new. [Geronimo]
      """
    And a file named ".gitlab-ci.yml" should exist
    And the file ".gitlab-ci.yml" should contain:
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
    And a file named "staged_file" should exist
    And the repo should have "1" commit
    And the repo head commit should contain the files:
      | filename       |
      | ChangeLog.rst  |
    And the repo index should contain the files:
      | filename       |
      | staged_file    |
      | .gitlab-ci.yml |
    And the repo index should contain the file "staged_file"
    And the repo tag "0.0.1" should exist
    And the repo head commit should be tagged "0.0.1"
