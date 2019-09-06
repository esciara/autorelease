Feature: CI/CD pipeline
  In order to automate the versioning of my project
  As a developer
  I want a pipeline to do the following for my python package project:
   - to test
   - to version
   - to generate the changelog
   - to publish version and changelog on Gitlab
   - to publish the package on my PyPi


  Background:
    Given a new working directory
    And a starting repo with one initial commit containing a lorem_ipsum file


  Scenario: CI generates the changelog and release for the project
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
    And on GitLab the GITLAB_TOKEN environment variable for the @semantic-release/gitlab plugin is properly set
    And a file named ".gitlab-ci.yml" with:
        # Some lines to help debug can be found at the end of this file
        """
        stages:
          - versioning

        versioning:
          image: node:12-alpine
          stage: versioning
          variables:
            GIT_STRATEGY: fetch
            GIT_DEPTH: "0"
          before_script:
            - apk add --no-cache git
            - git --version
            - git tag -l
            - npm install -g semantic-release@15.13.19
            - npm install -g @semantic-release/changelog@3.0.4
            - npm install -g @semantic-release/exec@3.3.5
            - npm install -g @semantic-release/git@7.0.16
            - npm install -g @semantic-release/gitlab@3.1.7
            - echo $CI_API_V4_URL
            - export GITLAB_URL=`echo $CI_API_V4_URL | sed "s/\/api/%/" | cut -d'%' -f1`
            - echo $GITLAB_URL
            - export GITLAB_PREFIX=`echo $CI_API_V4_URL | sed -e s,$GITLAB_URL,,g`
            - echo $GITLAB_PREFIX
          script:
            - npx semantic-release --branch $CI_COMMIT_REF_NAME --repository-url $CI_REPOSITORY_URL --debug
          only:
            refs:
              - /^master_.*/
        """
    And all files are added and committed to the repo with commit message:
        """
        fix: This is a fix commit for functional tests.
        """
    When I push the repo
    And I wait for the CI/CD pipeline to successfully complete
    And I pull the repo
    Then the repo head commit should be tagged "v0.0.1"
    And Gitlab should have a release with tag name "v0.0.1"
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
    And GitLab should have a release with tag name "v0.0.1"

##############################################
#       TO keep for feature debug needs      #
##############################################
#          before_script:
#            - ls -al
#            - apk add --no-cache git
#            - git --version
#            - git status
#            - git branch --list
#            - apk add --update curl
#            - echo $CI_PROJECT_PATH
#            - echo $CI_PROJECT_NAMESPACE
#            - echo $CI_PROJECT_NAME
#            - echo $CI_COMMIT_REF_NAME
#            - echo $GITLAB_TOKEN
#            - echo $CI_API_V4_URL
#            - export GITLAB_URL=`echo $CI_API_V4_URL | sed "s/\/api/%/" | cut -d'%' -f1`
#            - echo $GITLAB_URL
#            - export GITLAB_PREFIX=`echo $CI_API_V4_URL | sed -e s,$GITLAB_URL,,g`
#            - echo $GITLAB_PREFIX
#            - GITLAB_DOMAIN_NAME=`echo $GITLAB_URL | sed -e s,://,%,g |cut -d'%' -f2`
#            - echo $GITLAB_DOMAIN_NAME
#            - echo "git push --dry-run http://gitlab-ci-token:1S6T2NZqY87rzzU1xzhJ@${GITLAB_DOMAIN_NAME}/${CI_PROJECT_PATH}.git HEAD:${CI_COMMIT_REF_NAME}"
#            - git push --dry-run http://gitlab-ci-token:1S6T2NZqY87rzzU1xzhJ@${GITLAB_DOMAIN_NAME}/${CI_PROJECT_PATH}.git HEAD:${CI_COMMIT_REF_NAME}
#            - echo "curl -s --header "Private-Token:${GITLAB_TOKEN}" ${CI_API_V4_URL}/projects/${CI_PROJECT_NAMESPACE}%2F${CI_PROJECT_NAME}"
#            - curl -s --header "Private-Token:${GITLAB_TOKEN}" ${CI_API_V4_URL}/projects/${CI_PROJECT_NAMESPACE}%2F${CI_PROJECT_NAME} && echo
