# UsersApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getUsers**](#getusers) | **GET** /users | Read Users|
|[**getUsersAccountTypes**](#getusersaccounttypes) | **GET** /users/account-types | Get Account Types|
|[**getUsersCount**](#getuserscount) | **GET** /users/count | Count Users|
|[**getUsersSearch**](#getuserssearch) | **GET** /users/search | Search Users|
|[**getUsersuserId**](#getusersuserid) | **GET** /users/{user_id} | Read User|
|[**getUsersuserIdProfilePicture**](#getusersuseridprofilepicture) | **GET** /users/{user_id}/profile-picture | Read User Profile Picture|
|[**patchUsersuserId**](#patchusersuserid) | **PATCH** /users/{user_id} | Update User|
|[**postUsersRegister**](#postusersregister) | **POST** /users/register | User Register|

# **getUsers**
> Array<UserSimple> getUsers()

Return all users from database as a list of `UserSimple`  **This endpoint is only usable by administrators**

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let accountTypes: Array<AccountType>; // (optional) (default to undefined)

const { status, data } = await apiInstance.getUsers(
    accountTypes
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **accountTypes** | **Array&lt;AccountType&gt;** |  | (optional) defaults to undefined|


### Return type

**Array<UserSimple>**

### Authorization

[AuthorizationCodeAuthentication](../README.md#AuthorizationCodeAuthentication)

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getUsersAccountTypes**
> Array<AccountType> getUsersAccountTypes()

Return all account types hardcoded in the system

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

const { status, data } = await apiInstance.getUsersAccountTypes();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**Array<AccountType>**

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

# **getUsersCount**
> number getUsersCount()

Return the number of users in the database  **This endpoint is only usable by administrators**

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

const { status, data } = await apiInstance.getUsersCount();
```

### Parameters
This endpoint does not have any parameters.


### Return type

**number**

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

# **getUsersSearch**
> Array<UserSimple> getUsersSearch()

Search for a user using Jaro_Winkler distance algorithm. The `query` will be compared against users name, firstname and nickname. Assume that `query` is the beginning of a name, so we can capitalize words to improve results.  **The user must be authenticated to use this endpoint**

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let query: string; // (default to undefined)
let includedAccountTypes: Array<AccountType>; // (optional) (default to undefined)
let excludedAccountTypes: Array<AccountType>; // (optional) (default to undefined)
let accountType: AccountType; // (optional) (default to undefined)

const { status, data } = await apiInstance.getUsersSearch(
    query,
    includedAccountTypes,
    excludedAccountTypes,
    accountType
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **query** | [**string**] |  | defaults to undefined|
| **includedAccountTypes** | **Array&lt;AccountType&gt;** |  | (optional) defaults to undefined|
| **excludedAccountTypes** | **Array&lt;AccountType&gt;** |  | (optional) defaults to undefined|
| **accountType** | **AccountType** |  | (optional) defaults to undefined|


### Return type

**Array<UserSimple>**

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

# **getUsersuserId**
> User getUsersuserId()

Return `User` representation of user with id `user_id`  **The user must be authenticated to use this endpoint**

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: string; // (default to undefined)

const { status, data } = await apiInstance.getUsersuserId(
    userId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**string**] |  | defaults to undefined|


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
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **getUsersuserIdProfilePicture**
> getUsersuserIdProfilePicture()

Get the profile picture of an user.  Unauthenticated users can use this endpoint (needed for some OIDC services)

### Example

```typescript
import {
    UsersApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: string; // (default to undefined)

const { status, data } = await apiInstance.getUsersuserIdProfilePicture(
    userId
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userId** | [**string**] |  | defaults to undefined|


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

# **patchUsersuserId**
> patchUsersuserId(userUpdateAdmin)

Update an user, the request should contain a JSON with the fields to change (not necessarily all fields) and their new value  **This endpoint is only usable by administrators**

### Example

```typescript
import {
    UsersApi,
    Configuration,
    UserUpdateAdmin
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userId: string; // (default to undefined)
let userUpdateAdmin: UserUpdateAdmin; //

const { status, data } = await apiInstance.patchUsersuserId(
    userId,
    userUpdateAdmin
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userUpdateAdmin** | **UserUpdateAdmin**|  | |
| **userId** | [**string**] |  | defaults to undefined|


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

# **postUsersRegister**
> Result postUsersRegister(userRegister)

Register a user

### Example

```typescript
import {
    UsersApi,
    Configuration,
    UserRegister
} from './api';

const configuration = new Configuration();
const apiInstance = new UsersApi(configuration);

let userRegister: UserRegister; //

const { status, data } = await apiInstance.postUsersRegister(
    userRegister
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userRegister** | **UserRegister**|  | |


### Return type

**Result**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**201** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

