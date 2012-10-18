Feature: Queues

    Scenario: Add queue named with non-ASCII characters
        When I add the queue "epicerie" with display name "Épicerie" with extension "3000" in "default"
        Then queue "Épicerie" is displayed in the list

    Scenario: Cannot add queue named general
        When I add the queue "general" with display name "general" with extension "3001" in "default" with errors
        Then I see errors

    Scenario: Queue strategy ring linear
        When I add the queue "green" with ring strategy at "linear"
        Then I see no errors
        When I edit the queue "green"
        Then I see no errors
        When I edit the queue "green" and set ring strategy at "ringall"
        Then I see no errors
        When I edit the queue "green" and set ring strategy at "linear"
        Then I see errors