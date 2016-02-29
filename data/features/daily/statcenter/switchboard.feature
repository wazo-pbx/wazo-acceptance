Feature: Switchboard statistics

  Scenario: Call abandoned in the incoming queue
    Given a configured switchboard with an operator with infos:
    | firstname | lastname | number | context | protocol | agent_number |
    | Alice     | A        |   1001 | default | sip      |         1001 |
    Given there are users with infos:
    | firstname | lastname | number | context | protocol |
    | Bob       | B        |   1002 | default | sip      |
    Given "Bob B" calls "3009"
    Given "Alice A" is ringing
    When "Bob B" hangs up
    Then I should receive the following switchboard statistics:
    | Event                     |
    | SwitchboardEnteredEvent   |
    | SwitchboardAbandonedEvent |
    | SwitchboardWaitTimeEvent  |

  Scenario: Call answered by the operator with no transfer
    Given a configured switchboard with an operator with infos:
    | firstname | lastname | number | context | protocol | agent_number |
    | Alice     | A        |   1001 | default | sip      |         1001 |
    Given there are users with infos:
    | firstname | lastname | number | context | protocol |
    | Bob       | B        |   1002 | default | sip      |
    Given "Bob B" calls "3009"
    Given "Alice A" answers
    When "Bob B" hangs up
    Then I should receive the following switchboard statistics:
    | Event                     |
    | SwitchboardEnteredEvent   |
    | SwitchboardCompletedEvent |
    | SwitchboardWaitTimeEvent  |

  Scenario: Call on a full switchboard
    Given a configured switchboard with an operator with infos:
    | firstname | lastname | number | context | protocol | agent_number |
    | Alice     | A        |   1001 | default | sip      |         1001 |
    Given there are users with infos:
    | firstname | lastname | number | context | protocol |
    | Bob       | B        |   1002 | default | sip      |
    | Charles   | C        |   1003 | default | sip      |
    Given the switchboard is configured to receive a maxium of "1" call
    Given "Bob B" calls "3009"
    When "Charles C" calls "3009" and waits until the end
    Then I should receive the following switchboard statistics:
    | Event                     |
    | SwitchboardEnteredEvent   |
    | SwitchboardForwardedEvent |
