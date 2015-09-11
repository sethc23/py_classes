@framework
Feature: Client Computer Authentication via a Contract
    Aporo uses a Contract as one means of authenticating a Client.
    Each time a Client installs an Aporo Printer Driver ("Driver"),
    the Driver generates a random, highly-unique ID ("UID") that is saved
    on the Client's computer. A Client can authenticate a Driver
    by printing (with the Aporo Delivery Driver) a Contract approved
    by an Aporo manager. This method of authenticating a Client's
    computer involves:
        (a) a manager printing a Client Contract with
              an Aporo Printer Driver having administrative credentials,
        (b) Aporo servers processing the contents of the Contract
              and registering the Client, and
        (c) the Client printing the same Contract to Aporo from
              any computer the Client wishes to authenticate.
    .
    Scenario Outline: A manager prints a Client Contract

        Given a successful 'handshake' with Aporo servers from a(n) "<credentials>" with the credentials: "<machine_id>"
        And   a "Client Contract" for uploading to "http://printer.aporodelivery.com/" with "the same" PDF_ID
        When  the data is posted
        Then  within "<process_seconds>" seconds
        And   Celery processes the document and concludes with "add_new_vendor_info"
        And   Redis stores Celery results
        And   "<client_name>" in the Contract becomes registered
        And   the "Contract" is saved to the "<save_dir>" directory

        Examples:
        |   client_name  |   credentials  | machine_id   | process_seconds | save_dir            |
        |   Quick Bytes  |   manager      | admin1       | 5               | media/contracts/    |


    Scenario Outline: After a manager prints a Client Contract, the Client prints the same Contract

        Given a "<first_user_type>" with credentials "<first_user_creds>" prints the "<client_name>" Contract
        And   "<client_name>" in the Contract becomes registered within "<process_seconds>" seconds
        And   a "<second_user_type>" with credentials "<second_user_creds>" prints the "<client_name>" Contract
        Then  within "<process_seconds>" seconds
        And   Celery processes the document and concludes with "register_vendor"
        And   Redis stores Celery results
        And   "<client_name>" becomes associated with "<second_user_creds>"
        And   the source IP address "<known_user>" as a Known User

        Examples:
        | first_user_type | first_user_creds |   client_name  |   second_user_type | second_user_creds | process_seconds | known_user    |
        | manager         | admin1           |   Quick Bytes  |   vendor           | vendor1           | 5               | IS REGISTERED |

