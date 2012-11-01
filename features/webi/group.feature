Feature: Group

    Scenario: Add a group with name and number and remove it
        Given there is no group "2000"
        Given there is no group with name "administrative"
        When I create a group "Administrative" with number "2000"
        Then group "administrative" is displayed in the list
        When group "administrative" is removed
        Then group "administrative" is not displayed in the list

    Scenario: Cannot add a group with a name general
        Given there is no group "2001"
        When I set a group "general" with number "2001"
        When I submit with errors
        Then I see errors