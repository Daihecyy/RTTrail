# UserSimple

Simplified schema for user\'s model, used when getting all users

## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**name** | **string** |  | [default to undefined]
**id** | **string** |  | [default to undefined]
**account_type** | [**AccountType**](AccountType.md) |  | [default to undefined]
**is_active** | **boolean** |  | [default to undefined]

## Example

```typescript
import { UserSimple } from './api';

const instance: UserSimple = {
    name,
    id,
    account_type,
    is_active,
};
```

[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)
