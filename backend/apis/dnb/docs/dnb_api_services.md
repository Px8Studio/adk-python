# DNB API Services

## DNB Echo API

### Description
This API can be used to make test calls.

### API Resources
- **API Definition**: [View specification]
- **Changelog**: [View changes]

---

## Endpoints

### Retrieve 'Hello World'

**Method**: `GET`

**Description**: A demonstration of a GET call.

**Endpoint**:
```
https://api.dnb.nl/echo-api/helloworld
```

**Response**: `200 OK`

Returns in all cases.

**Content-Type**: `application/json`

**Response Example**:
```json
{
    "helloWorld": "DNB API Services"
}
```


Public Register

v1

API definition
Changelog
Description: The public register contains publications of organizations that are able to provide financial services. Search here if for example a bank has a license. Or a crypto company has been registered. More information can be found at https://www.dnb.nl/en/public-register.


DNB Statistics API

v2024100101

API definition
Changelog
Description: At DNB we provide statistical data on the Dutch financial sector and the Dutch balance of payments. This data enables policy makers, researchers and other interested parties to monitor developments and advance the achievement of societal goals. This API provides statistical data that has been published on the DNB website. The published statistics are compiled in accordance with our legal statistical task, or are based on supervisory information.

Not all the datasets on the 'data search' page of the DNB website are available via the DNB Statistics API yet. User requests regarding the availability of datasets can be sent to stat-info@dnb.nl. More information can be found on this page of the DNB website.