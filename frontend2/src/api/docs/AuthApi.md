# AuthApi

All URIs are relative to *http://localhost*

|Method | HTTP request | Description|
|------------- | ------------- | -------------|
|[**getLoginMigrateMailConfirm**](#getloginmigratemailconfirm) | **GET** /login/migrate-mail-confirm | Migrate Mail Confirm|
|[**postLoginAccessToken**](#postloginaccesstoken) | **POST** /login/access-token | Login For Access Token|
|[**postLoginActivate**](#postloginactivate) | **POST** /login/activate | Activate User|
|[**postLoginChangePassword**](#postloginchangepassword) | **POST** /login/change-password | Change Password|
|[**postLoginMigrateMail**](#postloginmigratemail) | **POST** /login/migrate-mail | Migrate Mail|
|[**postLoginRecover**](#postloginrecover) | **POST** /login/recover | Recover User|
|[**postLoginResetPassword**](#postloginresetpassword) | **POST** /login/reset-password | Reset Password|
|[**postLoginTestToken**](#postlogintesttoken) | **POST** /login/test-token | Test Token|

# **getLoginMigrateMailConfirm**
> any getLoginMigrateMailConfirm()

This endpoint will update the user new email address. The user will need to use the confirmation code sent by the `/users/migrate-mail` endpoint.

### Example

```typescript
import {
    AuthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let token: string; // (default to undefined)

const { status, data } = await apiInstance.getLoginMigrateMailConfirm(
    token
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **token** | [**string**] |  | defaults to undefined|


### Return type

**any**

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

# **postLoginAccessToken**
> AccessToken postLoginAccessToken()

Ask for a JWT access token using oauth password flow.  *username* and *password* must be provided  Note: the request body needs to use **form-data** and not json.

### Example

```typescript
import {
    AuthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let username: string; // (default to undefined)
let password: string; // (default to undefined)
let grantType: string; // (optional) (default to undefined)
let scope: string; // (optional) (default to '')
let clientId: string; // (optional) (default to undefined)
let clientSecret: string; // (optional) (default to undefined)

const { status, data } = await apiInstance.postLoginAccessToken(
    username,
    password,
    grantType,
    scope,
    clientId,
    clientSecret
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **username** | [**string**] |  | defaults to undefined|
| **password** | [**string**] |  | defaults to undefined|
| **grantType** | [**string**] |  | (optional) defaults to undefined|
| **scope** | [**string**] |  | (optional) defaults to ''|
| **clientId** | [**string**] |  | (optional) defaults to undefined|
| **clientSecret** | [**string**] |  | (optional) defaults to undefined|


### Return type

**AccessToken**

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/x-www-form-urlencoded
 - **Accept**: application/json


### HTTP response details
| Status code | Description | Response headers |
|-------------|-------------|------------------|
|**200** | Successful Response |  -  |
|**422** | Validation Error |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **postLoginActivate**
> Result postLoginActivate(userActivate)

Activate the previously created account.  **token**: the activation token sent by email to the user

### Example

```typescript
import {
    AuthApi,
    Configuration,
    UserActivate
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let userActivate: UserActivate; //

const { status, data } = await apiInstance.postLoginActivate(
    userActivate
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **userActivate** | **UserActivate**|  | |


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

# **postLoginChangePassword**
> Result postLoginChangePassword(changePassword)

Change a user password.  This endpoint will check the **old_password**, see also the `/users/reset-password` endpoint if the user forgot their password.

### Example

```typescript
import {
    AuthApi,
    Configuration,
    ChangePassword
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let changePassword: ChangePassword; //

const { status, data } = await apiInstance.postLoginChangePassword(
    changePassword
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **changePassword** | **ChangePassword**|  | |


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

# **postLoginMigrateMail**
> postLoginMigrateMail(mailMigration)

This endpoint will send a confirmation code to the user\'s new email address. He will need to use this code to confirm the change with `/users/confirm-mail-migration` endpoint.

### Example

```typescript
import {
    AuthApi,
    Configuration,
    MailMigration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let mailMigration: MailMigration; //

const { status, data } = await apiInstance.postLoginMigrateMail(
    mailMigration
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **mailMigration** | **MailMigration**|  | |


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

# **postLoginRecover**
> Result postLoginRecover(emailRecover)

Allow a user to start a password reset process.  If the provided **email** corresponds to an existing account, a password reset token will be sent. Using this token, the password can be changed with `/users/reset-password` endpoint

### Example

```typescript
import {
    AuthApi,
    Configuration,
    EmailRecover
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let emailRecover: EmailRecover; //

const { status, data } = await apiInstance.postLoginRecover(
    emailRecover
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **emailRecover** | **EmailRecover**|  | |


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

# **postLoginResetPassword**
> Result postLoginResetPassword(resetPassword)

Reset the user password, using a **reset_token** provided by `/users/recover` endpoint.

### Example

```typescript
import {
    AuthApi,
    Configuration,
    ResetPassword
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let resetPassword: ResetPassword; //

const { status, data } = await apiInstance.postLoginResetPassword(
    resetPassword
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **resetPassword** | **ResetPassword**|  | |


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

# **postLoginTestToken**
> User postLoginTestToken()

Test access token

### Example

```typescript
import {
    AuthApi,
    Configuration
} from './api';

const configuration = new Configuration();
const apiInstance = new AuthApi(configuration);

let accountType: AccountType; // (optional) (default to undefined)

const { status, data } = await apiInstance.postLoginTestToken(
    accountType
);
```

### Parameters

|Name | Type | Description  | Notes|
|------------- | ------------- | ------------- | -------------|
| **accountType** | **AccountType** |  | (optional) defaults to undefined|


### Return type

**User**

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

