Feature: Using semantic-release
  In order to prepare the release of a new version of my project
  As a developer
  I want to use `standard-version` to generate the changelog and bump the version of my project

  Background:
    Given a new working directory
    And a starting repo with one initial commit containing a file named "lorem_ipsum"
    And the pre-installed NodeJS packages are copied to the working directory
    And the NodeJS package "semantic-release" is installed
    And the NodeJS package "@semantic-release/exec" is installed
    And the NodeJS package "@semantic-release/git" is installed
    And the NodeJS package "@semantic-release/gitlab" is installed
    And a file named "package.json" with:
        """
        {
          "name": "autorelease_behave_support_packages",
          "version": "0.0.1",
          "description": "Only created for behave bdd tests on autorelease",
          "main": "no_file.js",
          "author": "",
          "license": "ISC",
          "devDependencies": {
            "@semantic-release/exec": "^3.3.5",
            "@semantic-release/git": "^7.0.16",
            "@semantic-release/gitlab": "^3.1.7",
            "semantic-release": "^15.13.19"
          }
        }
        """
    And a file named ".gitignore" with:
        """
        node_modules/
        node_modules
        package-lock.json
        """
    And the file ".gitignore" is added and committed to the repo with commit message:
        """
        chore: Ignore NodeJS generated files (used for release workflow)
        """

  Scenario: Creating the first changelog and release for the project
    Given a repo tag "v0.0.0" on the repo head
    And a file named ".releaserc" with:
        """
        {
          "plugins": [
            "@semantic-release/commit-analyzer",
            "@semantic-release/release-notes-generator",
            "@semantic-release/git",
            "@semantic-release/gitlab",
          ],
        }
        """
    And a file named "sample_file" with:
        """
        Lorem ipsum
        """
    And the file "sample_file" is added and committed to the repo with commit message:
        """
        fix: This is a test fix.
        """
    When I run semantic-release on current branch and with args "--no-ci"
#    When I run the local NodeJS built command "semantic-release --no-ci --branch {__TEST_MASTER_BRANCH__}"
    Then the command output should contain:
        """
        ✖ skip version bump on first release
        ✔ created CHANGELOG.md
        ✔ outputting changes to CHANGELOG.md
        ✔ committing CHANGELOG.md
        ✔ tagging release v0.0.1
        """
    And the file "CHANGELOG.md" should contain (templated):
        """
        # Changelog

        All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.

        ### 0.0.1 ({__TODAY__})


        ### Bug Fixes

        * This is a test fix.
        """

#  Scenario: Bumping version on non NodeJS files
#    Given a file named "__version__.py" with:
#        """
#        version = "0.0.1"
#        """
#    And a file named ".bumpversion.cfg" with:
#        """
#        [bumpversion]
#        current_version = 0.0.1
#        commit = False
#        tag = False
#
#        [bumpversion:file:__version__.py]
#        search = version = "{current_version}"
#        replace = version = "{new_version}"
#        """
#    Given a file named ".releaserc" with:
#        """
#        {
#          "plugins": [
#            "@semantic-release/commit-analyzer",
#            "@semantic-release/release-notes-generator",
#            ["@semantic-release/exec", {
#              "verifyConditionsCmd": "./verify.sh",
#              "publishCmd": "./publish.sh ${nextRelease.version} ${options.branch} ${commits.length} ${Date.now()}"
#            }],
#            "@semantic-release/git",
#            "@semantic-release/gitlab",
#          ]
#        }
#        """
#    And all files are added to the repo index
#    And the repo index is committed with message:
#        """
#        fix: This is a test fix.
#        """
##    And the file "sample_file" is added and committed to the repo with commit message:
##        """
##        fix: This is a test fix.
##        """
#    When I run the local NodeJS built command "standard-version --first-release"
#    Then it should pass
##    Then the command output should contain:
##        """
##        ✖ skip version bump on first release
##        ✔ created CHANGELOG.md
##        ✔ outputting changes to CHANGELOG.md
##        ✔ committing CHANGELOG.md
##        ✔ tagging release v0.0.1
##        """
#    And the file "CHANGELOG.md" should contain (templated):
#        """
#        # Changelog
#
#        All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.
#
#        ### 0.0.1 ({__TODAY__})
#
#
#        ### Bug Fixes
#
#        * This is a test fix.
#        """
