Feature: Stat

    Scenario: Generation of event FULL
        Given there are no calls running
        Given there is no agent with number "001"
        Given there is no "FULL" entry in queue "q01"
        Given there is a agent "Agent" "001" with extension "001@statscenter"
        Given there is a queue "q01" saturated with extension "5001@statscenter" with agent "001"
        Given I wait 5 seconds for the dialplan to be reloaded
        Given there is 4 calls to extension "5001@statscenter" then i hang up after "5s"
        Given I wait 5 seconds for the calls processing
        Then i should see 3 "FULL" event in queue "q01" in the queue log
