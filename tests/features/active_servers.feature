
@production
Feature: Verify Online Presence
    .


Scenario: Confirm Testing Is Not Internally Directing Requests

    Given We want to verify the online presence of the domain "printer.aporodelivery.com"
    Then  "/etc/hosts" should not internally direct requests

Scenario Outline: Confirm All Servers and Webpages are live

    Given "<page_title>" is live and we access "<webpage>"
    Then  the page should start loading within "<response_time>" seconds
    And   the response message should be "OK" with response code "200"

    Examples:
        | page_title                | webpage                                   | response_time |
        | Aporo                     | http://www.aporodelivery.com              | 5.0           |
        | GnamGnam Home Page        | http://www.gnamgnamapp.com/               | 5.0           |
        | GnamGnam Join Us Page     | http://www.gnamgnamapp.com/join/          | 5.0           |
        | GnamGnam Admin Page       | http://admin.gnamgnamapp.com/login        | 5.0           |

Scenario Outline: Confirm Printer Driver Available for Fast Download

    Given "<page_title>" is live and we access "<webpage>"
    Then  the page should start loading within "<resp_time>" seconds
    And   the response message should be "OK" with response code "200"
    And   the download should finish within "<dl_time>" seconds

    Examples:
        | page_title  | webpage                                                                                      | resp_time | dl_time |
        | Aporo       | http://printer.aporodelivery.com/static/downloads/AporoDelivery_Setup.exe?email_notice=false | 5.0       | 10      |

Scenario Outline: Confirm GnamGnamApp.com is Unchanged

    Given "<page_title>" is live and we access "<webpage>"
    Then  the page should start loading within "<response_time>" seconds
    And   the response message should be "OK" with response code "200"
    And   the webpage should be unchanged

    Examples:
        | page_title                | webpage                                   | response_time |
        | GnamGnam Home Page        | http://www.gnamgnamapp.com/               | 5.0           |

Scenario Outline: Confirm GnamGnam Admin Console is Accessible

    Given "GnamGnam Admin Console" is live and we access "http://admin.gnamgnamapp.com/"
    When  "<company>" logs in with user: "<username>" and pw: "<pw>"
    Then  the page will contain "<company>"
    And   the page will contain "Sign out"

    Examples:
        | company            | username  | pw     |
        | Aporo Delivery     | aporo     | 123456 |