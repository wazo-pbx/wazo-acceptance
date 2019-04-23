Feature: Asterisk

    Scenario: Asterisk Max File Descriptors
        Then max open file descriptors are equals to 8192

    Scenario: Asterisk Voicemail Directory
        Then directory of the Asterisk voicemail is empty

    Scenario: Sound Files Installed
        Then Asterisk sound files correctly installed

    Scenario: Asterisk Owns Dahdi
        Then Asterisk owns /dev/dadhi

    Scenario: Asterisk MOH files Permission
        Then MOH files owned by asterisk:www-data

    Scenario: Command core reload
        Asterisk command "core reload" return no error
