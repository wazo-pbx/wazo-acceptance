Feature: Call Generation

  Scenario: Call to inexistant extension
    Given there are telephony users with infos:
      | firstname | exten | context |
      | Alice     | 1100  | default |
    When "Alice" calls "1190"
    Then "Alice" is hungup immediately

  Scenario: Call to existant extension with answer
    Given there are telephony users with infos:
      | firstname | exten | context |
      | Alice     | 1100  | default |
      | Bob       | 1101  | default |
    When a call is started:
      | caller | dial | callee | talk_time | hangup |
      | Alice  | 1101 | Bob    | 3         | callee |
    Then I have the last call log matching:
      | destination_extension | duration | answered |
      | 1101                  | 3        | True     |

  Scenario: No answer destination with disabled forward exten on no answer
    Given the "forwarding on no-answer" extension is disabled
    Given there are telephony users with infos:
      | firstname | lastname | exten | context |
      | James     | Bond     | 1101  | default |
      | Tiffany   | Case     | 1102  | default |
      | Pussy     | Galore   | 1103  | default |
    Given "James Bond" has a "5" seconds ringing time
    Given "James Bond" has a "noanswer" fallback to user "Pussy Galore"
    When "Tiffany Case" calls "1101"
    Then "James Bond" is ringing
    When I wait "9" seconds for the call processing
    Then "Pussy Galore" is ringing

  Scenario: Busy destination with disabled forward exten on busy
    Given the "forwarding on busy" extension is disabled
    Given there are telephony users with infos:
      | firstname | lastname | exten | context |
      | James     | Bond     | 1101  | default |
      | Honey     | Ryder    | 1102  | default |
      | Sylvia    | Trench   | 1103  | default |
    Given "James Bond" has a "busy" fallback to user "Sylvia Trench"
    When "Honey Ryder" calls "1101"
    Then "James Bond" is ringing
    When "James Bond" hangs up
    When I wait "2" seconds for the call processing
    Then "Sylvia Trench" is ringing

  Scenario: Check that new calls are not marked as on_hold when GETTING calls
    Given there are telephony users with infos:
      | firstname | lastname | exten | context |
      | Oliver    | Queen    | 1001  | default |
      | Thea      | Queen    | 1002  | default |
    Given "Oliver Queen" calls "1002"
    When "Thea Queen" answers
    Then "Oliver Queen" call is not "on_hold"
    Then "Thea Queen" call is not "on_hold"

  Scenario: Call on hold are marked as on_hold when GETTING calls
    Given there are telephony users with infos:
      | firstname | lastname | exten | context |
      | Bruce     | Wayne    | 1001  | default |
      | Clark     | Kent     | 1002  | default |
    Given "Bruce Wayne" calls "1002"
    Given "Clark Kent" answers
    When "Clark Kent" puts his call on hold
    Then "Clark Kent" call is "on_hold"
    Then "Bruce Wayne" call is not "on_hold"

  Scenario: Resumed calls are not marked as on_hold when GETTING calls
    Given there are telephony users with infos:
      | firstname | lastname | exten | context |
      | Maggie    | Greene   | 1001  | default |
      | Rick      | Grimes   | 1002  | default |
    Given "Maggie Greene" calls "1002"
    Given "Rick Grimes" answers
    When "Maggie Greene" puts his call on hold
    When "Maggie Greene" resumes his call
    Then "Maggie Greene" call is not "on_hold"
    Then "Rick Grimes" call is not "on_hold"

  Scenario: Relocate with multiple contacts
    Given there are telephony users with infos:
      | firstname | lastname | exten | context | username | password | with_token |
      | Donald    | Trump    | 1001  | default | donald   | trump    | no         |
      | Vladimir  | Poutine  | 1002  | default | vladimir | poutine  | yes        |
    Given "Vladimir Poutine" has lines:
      | name  | exten | context | with_phone |
      | line1 | 1002  | default | yes        |
      | line2 | 1002  | default | yes        |
    Given "Donald Trump" calls "1002"
    When "Vladimir Poutine" answers on its contact "1"
    When "Vladimir Poutine" relocates its call to its contact "2"
    When "Vladimir Poutine" answers on its contact "2"
    Then "Vladimir Poutine" is talking to "Donald Trump" on its contact "2"
