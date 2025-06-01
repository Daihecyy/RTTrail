# User

Schema for user\'s model similar to user table in database

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**id** | **string** |  | [default to undefined]
**account_type** | [**AccountType**](AccountType.md) |  | [default to undefined]
**is_active** | **boolean** |  | [default to undefined]
**email** | **string** |  | [default to undefined]
**created_on** | **string** |  | [optional] [default to undefined]

## Example

```typescript
import { User } from './api';

const instance: User = {
    name,
    id,
    account_type,
    is_active,
    email,
    created_on,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
