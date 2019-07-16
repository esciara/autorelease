Feature: Shared steps for repo setup
  In order to test the features
  As a developer
  I want to create starting repos

  Scenario: Reused step: creation of a starting repo with specific change log
    Given a starting repo at version "0.0.1", with a staged file and a changelog file with:
      """
      Anything I want
      """
    Then I should have a repo named "autorelease-test-repo-" ending with today's date
    And I should have a git label "0.0.1" at the last commit
    And I should have a file named "staged_file" staged in git
    And I should have a file named "Changelog.rst" with:
      """
      Anything I want
      """

  Scenario: Reused step: creation of a starting repo
    Given a starting repo at version "0.0.1", with a staged file and a changelog file
    Then I should have a repo named "autorelease-test-repo-" ending with today's date
    And I should have a git label "0.0.1" at the last commit
    And I should have a file named "staged_file" staged in git
    And I should have a file named "Changelog.rst" with:
      """
      0.0.1 (2019-06-12)
      ------------------

      New
      ~~~
      - something new. [Geronimo]
      """

