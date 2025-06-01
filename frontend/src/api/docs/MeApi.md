# MeApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getUsersMe**](#getusersme) | **GET** /users/me | Read Current User|
|[**getUsersMeProfilePicture**](#getusersmeprofilepicture) | **GET** /users/me/profile-picture | Read Own Profile Picture|
|[**patchUsersMe**](#patchusersme) | **PATCH** /users/me | Update Current User|
|[**postUsersMeAskDeletion**](#postusersmeaskdeletion) | **POST** /users/me/ask-deletion | Ask User Deletion|
|[**postUsersMeProfilePicture**](#postusersmeprofilepicture) | **POST** /users/me/profile-picture | Create Current User Profile Picture|

# **getUsersMe**
> User getUsersMe()

Return `User` representation of current user  **The user must be authenticated to use this endpoint**

### Example

```typescript
import {
    MeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MeApi(configuration);

const { status, data } = await apiInstance.getUsersMe();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**User**

### Authorization

[AuthorizationCodeAuthentication](../README.md#AuthorizationCodeAuthentication)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getUsersMeProfilePicture**
> getUsersMeProfilePicture()

Get the profile picture of the authenticated user.

### Example

```typescript
import {
    MeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MeApi(configuration);

const { status, data } = await apiInstance.getUsersMeProfilePicture();
```

### Parameters
This endpoint does not have any parameters.


### Return type

void (empty response body)

### Authorization

[AuthorizationCodeAuthentication](../README.md#AuthorizationCodeAuthentication)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **patchUsersMe**
> patchUsersMe(userUpdate)

Update the current user, the request should contain a JSON with the fields to change (not necessarily all fields) and their new value  **The user must be authenticated to use this endpoint**

### Example

```typescript
import {
    MeApi,
    Configuration,
    UserUpdate
} from './api';

const configuration = new Configuration();
const apiInstance = new MeApi(configuration);

let userUpdate: UserUpdate; //

const { status, data } = await apiInstance.patchUsersMe(
    userUpdate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userUpdate** | **UserUpdate**|  | |


### Return type

void (empty response body)

### Authorization

[AuthorizationCodeAuthentication](../README.md#AuthorizationCodeAuthentication)

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **postUsersMeAskDeletion**
> postUsersMeAskDeletion()

This endpoint will ask administrators to process to the user deletion. This manual verification is needed to prevent data from being deleting for other users

### Example

```typescript
import {
    MeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MeApi(configuration);

const { status, data } = await apiInstance.postUsersMeAskDeletion();
```

### Parameters
This endpoint does not have any parameters.


### Return type

void (empty response body)

### Authorization

[AuthorizationCodeAuthentication](../README.md#AuthorizationCodeAuthentication)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: Not defined


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**204** | Successful Response |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **postUsersMeProfilePicture**
> Result postUsersMeProfilePicture()

Upload a profile picture for the current user.  **The user must be authenticated to use this endpoint**

### Example

```typescript
import {
    MeApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new MeApi(configuration);

let image: File; // (default to undefined)

const { status, data } = await apiInstance.postUsersMeProfilePicture(
    image
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **image** | [**File**] |  | defaults to undefined|


### Return type

**Result**

### Authorization

[AuthorizationCodeAuthentication](../README.md#AuthorizationCodeAuthentication)

### HTTP request headers

 - **Content-Type**: multipart/form-data
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

