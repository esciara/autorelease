Feature: Shared steps for repo setup
  In order to test the features
  As a developer
  I want to create starting repos

  Scenario: Reused step: creation of a starting repo with specific change log
    Given a starting repo at version "0.0.1", with a staged file and a changelog file with:
      """
      Anything I want
      """
    Then a repo named "autorelease-test-repo-" ending with today's date should exist
    And the last commit should have label "0.0.1"
    And a file named "staged_file" should exist
    And the file "staged_file" should be staged in git
    And a file named "Changelog.rst" should exist
    And the file "Changelog.rst" should contain:
      """
      Anything I want
      """

  Scenario: Reused step: creation of a starting repo
    Given a starting repo at version "0.0.1", with a staged file and a changelog file
    Then a repo named "autorelease-test-repo-" ending with today's date should exist
    And the last commit should have label "0.0.1"
    And a file named "staged_file" should exist
    And the file "staged_file" should be staged in git
    And a file named "Changelog.rst" should exist
    And the file "Changelog.rst" should contain:
      """
      0.0.1 (2019-06-12)
      ------------------

      New
      ~~~
      - something new. [Geronimo]
      """

