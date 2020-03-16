Feature: Call Generation

    # NOTE(afournier): there is no API endpoint to list the monitor files
    Scenario: Call with extension call recording activated
        Given the "Call recording" extension is enabled
        Given there are users with infos:
         | firstname | lastname | number | context | protocol |
         | User      | 100      |   1100 | default | sip      |
         | User      | 101      |   1101 | default | sip      |
        When a call is started:
         | caller   | dial | callee   | talk_time | hangup |
         | User 100 | 1101 | User 101 | 3         | callee |
        Then I see no recording file of this call in monitoring audio files page

    Scenario: Bus messages on hold and resume
        Given I listen on the bus for messages:
        | queue | routing_key  |
        | test  | calls.hold.# |
        Given there are users with infos:
        | firstname | lastname | number | context | protocol |
        | Marty     | McFly    |   1001 | default | sip      |
        | George    | McFly    |   1002 | default | sip      |
        Given "Marty McFly" calls "1002"
        Given "George McFly" answers
        When "George McFly" puts his call on hold
        Then I receive a "call_held" on the queue "test" with data:
        | call_id | origin_uuid | user_uuid |
        | ANY     | yes         | ANY       |
        When "George McFly" resumes his call
        Then I receive a "call_resumed" on the queue "test" with data:
        | call_id | origin_uuid | user_uuid |
        | ANY     | yes         | ANY       |

    Scenario: Transfer timeout is respected
        Given there are users with infos:
        | firstname | lastname | number | context | protocol |
        | Marty     | McFly    |   1001 | default | sip      |
        | George    | McFly    |   1002 | default | sip      |
        | Zzyxz     | Axalotl  |   1003 | default | sip      |
        Given "Marty McFly" calls "1002"
        Given "George McFly" answers
        When "George McFly" transfers "Marty McFly" to "1003" with timeout "3" via xivo-ctid-ng
        Then "Zzyxz Axalotl" is ringing
        When I wait 4 seconds
        Then "Zzyxz Axalotl" is hungup
