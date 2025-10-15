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