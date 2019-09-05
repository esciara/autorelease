Feature: Using semantic-release
  In order to prepare the release of a new version of my project
  As a developer
  I want to use `semantic-release` to generate the changelog and bump the version of my project

  Background:
    Given a new working directory
    And a starting repo with one initial commit containing a lorem_ipsum file
    And the pre-installed NodeJS packages are copied to the working directory
    And the NodeJS following packages are installed:
      | package_name                |
      | semantic-release            |
      | @semantic-release/exec      |
      | @semantic-release/git       |
      | @semantic-release/gitlab    |
      | @semantic-release/changelog |
    And a file named "package.json" with:
        """
        {
          "name": "autorelease_behave_support_packages",
          "version": "v0.0.1",
          "description": "Only created for behave bdd tests on autorelease",
          "main": "no_file.js",
          "author": "",
          "license": "ISC",
          "devDependencies": {
            "@semantic-release/changelog": "^3.0.4",
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
            "@semantic-release/changelog",
            "@semantic-release/git",
            "@semantic-release/gitlab",
          ],
        }
        """
    And I set the GITLAB_TOKEN, GITLAB_URL and GITLAB_PREFIX environment variables for the @semantic-release/gitlab plugin
    And a file named "sample_file" with:
        """
        Lorem ipsum
        """
    And all files are added and committed to the repo with commit message:
        """
        fix: This is a fix commit for functional tests.
        """
    When I run semantic-release on current branch and with args "--no-ci"
    Then it should pass
    And the repo head commit should be tagged "v0.0.1"
    And gitlab should have a release with tag name "v0.0.1"
    And a file named "CHANGELOG.md" should exist
    And the repo head commit should contain the file "CHANGELOG.md"
    And the file "CHANGELOG.md" should contain (templated):
#        # Changelog
#
#        All notable changes to this project will be documented in this file. See [standard-version](https://github.com/conventional-changelog/standard-version) for commit guidelines.
#
        """
        ## [0.0.1]({__GITLAB_PROJECT_URL__}/compare/v0.0.0...v0.0.1) ({__TEST_RUN_START_DATE__})


        ### Bug Fixes

        * This is a fix commit for functional tests. ([{__COMMIT_HEAD_1_SHA__}]({__COMMIT_HEAD_1_URL__}))
        """


  Scenario: Bumping version on non NodeJS files
    Given a repo tag "v0.0.1" on the repo head
    And a file named "__version__.py" with:
        """
        1
        version = "0.0.1"
        moreversion = "0.0.1"
        version = "0.0.1" bla
        version = "0.0.1"
        1
        """
    And a file named "other_version.py" with:
        """
        1
        other_version = "0.0.1"
        more other_version = "0.0.1"
        other_version = "0.0.1" bla
        other_version = "0.0.1"
        1
        """
    And an executable file named "find_and_replace_versions.sh" with:
        """
        sed -i -e "s/^version = \"${1}\"$/version = \"${2}\"/g" __version__.py
        sed -i -e "s/^other_version = \"${1}\"$/other_version = \"${2}\"/g" other_version.py
        """
    And a file named ".releaserc" with:
        """
        {
          "plugins": [
            "@semantic-release/commit-analyzer",
            "@semantic-release/release-notes-generator",
            "@semantic-release/changelog",
            ["@semantic-release/exec", {
              "prepareCmd": "./find_and_replace_versions.sh ${lastRelease.version} ${nextRelease.version}"
            }],
            ["@semantic-release/git", {
              "assets": [["**", "!.git", "!**/node_modules"]]
            }],
            "@semantic-release/gitlab",
          ]
        }
        """
    And all files are added and committed to the repo with commit message:
        """
        fix: This is a commit for functional tests.
        """
    And I set the GITLAB_TOKEN, GITLAB_URL and GITLAB_PREFIX environment variables for the @semantic-release/gitlab plugin
    When I run semantic-release on current branch and with args "--no-ci"
    Then it should pass
    And the file "__version__.py" should contain:
        """
        1
        version = "0.0.2"
        moreversion = "0.0.1"
        version = "0.0.1" bla
        version = "0.0.2"
        1
        """
    And the file "other_version.py" should contain:
        """
        1
        other_version = "0.0.2"
        more other_version = "0.0.1"
        other_version = "0.0.1" bla
        other_version = "0.0.2"
        1
        """
    And the repo head commit should contain the files:
      | filename         |
      | __version__.py   |
      | other_version.py |


  Scenario: Publish a python package to a pypi server
    Given there is no package of name "hello_world" and version "0.0.1" on the pypi server
    And a file named "hello_world.py" with:
        """
        if __name__ == '__main__':
        print("Hello World!")
        """
    And a file named "README.md" with:
        """
        Lorem ipsum
        """
    And a file named "pyproject.toml" with:
        """
        [tool.poetry]
        name = "hello_world"
        version = "0.0.1"
        description = "Hello world!"
        license = "LGPL v2.1"
        authors = [ "Foo Bar <foo@bar.com>" ]
        readme = 'README.md'
        repository = "http://repo"
        homepage = "https://homepage"
        keywords = []
        """
    And I install the python package through poetry
    And all files are added and committed to the repo with commit message:
        """
        fix: This is a commit for functional tests.
        """
    When I run "poetry publish --build -r localpypi"
    Then it should pass