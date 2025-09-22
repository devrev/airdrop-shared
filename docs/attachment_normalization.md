# Attachment normalization

Attachments have a special way of normalization compared to other resources. Function for normalizing "attachments" should return an object "NormalizedAttachment" instead of "NormalizedItem".

## NormalizedAttachment

NormalizedAttachment represents the standardized structure of an attachment after normalization in the Airdrop platform. This interface defines the essential properties needed to identify and link attachments to their parent items.

### Properties

- _url_

  Required. A **string** representing the URL where the attachment can be accessed.

- _id_

  Required. A **string** that uniquely identifies the normalized attachment.

- _file_name_

  Required. A **string** representing the name of the attachment file.

- _parent_id_

  Required. A **string** identifying the parent item this attachment belongs to.

- _author_id_

  Optional. A **string** identifying the author or creator of the attachment.

- _grand_parent_id_

  Optional. A **number** identifying a higher-level parent entity, if applicable.

### Example

```typescript
export function normalizeAttachment(item: any): NormalizedAttachment {
  return {
    id: item.gid,
    url: item.download_url,
    file_name: item.name,
    parent_id: item.parent_id,
  };
}
```

### Further remarks

Note:

- In the example above, parent_id should be the ID of the resource that the attachment belongs to. For example, if we're normalizing an attachment for a task, parent_id should be the ID of the task.