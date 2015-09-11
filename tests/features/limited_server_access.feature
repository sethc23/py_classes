
@framework
Feature: Limited Server Access

    Scenario Outline: Check In Requests & Document Post Attempts Made to Aporo

        Given data for posting to "http://printer.aporodelivery.com/api/check/"
        When  the post request is from a(n) "<user_type>" with the credentials: "<machine_id>"
        And   the request format is "<request_format>"
        And   the data is posted
        Then  Aporo will return: "<chk_in_result>"
        And   (if not FORBIDDEN) Aporo creates a DB entry and returns an Order Tag, a Post Url, and QR code information
        And   upon a second post to "http://printer.aporodelivery.com/" with a "<doc_type>" and with "<paired>" PDF_ID
        And   Celery processes the document and concludes with "<celery_result>"
        And   Redis stores Celery results
        And   Aporo will return: "<doc_result>"

        Examples:
        | request_format  |  user_type  | machine_id |  chk_in_result | doc_type | paired       | doc_result | celery_result       |
        | valid           |  vendor     | vendor1    |  CREATED       | pdf      | the same     | OK         | read_order_into_db  |
        | valid           |  manager    | admin1     |  CREATED       | pdf      | the same     | OK         | admin_req           |
        | valid           |  unknown    | unknown    |  CREATED       | pdf      | the same     | OK         | unknown_req         |
        | invalid         |  vendor     | vendor1    |  FORBIDDEN     | pdf      | the same     | FORBIDDEN  | None                |
        | invalid         |  manager    | admin1     |  FORBIDDEN     | pdf      | the same     | FORBIDDEN  | None                |
        | invalid         |  unknown    | unknown    |  FORBIDDEN     | pdf      | the same     | FORBIDDEN  | None                |

        | invalid         |  vendor     | None       |  FORBIDDEN     | pdf      | the same     | FORBIDDEN  | None                |
        | invalid         |  manager    | None       |  FORBIDDEN     | pdf      | the same     | FORBIDDEN  | None                |
        | invalid         |  unknown    | None       |  FORBIDDEN     | pdf      | the same     | FORBIDDEN  | None                |

        | valid           |  vendor     | vendor1    |  CREATED       | txt      | the same     | FORBIDDEN  | None                |
        | valid           |  manager    | admin1     |  CREATED       | txt      | the same     | FORBIDDEN  | None                |
        | valid           |  unknown    | unknown    |  CREATED       | txt      | the same     | FORBIDDEN  | None                |
        | invalid         |  vendor     | vendor1    |  FORBIDDEN     | txt      | the same     | FORBIDDEN  | None                |
        | invalid         |  unknown    | None       |  FORBIDDEN     | txt      | the same     | FORBIDDEN  | None                |

        | valid           |  vendor     | vendor1    |  CREATED       | pdf      | a different  | FORBIDDEN  | None                |
        | valid           |  manager    | admin1     |  CREATED       | pdf      | a different  | FORBIDDEN  | None                |
        | valid           |  unknown    | unknown    |  CREATED       | pdf      | a different  | FORBIDDEN  | None                |
        | invalid         |  vendor     | vendor1    |  FORBIDDEN     | pdf      | a different  | FORBIDDEN  | None                |
        | invalid         |  unknown    | None       |  FORBIDDEN     | pdf      | a different  | FORBIDDEN  | None                |


    Scenario Outline: Blacklisting an IP Address

        Given a new IP address
        And   data for posting to "http://printer.aporodelivery.com/api/check/"
        When  the post request is from a(n) "<credentials>" with the credentials: "<machine_id>"
        And   the request format is "<request_format>"
        And   the data is posted
        And   the date is posted "<post_count>" more times (with a different UUID)
        Then  the source IP is blacklisted

        Examples:
        | request_format | credentials | machine_id | post_count |
        | valid          | unknown     | unknown    | 4          |
        | invalid        | unknown     | None       | 2          |
