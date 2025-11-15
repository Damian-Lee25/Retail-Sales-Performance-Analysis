CREATE OR REPLACE DATABASE SALES;
USE DATABASE SALES;
USE SCHEMA PUBLIC;
-- Setting up Storage Integration

CREATE OR REPLACE STORAGE INTEGRATION E2E_INT
  TYPE = EXTERNAL_STAGE
  STORAGE_PROVIDER = 'S3'
  ENABLED = TRUE
  STORAGE_AWS_ROLE_ARN = 'input_Role_ARN'
  STORAGE_ALLOWED_LOCATIONS = ('input_bucket_url');

-- Integration Details
DESC INTEGRATION E2E_INT;

-- Creating Staging Location 
CREATE OR REPLACE STAGE SALES.PUBLIC.E2E_STAGE

STORAGE_INTEGRATION = E2E_INT

URL= 'input_bucket_url';

-- If no errors appear, then stage & integration was successful
ls @SALES.PUBLIC.E2E_STAGE;
-- ------------------------------------------------------------------------------------------------------------------
-- Creating Source table that will receive data from snow pipe
CREATE OR REPLACE TABLE SALES.PUBLIC.SOURCE
(
DATE DATE,
PRODUCT STRING,
REGION STRING,
UNITS_SOLD INT,
UNIT_PRICE FLOAT,
SALES FLOAT
);

-- Creating a snowpipe to extract data from s3 bucket
CREATE OR REPLACE PIPE SALES.PUBLIC.E2E_PIPE 

AUTO_INGEST = TRUE AS

COPY INTO SALES.PUBLIC.SOURCE
FROM 
(
SELECT
    $1 AS DATE,
    $2 AS PRODUCT,
    $3 AS REGION,
    $4 AS UNITS_SOLD,
    $5 AS UNIT_PRICE,
    $6 AS SALES
FROM @SALES.PUBLIC.E2E_STAGE)

FILE_FORMAT = (TYPE='CSV' FIELD_OPTIONALLY_ENCLOSED_BY='"' SKIP_HEADER=1)


-- Confirming snowpipe was estblished successfully
SELECT SYSTEM$PIPE_STATUS('SALES.PUBLIC.E2E_PIPE');


-- Configure Event Notification 
SHOW PIPES; -- COPY arn within the notification_channel. Then create event inside of s3 bucket