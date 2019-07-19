Feature: Shared steps for repo setup
  In order to test the features
  As a developer
  I want to create starting repos

#  Scenario: Reused step: creation of a starting repo with specific change log
#    Given a new working directory
#    And a starting repo at version "0.0.1", with a staged file and a changelog file with
#      """
#      Anything I want
#      """
#    Then a local repo should exist
#    And a repo named "autorelease-test-repo-" ending with today's date should exist on GitLab
#    And the last commit should have label "0.0.1"
#    And a file named "staged_file" should exist
#    And the file "staged_file" should be staged in git
#    And a file named "ChangeLog.rst" should exist
#    And the file "ChangeLog.rst" should contain
#      """
#      Anything I want
#      """

  @wip
  Scenario: Reused step: creation of a starting repo
    Given a new working directory
    And a starting repo at version "0.0.1", with a staged file and a changelog file
    Then a local repo should exist
#    And a repo named "autorelease-test-repo-" ending with today's date should exist on GitLab
    And a file named "ChangeLog.rst" should exist
    And the file "ChangeLog.rst" should contain
      """
      0.0.1 (2019-06-12)
      ------------------

      New
      ~~~
      - something new. [Geronimo]
      """
    And a file named "staged_file" should exist
    And the local repo should have "1" commit
    And the file "ChangeLog.rst" should be in the last commit
    And the file "staged_file" should be staged in git
    And the last commit should have be tagged "0.0.1"

