Feature: Using standard-version
  In order to prepare the release of a new version of my project
  As a developer
  I want to use `standard-version` to generate the changelog and bump the version of my project


  Background:
    Given a new working directory
    And a starting repo with one initial commit containing a file named "lorem_ipsum"
    And the pre-installed NodeJS packages are copied to the working directory
    And the NodeJS package "standard-version" is installed
#    TODO: make sure git ignores put all NodeJS related files


  Scenario: Creating the first changelog for the project
    And a file named "sample_file" with:
      """
      Lorem ipsum
      """
    And the file "sample_file" is added and committed to the repo with commit message:
      """
      fix: this is a test fix
      """
    When I run the local NodeJS built command "standard-version --first-release"
    Then the command output should contain:
      """
      ✖ skip version bump on first release
      ✔ created CHANGELOG.md
      ✔ outputting changes to CHANGELOG.md
      ✔ committing CHANGELOG.md
      ✔ tagging release v1.0.0
      """
