# CoreApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getFaviconIco**](#getfaviconico) | **GET** /favicon.ico | Get Favicon|
|[**getInformation**](#getinformation) | **GET** /information | Read Information|
|[**getPrivacy**](#getprivacy) | **GET** /privacy | Read Privacy|
|[**getRobotsTxt**](#getrobotstxt) | **GET** /robots.txt | Read Robots Txt|
|[**getSecurityTxt**](#getsecuritytxt) | **GET** /security.txt | Read Security Txt|
|[**getStylefileCss**](#getstylefilecss) | **GET** /style/{file}.css | Get Style File|
|[**getSupport**](#getsupport) | **GET** /support | Read Support|
|[**getTermsAndConditions**](#gettermsandconditions) | **GET** /terms-and-conditions | Read Terms And Conditions|
|[**getWellKnownSecurityTxt**](#getwellknownsecuritytxt) | **GET** /.well-known/security.txt | Read Wellknown Security Txt|

# **getFaviconIco**
> getFaviconIco()


### Example

```typescript
import {
    CoreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CoreApi(configuration);

const { status, data } = await apiInstance.getFaviconIco();
```

### Parameters
This endpoint does not have any parameters.


### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getInformation**
> CoreInformation getInformation()

Return information about rttrail. This endpoint can be used to check if the API is up.

### Example

```typescript
import {
    CoreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CoreApi(configuration);

const { status, data } = await apiInstance.getInformation();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**CoreInformation**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getPrivacy**
> getPrivacy()

Return RTTrail privacy

### Example

```typescript
import {
    CoreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CoreApi(configuration);

const { status, data } = await apiInstance.getPrivacy();
```

### Parameters
This endpoint does not have any parameters.


### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getRobotsTxt**
> getRobotsTxt()

Return RTTrail robots.txt file

### Example

```typescript
import {
    CoreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CoreApi(configuration);

const { status, data } = await apiInstance.getRobotsTxt();
```

### Parameters
This endpoint does not have any parameters.


### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSecurityTxt**
> getSecurityTxt()

Return RTTrail security.txt file

### Example

```typescript
import {
    CoreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CoreApi(configuration);

const { status, data } = await apiInstance.getSecurityTxt();
```

### Parameters
This endpoint does not have any parameters.


### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getStylefileCss**
> getStylefileCss()

Return a style file from the assets folder

### Example

```typescript
import {
    CoreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CoreApi(configuration);

let file: string; // (default to undefined)

const { status, data } = await apiInstance.getStylefileCss(
    file
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **file** | [**string**] |  | defaults to undefined|


### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getSupport**
> getSupport()

Return RTTrail terms and conditions pages

### Example

```typescript
import {
    CoreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CoreApi(configuration);

const { status, data } = await apiInstance.getSupport();
```

### Parameters
This endpoint does not have any parameters.


### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getTermsAndConditions**
> getTermsAndConditions()

Return RTTrail terms and conditions pages

### Example

```typescript
import {
    CoreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CoreApi(configuration);

const { status, data } = await apiInstance.getTermsAndConditions();
```

### Parameters
This endpoint does not have any parameters.


### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getWellKnownSecurityTxt**
> getWellKnownSecurityTxt()

Return RTTrail security.txt file

### Example

```typescript
import {
    CoreApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new CoreApi(configuration);

const { status, data } = await apiInstance.getWellKnownSecurityTxt();
```

### Parameters
This endpoint does not have any parameters.


### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

