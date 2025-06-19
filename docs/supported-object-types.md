# Supported DevRev object types for Airdrop

This document contains the list of all DevRev object types that are supported for Airdrop.

## Key capabilities

| Capability | Description |
|-------|-------------|
| Can Load | Indicates that the object type can be loaded into the DevRev with Airdrop. |
| Can Extract | Indicates that the object type can be synced out to external systems. |
| Can Subtype | Indicates that the object type supports [subtype](https://developer.devrev.ai/beta/guides/object-customization#subtype) creation. |
| Can App Fragment | Indicates that the object type supports application fragments. |

## new_custom_object

**Resource Type:** `custom_object`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `leaf_type` | get_leaf |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `title` | text |  | Title of the custom object |


---

## account

**Resource Type:** `account`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `address` | struct |  | Address of the Organization. |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `description` | rich_text |  | Description of the corresponding Account. |
| `display_name` | text | ✔︎ | Name of the Organization. |
| `environment` | enum |  | The environment of the Org. Defaults to 'production' if not specified. |
| `owned_by` | reference (collection) -> [#category:user] | ✔︎ | List of Dev user IDs owning this Account. |
| `phone_number` | struct (collection) |  | Phone numbers of the Organization. |
| `phone_numbers` | text (collection) |  | Phone numbers of the Organization. |
| `state` | enum | ✔︎ | State of the Organization. |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with an object. |
| `websites` | text (collection) |  | Websites |

#### Enum values

**environment**

| Value | Name | Description |
|-----|------|-------------|
| `PRODUCTION` | PRODUCTION | - |
| `STAGING` | STAGING | - |
| `TEST` | TEST | - |

**state**

| Value | Name | Description |
|-----|------|-------------|
| `ACTIVE` | ACTIVE | - |
| `INACTIVE` | INACTIVE | - |
| `LOCKED` | LOCKED | - |

### Structs

#### postal_address

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `country` | text |  | Country name component. |
| `formatted` | text |  | Full mailing address, formatted for display or use on a mailing label. |
| `locality` | text |  | Town, city. |
| `postal_code` | text |  | Zip code of the address. |
| `region` | text |  | State, province, prefecture, or region component. |
| `street_address` | text |  | Full street address component. |


## airdrop_authorization_policy

**Resource Type:** `airdrop_authorization_policy`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `groups` | reference (collection) -> [#record:airdrop_platform_group #record:group] |  | Groups this role applies to. |
| `privileges` | enum (collection) |  | Privileges the role provides. |
| `targets` | type_key (collection) | ✔︎ | Target object types the role applies to. |
| `users` | reference (collection) -> [#record:devu #record:revu] |  | Users this role applies to. |

#### Enum values

**privileges**

| Value | Name | Description |
|-----|------|-------------|
| `create` | create | - |
| `delete` | delete | - |
| `read` | read | - |
| `update` | update | - |


## airdrop_platform_group

**Resource Type:** `airdrop_platform_group`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `key` | enum | ✔︎ | Key of the platform provided group. |

#### Enum values

**key**

| Value | Name | Description |
|-----|------|-------------|
| `dev_users` | Dev users | "Dynamic dev users group created by DevRev" |
| `none` | No group | "No group selected" |
| `rev_users` | Rev users | "Dynamic rev users group created by DevRev" |


## article

**Resource Type:** `article`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_level` | enum |  | Default access level for the object. |
| `aliases` | text (collection) |  | Aliases for the URL of the article. |
| `applies_to_part_ids` | reference (collection) -> [#category:part] |  | Parts relevant to the article. |
| `authored_by_ids` | reference (collection) -> [#category:user] |  | Users that authored the article. |
| `content` | rich_text |  |  |
| `content_filename` | text |  |  |
| `content_filetype` | enum |  |  |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `description` | rich_text |  | Description of the article. |
| `extracted_plain_text` | text |  | Extracted Plain Text |
| `item_url_field` | text |  | Link to the item in the origin system |
| `language` | text |  | Language of the article for i18n support. |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `num_downvotes` | int |  | Number of downvotes on the article. |
| `num_upvotes` | int |  | Number of upvotes on the article. |
| `owned_by_ids` | reference (collection) -> [#category:user] | ✔︎ | Users that own the article. |
| `parent` | reference -> [#record:directory] |  | Parent of the article. |
| `primary_article_id` | reference -> [#record:article] |  | Primary article ID |
| `published_date` | timestamp |  | Timestamp when the article was published. |
| `rank` | text |  | Rank of the article. |
| `resource` | struct |  | Resource of the article. |
| `scope` | enum |  | Scope of the article. |
| `shared_with` | permission (collection) |  | The list of Rev user, groups and dynamic groups with whom the article is shared and the corresponding roles. |
| `status` | enum |  | Status of the article. |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the article. |
| `title` | text | ✔︎ | Title of the article. |
| `type` | enum |  | Type of the article. |
| `visible_to` | enum |  |  |

#### Enum values

**access_level**

| Value | Name | Description |
|-----|------|-------------|
| `EXTERNAL` | - | - |
| `INTERNAL` | - | - |
| `PRIVATE` | - | - |
| `PUBLIC` | - | - |
| `RESTRICTED` | - | - |

**content_filetype**

| Value | Name | Description |
|-----|------|-------------|
| `application/json` | - | - |
| `devrev/rt` | - | - |
| `image/avif` | - | - |
| `image/gif` | - | - |
| `image/jpeg` | - | - |
| `image/png` | - | - |
| `image/svg+xml` | - | - |
| `image/webp` | - | - |
| `paligo/html` | - | - |
| `text/css; charset=utf-8` | - | - |
| `text/html; charset=utf-8` | - | - |
| `text/javascript; charset=utf-8` | - | - |
| `text/plain` | - | - |
| `text/xml; charset=utf-8` | - | - |

**scope**

| Value | Name | Description |
|-----|------|-------------|
| `1` | internal | - |
| `2` | external | - |

**status**

| Value | Name | Description |
|-----|------|-------------|
| `archived` | archived | - |
| `draft` | draft | - |
| `published` | published | - |
| `review_needed` | review_needed | - |

**type**

| Value | Name | Description |
|-----|------|-------------|
| `article` | article | - |
| `content_block` | content_block | - |

**visible_to**

| Value | Name | Description |
|-----|------|-------------|
| `customer_admins` | - | - |
| `customers` | - | - |
| `verified_customers` | - | - |

### Structs

#### resource

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `artifact_ids` | reference |  | Artifacts of the resource (relevant only for type artifact). |
| `artifacts` | reference |  | Artifacts of the resource (relevant only for type artifact). |
| `content_blocks` | reference |  | Content blocks used in the article (relevant only for devrev/rt articles). |
| `published_version` | text |  | The published version of the resource |
| `type` | enum |  | The type of resource. |
| `url` | text |  | URL of the resource (relevant only for type url). |


## capability

**Resource Type:** `part`, `capability`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `part_type` | "capability" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `delivered_as` | enum (collection) |  | Methods the product can be delivered as |
| `description` | rich_text |  | Description of the part |
| `docs` | struct (collection) |  | Docs associated with the part |
| `fulfilled_by` | reference (collection) -> [#category:part] |  | IDs of the runnables that fulfill this capability |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `name` | text | ✔︎ | Name of the part |
| `owned_by_ids` | reference (collection) -> [#record:devu] | ✔︎ | User IDs of the users that own the part |
| `parent_part` | reference -> [#category:part] | ✔︎ | Parent of this part |
| `pm_owner_id` | reference -> [#record:devu] |  | User ID of the PM owner of the part |
| `ref_url` | text |  | URL to the part details (git url, website, etc.) |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |

#### Enum values

**delivered_as**

| Value | Name | Description |
|-----|------|-------------|
| `goods` | goods | - |
| `service` | service | - |
| `software` | software | - |


## channel

**Resource Type:** `chat`, `channel`

**Capabilities:** Can Load

### Fixed fields

| Field | Value |
|-------|-------|
| `chat_type` | "channel" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_level` | enum |  | The access level for the channel. |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `name` | text |  | The name of the channel. If provided, this will be unique across all channels in the Dev org. It's case insensitive and must contain the characters [A-Za-z0-9_-]. |
| `title` | text |  | The title given to the chat. |

#### Enum values

**access_level**

| Value | Name | Description |
|-----|------|-------------|
| `EXTERNAL` | EXTERNAL | - |
| `INTERNAL` | INTERNAL | - |
| `PRIVATE` | PRIVATE | - |
| `PUBLIC` | PUBLIC | - |
| `RESTRICTED` | RESTRICTED | - |
| `UNKNOWN` | UNKNOWN | - |


## comment

**Resource Type:** `comment`

**Capabilities:** Can Extract, Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `body` | rich_text | ✔︎ | Comment body |
| `created_by_id` | reference -> [#category:user] | ✔︎ | User ID of the user that created the object |
| `creator_display_name` | text |  | Creator display name |
| `external_ref` | text |  | The external reference to associate with the entry. This must be unique across the entry's siblings, i.e. all children of its parent. |
| `grandparent_object_id` | reference -> [#category:chat #category:custom_object #category:part #category:work #record:account #record:conversation #record:incident #record:revu] |  | The object this relates to |
| `grandparent_object_type` | text |  | The object type this relates to |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] | ✔︎ | User ID of the user that last modified the object |
| `parent_object_id` | reference -> [#category:chat #category:custom_object #category:part #category:work #record:account #record:comment #record:conversation #record:incident #record:revu] | ✔︎ | The object this relates to |
| `parent_object_type` | text |  | The object type this relates to |
| `visibility` | enum |  | Visibility of the comment |

#### Enum values

**visibility**

| Value | Name | Description |
|-----|------|-------------|
| `Visibility_EXTERNAL` | Visibility_EXTERNAL | - |
| `Visibility_INTERNAL` | Visibility_INTERNAL | - |
| `Visibility_PRIVATE` | Visibility_PRIVATE | - |
| `Visibility_PUBLIC` | Visibility_PUBLIC | - |


## component

**Resource Type:** `part`, `component`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `part_type` | "component" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `delivered_as` | enum (collection) |  | Methods the product can be delivered as |
| `description` | rich_text |  | Description of the part |
| `development_owner_id` | reference -> [#record:devu] |  | User ID of the development owner of the part |
| `docs` | struct (collection) |  | Docs associated with the part |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `name` | text | ✔︎ | Name of the part |
| `owned_by_ids` | reference (collection) -> [#record:devu] | ✔︎ | User IDs of the users that own the part |
| `parent_part` | reference -> [#category:part] |  | Parent of this part |
| `pm_owner_id` | reference -> [#record:devu] |  | User ID of the PM owner of the part |
| `qa_owner_id` | reference -> [#record:devu] |  | User ID of the QA owner of the part |
| `ref_url` | text |  | URL to the part details (git url, website, etc.) |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |

#### Enum values

**delivered_as**

| Value | Name | Description |
|-----|------|-------------|
| `goods` | goods | - |
| `service` | service | - |
| `software` | software | - |


## conversation

**Resource Type:** `conversation`

**Capabilities:** Can Load, Can Subtype

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `applies_to_part_ids` | reference (collection) -> [#category:part] |  | Details of the parts relevant to the conversation. |
| `broadcast_channels` | text (collection) |  | Active channels for the conversation |
| `channels` | reference (collection) -> [#record:external_communication_channel] |  | Channel IDs of the conversation |
| `conversation_type` | enum | ✔︎ | A type of object used to track conversations |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `description` | rich_text |  | Description of the conversation object |
| `first_response_time` | timestamp |  | Timestamp to track the first response from Dev |
| `first_unreplied_rev_message_date` | timestamp |  | First unreplied customer message's timestamp |
| `group` | reference -> [#record:group] |  | Group that owns the conversation |
| `is_creator_verified` | bool |  | Whether the conversation is created by verified user. |
| `is_spam` | bool |  | Whether the conversation is spam. |
| `last_external_message_date` | timestamp |  | Timestamp of the last message in external discussion |
| `last_external_message_id` | reference -> [#record:comment] |  | ID of the last message in external discussion. |
| `last_internal_message_date` | timestamp |  | Timestamp of the last message in internal discussions. |
| `last_internal_message_id` | reference -> [#record:comment] |  | ID of the last message in internal discussion. |
| `last_message_id` | reference -> [#record:comment] |  | ID of the last message on the object. |
| `last_message_timestamp` | timestamp |  | Timestamp of the last message in the conversation |
| `member_ids` | reference (collection) -> [#category:user] | ✔︎ | User IDs of the users in the conversation |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `owned_by_ids` | reference (collection) -> [#category:user] |  | Users that own the conversation |
| `participant_oids` | reference (collection) -> [#record:account #record:revo] |  | Globally unique IDs of participating orgs |
| `participant_uids` | reference (collection) -> [#category:user] |  | Globally unique ID of DevRev rev users |
| `priority` | enum |  | Priority of the conversation |
| `sla_id` | reference -> [#record:sla] |  | The ID of the SLA applying to this object, controlling how the SLA tracking service treats it. |
| `sla_tracker_id` | reference -> [#record:sla_tracker] |  | The ID of the SLA tracker applied to this object, which is used to track the SLA metrics. |
| `source_channel` | text |  | Source channel for the conversation |
| `source_channel_v2` | reference -> [#record:external_communication_channel] |  | Source channel ID of the conversation |
| `stage` | enum |  | Stage of the conversation |
| `started_by_id` | reference -> [#category:user] |  | User that started the conversation |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |
| `title` | text |  | Title of the conversation object |
| `turing_active` | bool |  | Whether Turing is active on the conversation. Will be true when Turing is active and false when it stops responding or when a dev user responds to the conversation. |
| `user_sessions` | reference (collection) -> [#record:user_session] |  | User sessions associated with the conversation. |

#### Enum values

**conversation_type**

| Value | Name | Description |
|-----|------|-------------|
| `support` | Support | - |

**priority**

| Value | Name | Description |
|-----|------|-------------|
| `P0` | P0 | - |
| `P1` | P1 | - |
| `P2` | P2 | - |

**stage**

| Value | Name | Description |
|-----|------|-------------|
| `archived` | Archived | - |
| `hold` | Hold | - |
| `needs_response` | Needs Response | - |
| `new` | New | - |
| `resolved` | Resolved | - |
| `suspended` | Suspended | - |
| `waiting_on_user` | Waiting On User | - |


## custom_link

**Resource Type:** `link`

**Capabilities:** Can Extract, Can Load

### Fixed fields

| Field | Value |
|-------|-------|
| `link_type` | "custom_link" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `link_type_id` | enum | ✔︎ | Link Type |
| `source_id` | reference -> [#category:custom_object #record:account #record:capability #record:enhancement #record:feature #record:incident #record:issue #record:opportunity #record:product #record:project #record:revu #record:task #record:ticket] | ✔︎ | Source object ID |
| `target_id` | reference -> [#category:custom_object #record:account #record:capability #record:enhancement #record:feature #record:incident #record:issue #record:opportunity #record:product #record:project #record:revu #record:task #record:ticket] | ✔︎ | Target object ID |

#### Enum values

**link_type_id**

| Value | Name | Description |
|-----|------|-------------|
| `is_dependent_on` | Is Dependent On | - |
| `is_duplicate_of` | Is Duplicate Of | - |
| `is_parent_of` | Is Parent Of | - |
| `is_related_to` | Is Related To | - |


## custom_part

**Resource Type:** `part`, `custom_part`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `part_type` | "custom_part" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `delivered_as` | enum (collection) |  | Methods the product can be delivered as |
| `description` | rich_text |  | Description of the part |
| `docs` | struct (collection) |  | Docs associated with the part |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `name` | text | ✔︎ | Name of the part |
| `owned_by_ids` | reference (collection) -> [#record:devu] | ✔︎ | User IDs of the users that own the part |
| `parent_part` | reference -> [#category:part] |  | Parent of this part |
| `ref_url` | text |  | URL to the part details (git url, website, etc.) |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |

#### Enum values

**delivered_as**

| Value | Name | Description |
|-----|------|-------------|
| `goods` | goods | - |
| `service` | service | - |
| `software` | software | - |


## devu

**Resource Type:** `dev_user`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `display_name` | text | ✔︎ | The user's display name. The name is non-unique and mutable. |
| `email` | text |  | Email address of the user. |
| `external_identities` | struct (collection) |  | IDs of the Dev User outside the DevRev SOR. |
| `full_name` | text |  | Full name of the user. |


## directory

**Resource Type:** `directory`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `description` | text |  | Description of the directory |
| `icon` | text |  | Icon of the directory |
| `language` | text |  | Language of the directory |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `parent` | reference -> [#record:directory] |  | Parent directory |
| `published` | bool | ✔︎ | Whether the directory is published |
| `rank` | text |  | Rank of the directory |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the directory |
| `title` | text | ✔︎ | Title of the directory |


## dm

**Resource Type:** `chat`, `dm`

**Capabilities:** Can Load

### Fixed fields

| Field | Value |
|-------|-------|
| `chat_type` | "dm" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `is_default` | bool |  | Whether this is the default DM for messaging the constituent users. If true, then this DM is always returned when opening a DM for the users. Note only one DM may be the default for a given set of users. |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `record_ids` | text (collection) |  | The associated records for this DM. |
| `title` | text |  | The title given to the chat. |
| `user_ids` | reference (collection) -> [#category:user] | ✔︎ | The users in the direct message. Only these users have access the chat's history and can send new messages. |


## enhancement

**Resource Type:** `part`, `enhancement`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `part_type` | "enhancement" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account_ids` | reference (collection) -> [#record:account] |  | Accounts associated to enhancement |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `delivered_as` | enum (collection) |  | Methods the product can be delivered as |
| `description` | rich_text |  | Description of the part |
| `docs` | struct (collection) |  | Docs associated with the part |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `name` | text | ✔︎ | Name of the part |
| `opportunity_ids` | reference (collection) -> [#category:work] |  | Opportunities from the enhancement |
| `owned_by_ids` | reference (collection) -> [#record:devu] | ✔︎ | User IDs of the users that own the part |
| `parent_part` | reference -> [#category:part] | ✔︎ | Parent of this part |
| `potential_revenue` | float |  | Potential revenue from the enhancement |
| `ref_url` | text |  | URL to the part details (git url, website, etc.) |
| `release_notes` | text |  | Release notes of the enhancement |
| `rev_score` | float |  | Rev Score of the enhancement |
| `rev_score_tier` | enum |  | Rev Score tier of the enhancement |
| `stage` | enum | ✔︎ | Stage of the part |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |
| `target_close_date` | timestamp |  | Target close date for the object |
| `target_start_date` | timestamp |  | Target start date for the object |
| `ticket_ids` | reference (collection) -> [#category:work] |  | Tickets associated with the enhancement |

#### Enum values

**delivered_as**

| Value | Name | Description |
|-----|------|-------------|
| `goods` | goods | - |
| `service` | service | - |
| `software` | software | - |

**rev_score_tier**

| Value | Name | Description |
|-----|------|-------------|
| `high` | high | - |
| `low` | low | - |
| `medium` | medium | - |

**stage**

| Value | Name | Description |
|-----|------|-------------|
| `deprecated` | Deprecated | - |
| `deprioritized` | Deprioritized | - |
| `general_availability` | General Availability | - |
| `ideation` | Ideation | - |
| `in_development` | In Development | - |
| `in_testing` | In testing | - |
| `limited_availability` | Limited Availability | - |
| `prioritized` | Prioritized | - |
| `ux_design` | UX Design | - |
| `wont_do` | Won't do | - |


## feature

**Resource Type:** `part`, `feature`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `part_type` | "feature" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `api_endpoints` | struct (collection) |  | Associated API endpoints |
| `api_parameters_summary` | text (collection) |  | Associated API parameters |
| `api_prefix_summary` | text (collection) |  | Common Path Denominators of the Api Operations |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `delivered_as` | enum (collection) |  | Methods the product can be delivered as |
| `description` | rich_text |  | Description of the part |
| `development_owner_id` | reference -> [#record:devu] |  | User ID of the development owner of the part |
| `discoveryevidences` | text (collection) |  | A evidences that the inferer were able to find that justify the inference outcome |
| `docs` | struct (collection) |  | Docs associated with the part |
| `fulfilled_by` | reference (collection) -> [#category:part] |  | IDs of the runnables that fulfill this feature |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `name` | text | ✔︎ | Name of the part |
| `owned_by_ids` | reference (collection) -> [#record:devu] | ✔︎ | User IDs of the users that own the part |
| `parent_part` | reference -> [#category:part] | ✔︎ | Parent of this part |
| `pm_owner_id` | reference -> [#record:devu] |  | User ID of the PM owner of the part |
| `qa_owner_id` | reference -> [#record:devu] |  | User ID of the QA owner of the part |
| `ref_url` | text |  | URL to the part details (git url, website, etc.) |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |

#### Enum values

**delivered_as**

| Value | Name | Description |
|-----|------|-------------|
| `goods` | goods | - |
| `service` | service | - |
| `software` | software | - |


## group

**Resource Type:** `group`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `description` | rich_text | ✔︎ | Description of the group |
| `includes` | reference (collection) -> [#record:group] |  | IDs of the group(s) that the group includes |
| `member_type` | enum |  | Type of the members in the group. |
| `name` | text | ✔︎ | Name of the group |
| `owner` | reference -> [#record:devu] |  | Owner of the group |
| `type` | enum |  | Type of the group |

#### Enum values

**member_type**

| Value | Name | Description |
|-----|------|-------------|
| `dev_user` | dev_user | - |
| `rev_user` | rev_user | - |
| `svc_acc` | svc_acc | - |

**type**

| Value | Name | Description |
|-----|------|-------------|
| `dynamic` | dynamic | - |
| `static` | static | - |


## incident

**Resource Type:** `incident`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `acknowledged_date` | timestamp |  | Timestamp when the incident was acknowledged. |
| `applies_to_part_ids` | reference (collection) -> [#category:part] |  | Parts to which the work is attached. |
| `body` | rich_text |  | Body of the work object |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `identified_date` | timestamp |  | Time when the incident was identified/reported. |
| `item_url_field` | text |  | Link to the item in the origin system |
| `mitigated_date` | timestamp |  | Timestamp when the incident was mitigated. |
| `owned_by_ids` | reference -> [#category:user] | ✔︎ | User IDs of the users that own the work |
| `pia_ids` | reference (collection) -> [#record:article] |  | The article ids of the Post-Incident Analysis(PIA) of the incident. |
| `playbook_ids` | reference (collection) -> [#record:article] |  | The article ids of the playbook(s) associated with the incident. |
| `related_doc_ids` | reference (collection) -> [#record:article] |  | The article ids of other documents associated with the incident. |
| `reported_by` | enum |  | The entity that first reported the incident. |
| `severity` | enum | ✔︎ | Severity of the work |
| `stage` | enum | ✔︎ |  |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object. |
| `target_close_date` | timestamp |  | Timestamp when the work is expected to be complete |
| `title` | text | ✔︎ | Title of the work object |

#### Enum values

**reported_by**

| Value | Name | Description |
|-----|------|-------------|
| `1` | Customer | - |
| `2` | Internal Users | - |
| `3` | System | - |

**severity**

| Value | Name | Description |
|-----|------|-------------|
| `1` | sev-0 | - |
| `2` | sev-1 | - |
| `3` | sev-2 | - |
| `4` | sev-3 | - |

**stage**

| Value | Name | Description |
|-----|------|-------------|
| `acknowledged` | Acknowledged | - |
| `canceled` | Canceled | - |
| `duplicate` | Duplicate | - |
| `fixing` | Fixing | - |
| `mitigated` | Mitigated | - |
| `resolved` | Resolved | - |
| `triage` | Triage | - |


## issue

**Resource Type:** `work`, `issue`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `work_type` | "issue" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account_ids` | reference (collection) -> [#record:account] |  | Accounts associated to issues |
| `actual_close_date` | timestamp |  | Timestamp when the work was actually completed |
| `actual_effort` | float |  | Actual effort to complete the issue |
| `applies_to_part_id` | reference -> [#category:part] | ✔︎ | Details of the part relevant to the work |
| `applies_to_version_ids` | reference (collection) -> [#record:version] |  | Part versions relevant to the work |
| `body` | rich_text |  | Body of the work object |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `estimated_effort` | float |  | Estimated effort to complete the issue |
| `fallback_parts` | reference -> [#category:part] |  | Other values that could serve as part if apples_to_part_id is found to be invalid. |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `owned_by_ids` | reference (collection) -> [#category:user] | ✔︎ | User IDs of the users that own the work |
| `priority` | enum | ✔︎ | Priority of the work based upon impact and criticality |
| `release_version_ids` | reference (collection) -> [#record:version] |  | Versions that will contain the resolving commit IDs |
| `reported_by_ids` | reference (collection) -> [#category:user] |  | User IDs of the users that reported the work |
| `rev_org_ids` | reference (collection) -> [#record:account #record:revo] |  | Rev orgs associated to issues |
| `sla_id` | reference -> [#record:sla] |  | The ID of the SLA applying to this object, controlling how the SLA tracking service treats it. |
| `sla_tracker_id` | reference -> [#record:sla_tracker] |  | The ID of the SLA tracker applied to this object, which is used to track the SLA metrics. |
| `sprint_id` | reference -> [#record:vista_group_item] |  | Sprint to which the issue belongs. |
| `stage` | enum | ✔︎ | Stage of the object |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |
| `target_close_date` | timestamp |  | Timestamp when the work is expected to be complete |
| `target_start_date` | timestamp |  | Target start date for the object |
| `title` | text | ✔︎ | Title of the work object |

#### Enum values

**priority**

| Value | Name | Description |
|-----|------|-------------|
| `P0` | P0 | - |
| `P1` | P1 | - |
| `P2` | P2 | - |
| `P3` | P3 | - |

**stage**

| Value | Name | Description |
|-----|------|-------------|
| `backlog` | Backlog | - |
| `completed` | Completed | - |
| `duplicate` | Duplicate | - |
| `in_deployment` | In Deployment | - |
| `in_development` | In Development | - |
| `in_review` | In Review | - |
| `in_testing` | In Testing | - |
| `prioritized` | Prioritized | - |
| `triage` | Triage | - |
| `wont_fix` | Won't Fix | - |


## link

**Resource Type:** `link`

**Capabilities:** Can Extract, Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `link_type` | enum | ✔︎ | Type of link used to define the relationship. |
| `source_id` | reference -> [#category:work #record:incident] | ✔︎ | Source object ID |
| `source_object_type` | enum |  | Source object type |
| `target_id` | reference -> [#category:work #record:incident] | ✔︎ | Target object ID |
| `target_object_type` | enum |  | Target object type |
| `transformed_from_id` | text |  |  |

#### Enum values

**link_type**

| Value | Name | Description |
|-----|------|-------------|
| `is_dependent_on` | Is Dependent On | - |
| `is_duplicate_of` | Is Duplicate Of | - |
| `is_parent_of` | Is Parent Of | - |
| `is_related_to` | Is Related To | - |

**source_object_type**

| Value | Name | Description |
|-----|------|-------------|
| `conversation` | - | - |
| `incident` | - | - |
| `work` | - | - |

**target_object_type**

| Value | Name | Description |
|-----|------|-------------|
| `conversation` | - | - |
| `incident` | - | - |
| `work` | - | - |


## linkable

**Resource Type:** `part`, `linkable`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `part_type` | "linkable" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `coderepo_paths` | text |  | Paths in the repository for the code part |
| `coderepo_url` | text |  | URL to the server & repo for the code part |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `delivered_as` | enum (collection) |  | Methods the product can be delivered as |
| `description` | rich_text |  | Description of the part |
| `discoveryevidences` | text (collection) |  | A evidences that the inferer were able to find that justify the inference outcome |
| `docs` | struct (collection) |  | Docs associated with the part |
| `item_url_field` | text |  | Link to the item in the origin system |
| `kind` | enum |  | The kind of linkable |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `name` | text | ✔︎ | Name of the part |
| `owned_by_ids` | reference (collection) -> [#record:devu] | ✔︎ | User IDs of the users that own the part |
| `parent_part` | reference -> [#category:part] |  | Parent of this part |
| `ref_url` | text |  | URL to the part details (git url, website, etc.) |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |

#### Enum values

**delivered_as**

| Value | Name | Description |
|-----|------|-------------|
| `goods` | goods | - |
| `service` | service | - |
| `software` | software | - |

**kind**

| Value | Name | Description |
|-----|------|-------------|
| `component` | component | - |
| `library` | library | - |


## meeting

**Resource Type:** `meeting`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `channel` | enum | ✔︎ | The channel of meeting. |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `description` | rich_text |  | Description of the meeting. |
| `ended_date` | timestamp |  | Time at which meeting ended. |
| `engagement_new_ref` | text |  | Reference ID associated with the new engagement |
| `external_ref_id` | text |  | External reference of the meeting. This is the identifier from the meeting channel/provider. |
| `external_url` | text |  | External URL associated with the meeting. |
| `member_ids` | reference (collection) -> [#category:user] | ✔︎ | IDs of the members in the meeting. |
| `organizer_id` | reference -> [#category:user] | ✔︎ | ID of the organizer of the meeting. |
| `parent_id` | reference -> [#category:work #record:account] |  | Parent ID of the meeting. |
| `parent_object_type` | enum |  | Parent Objet Type |
| `recording_url` | text |  | Recording URL of the meeting. |
| `scheduled_date` | timestamp | ✔︎ | Time at which meeting was scheduled to start. |
| `state` | enum | ✔︎ | The state of meeting. |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the meeting. |
| `title` | text | ✔︎ | Title of the meeting object. |

#### Enum values

**channel**

| Value | Name | Description |
|-----|------|-------------|
| `amazon_connect` | amazon_connect | - |
| `devrev` | devrev | - |
| `google_meet` | google_meet | - |
| `offline` | offline | - |
| `other` | other | - |
| `teams` | teams | - |
| `zoom` | zoom | - |

**parent_object_type**

| Value | Name | Description |
|-----|------|-------------|
| `account` | - | - |
| `work` | - | - |

**state**

| Value | Name | Description |
|-----|------|-------------|
| `canceled` | canceled | - |
| `completed` | completed | - |
| `no_show` | no_show | - |
| `ongoing` | ongoing | - |
| `rejected` | rejected | - |
| `rescheduled` | rescheduled | - |
| `scheduled` | scheduled | - |
| `waiting` | waiting | - |


## microservice

**Resource Type:** `part`, `microservice`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `part_type` | "microservice" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `delivered_as` | enum (collection) |  | Methods the product can be delivered as |
| `description` | rich_text |  | Description of the part |
| `development_owner_id` | reference -> [#record:devu] |  | User ID of the development owner of the part |
| `docs` | struct (collection) |  | Docs associated with the part |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `name` | text | ✔︎ | Name of the part |
| `owned_by_ids` | reference (collection) -> [#record:devu] | ✔︎ | User IDs of the users that own the part |
| `parent_part` | reference -> [#category:part] |  | Parent of this part |
| `pm_owner_id` | reference -> [#record:devu] |  | User ID of the PM owner of the part |
| `qa_owner_id` | reference -> [#record:devu] |  | User ID of the QA owner of the part |
| `ref_url` | text |  | URL to the part details (git url, website, etc.) |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |

#### Enum values

**delivered_as**

| Value | Name | Description |
|-----|------|-------------|
| `goods` | goods | - |
| `service` | service | - |
| `software` | software | - |


## object_member

**Resource Type:** `object_member`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `add_member_ids` | reference (collection) -> [#category:user] |  | Add or update user IDs in the group |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `member_id` | reference -> [#category:user] |  | ID of the user or group |
| `object_id` | reference -> [#record:group] | ✔︎ | Globally unique DevRev Object Name (DON) for the object where the member is being added. |
| `remove_member_ids` | reference (collection) -> [#category:user] |  | Remove user IDs from the group |
| `role_id` | reference -> [#record:role] |  | Role that entails the permissions of the member |
| `target_object_type` | enum | ✔︎ | Type of target object |
| `valid_from_date` | timestamp | ✔︎ | Timestamp when this membership is valid |
| `valid_to_date` | timestamp |  | Timestamp when this membership expires |

#### Enum values

**target_object_type**

| Value | Name | Description |
|-----|------|-------------|
| `dashboard` | - | - |
| `group` | - | - |


## opportunity

**Resource Type:** `work`, `opportunity`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `work_type` | "opportunity" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account_id` | reference -> [#record:account] |  | ID of the account that the opportunity is related to. |
| `actual_close_date` | timestamp |  | Timestamp when the work was actually completed |
| `annual_contract_value` | struct |  | Annual contract value of the opportunity. |
| `body` | rich_text |  | Body of the work object |
| `budget` | struct |  | Budget of the opportunity. |
| `contact_ids` | reference (collection) -> [#record:revu] |  | Contacts involved in the opportunity. |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `fallback_parts` | reference -> [#category:part] |  | Other values that could serve as part if apples_to_part_id is found to be invalid. |
| `forecast_category` | enum | ✔︎ | Forecast category of the opportunity. |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `owned_by_ids` | reference (collection) -> [#category:user] | ✔︎ | User IDs of the users that own the work |
| `priority` | enum | ✔︎ | Priority of the opportunity. |
| `probability` | float |  | Probability of winning the deal, value lies between 0.0% and 100.0% |
| `reported_by_ids` | reference (collection) -> [#category:user] |  | User IDs of the users that reported the work |
| `stage` | enum | ✔︎ | Stage of the object |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |
| `target_close_date` | timestamp |  | Timestamp when the work is expected to be complete |
| `title` | text | ✔︎ | Title of the work object |
| `value` | struct |  | Value of the opportunity. |

#### Enum values

**forecast_category**

| Value | Name | Description |
|-----|------|-------------|
| `commit` | commit | - |
| `omitted` | omitted | - |
| `pipeline` | pipeline | - |
| `strong_upside` | strong_upside | - |
| `upside` | upside | - |
| `won` | won | - |

**priority**

| Value | Name | Description |
|-----|------|-------------|
| `P0` | P0 | - |
| `P1` | P1 | - |
| `P2` | P2 | - |
| `P3` | P3 | - |

**stage**

| Value | Name | Description |
|-----|------|-------------|
| `closed_lost` | Closed Lost | - |
| `closed_won` | Closed Won | - |
| `contract` | Contract | - |
| `negotiation` | Negotiation | - |
| `qualification` | Qualification | - |
| `stalled` | Stalled | - |
| `validation` | Validation | - |

### Structs

#### money

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `amount` | text | ✔︎ | Amount of the money. |
| `currency` | text | ✔︎ | Currency of the money. |


## product

**Resource Type:** `part`, `product`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `part_type` | "product" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `delivered_as` | enum (collection) |  | Methods the product can be delivered as |
| `description` | rich_text |  | Description of the part |
| `docs` | struct (collection) |  | Docs associated with the part |
| `fulfilled_by` | reference (collection) -> [#category:part] |  | IDs of the runnables that fulfill this product |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `name` | text | ✔︎ | Name of the part |
| `owned_by_ids` | reference (collection) -> [#record:devu] | ✔︎ | User IDs of the users that own the part |
| `pm_owner_id` | reference -> [#record:devu] |  | User ID of the PM owner of the part |
| `product_delivered_as` | enum |  | Product Delivered as |
| `ref_url` | text |  | URL to the part details (git url, website, etc.) |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |

#### Enum values

**delivered_as**

| Value | Name | Description |
|-----|------|-------------|
| `goods` | goods | - |
| `service` | service | - |
| `software` | software | - |

**product_delivered_as**

| Value | Name | Description |
|-----|------|-------------|
| `goods` | goods | - |
| `service` | service | - |


## revu

**Resource Type:** `rev_user`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `description` | rich_text |  | Description of the Rev user. |
| `display_handle` | text |  | The user's display handle. This field is deprecated now. Use display_name field instead. |
| `display_name` | text | ✔︎ | The user's display name. The name is non-unique and mutable. |
| `email` | text |  | Email address of the user. |
| `external_uid` | text |  | External ref is a mutable unique identifier for a user within the Rev organization from your primary customer record. If none is available, a good alternative is the email address/phone number which could uniquely identify the user. If none is specified, a system-generated identifier will be assigned to the user. |
| `full_name` | text |  | Full name of the user. |
| `phone_numbers` | text (collection) |  | Phone numbers of the user. |
| `rev_org` | reference -> [#record:account #record:revo] |  | The ID of the parent Rev Organization. |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |


## runnable

**Resource Type:** `part`, `runnable`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `part_type` | "runnable" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `coderepo_paths` | text |  | Paths in the repository for the code part |
| `coderepo_url` | text |  | URL to the server & repo for the code part |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `delivered_as` | enum (collection) |  | Methods the product can be delivered as |
| `description` | rich_text |  | Description of the part |
| `discoveryevidences` | text (collection) |  | A evidences that the inferer were able to find that justify the inference outcome |
| `docs` | struct (collection) |  | Docs associated with the part |
| `item_url_field` | text |  | Link to the item in the origin system |
| `kind` | enum |  | The kind of runnable |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `name` | text | ✔︎ | Name of the part |
| `owned_by_ids` | reference (collection) -> [#record:devu] | ✔︎ | User IDs of the users that own the part |
| `parent_part` | reference -> [#category:part] |  | Parent of this part |
| `ref_url` | text |  | URL to the part details (git url, website, etc.) |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |

#### Enum values

**delivered_as**

| Value | Name | Description |
|-----|------|-------------|
| `goods` | goods | - |
| `service` | service | - |
| `software` | software | - |

**kind**

| Value | Name | Description |
|-----|------|-------------|
| `ecr_image` | ecr_image | - |
| `lambda` | lambda | - |
| `microservice` | microservice | - |
| `service` | service | - |


## sysu

**Resource Type:** `sys_user`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `display_name` | text | ✔︎ | The user's display name. The name is non-unique and mutable. |
| `full_name` | text |  | Full name of the user. |


## tag

**Resource Type:** `tag`

**Capabilities:** Can Load

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `access_level` | enum |  | Access level for the tag |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `description` | rich_text |  | Description of the tag |
| `name` | text | ✔︎ | Name of the tag |
| `style` | text |  | hex color of in the format #RRGGBB |

#### Enum values

**access_level**

| Value | Name | Description |
|-----|------|-------------|
| `internal` | internal | - |
| `private` | private | - |
| `public` | public | - |
| `restricted` | restricted | - |


## task

**Resource Type:** `work`, `task`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `work_type` | "task" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `actual_close_date` | timestamp |  | Timestamp when the work was actually completed |
| `actual_effort` | float |  | Actual effort to complete the task |
| `applies_to_part_id` | reference -> [#category:part] |  | Details of the part relevant to the work |
| `applies_to_version_ids` | reference (collection) -> [#record:version] |  | Part versions relevant to the work |
| `body` | rich_text |  | Body of the work object |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `embedded` | bool |  | Whether this task is an embedded task of another work or not |
| `estimated_effort` | float |  | Estimated effort to complete the task |
| `fallback_parts` | reference -> [#category:part] |  | Other values that could serve as part if apples_to_part_id is found to be invalid. |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `owned_by_ids` | reference (collection) -> [#category:user] | ✔︎ | User IDs of the users that own the work |
| `priority` | enum |  | Priority of the work based upon impact and criticality |
| `reported_by_ids` | reference (collection) -> [#category:user] |  | User IDs of the users that reported the work |
| `stage` | enum | ✔︎ | Stage of the object |
| `start_date` | timestamp |  | Timestamp when the task was started |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |
| `target_close_date` | timestamp |  | Timestamp when the work is expected to be complete |
| `title` | text | ✔︎ | Title of the work object |

#### Enum values

**priority**

| Value | Name | Description |
|-----|------|-------------|
| `P0` | P0 | - |
| `P1` | P1 | - |
| `P2` | P2 | - |
| `P3` | P3 | - |

**stage**

| Value | Name | Description |
|-----|------|-------------|
| `in_development` | In Development | - |
| `open` | Open | - |
| `resolved` | Resolved | - |


## ticket

**Resource Type:** `work`, `ticket`

**Capabilities:** Can Extract, Can Load, Can Subtype

### Fixed fields

| Field | Value |
|-------|-------|
| `work_type` | "ticket" |

### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `account_id` | reference -> [#record:account] |  | Globally unique ID for a DevRev account |
| `actual_close_date` | timestamp |  | Timestamp when the work was actually completed |
| `applies_to_part_id` | reference -> [#category:part] | ✔︎ | Details of the part relevant to the work |
| `applies_to_version_ids` | reference (collection) -> [#record:version] |  | Part versions relevant to the work |
| `body` | rich_text |  | Body of the work object |
| `channels` | enum (collection) |  | Channels of the ticket |
| `channels_v2` | reference (collection) -> [#record:external_communication_channel] |  | Channel IDs of the ticket |
| `created_by_id` | reference -> [#category:user] |  | User ID of the user that created the object |
| `fallback_parts` | reference -> [#category:part] |  | Other values that could serve as part if apples_to_part_id is found to be invalid. |
| `group` | reference -> [#record:group] |  | Group that owns the ticket |
| `is_spam` | bool |  | Whether the ticket is spam. |
| `item_url_field` | text |  | Link to the item in the origin system |
| `modified_by_id` | reference -> [#category:user] |  | User ID of the user that last modified the object |
| `needs_response` | bool |  | Whether the ticket needs a response. |
| `owned_by_ids` | reference (collection) -> [#category:user] | ✔︎ | User IDs of the users that own the work |
| `reported_by_ids` | reference (collection) -> [#category:user] |  | User IDs of the users that reported the work |
| `rev_oid` | reference -> [#record:account #record:revo] |  | Globally unique ID for a DevRev rev org |
| `sentiment` | enum |  | Sentiment of the object |
| `sentiment_modified_date` | timestamp |  | Timestamp when the sentiment was last modified |
| `sentiment_summary` | text |  | Summary justifying the sentiment |
| `severity` | enum | ✔︎ | Severity of the ticket |
| `sla_id` | reference -> [#record:sla] |  | The ID of the SLA applying to this object, controlling how the SLA tracking service treats it. |
| `sla_tracker_id` | reference -> [#record:sla_tracker] |  | The ID of the SLA tracker applied to this object, which is used to track the SLA metrics. |
| `source_channel_v2` | reference -> [#record:external_communication_channel] |  | Source channel ID of the ticket |
| `stage` | enum | ✔︎ | Stage of the object |
| `tags` | reference (collection) -> [#record:tag] |  | Tags associated with the object |
| `target_close_date` | timestamp |  | Timestamp when the work is expected to be complete |
| `title` | text | ✔︎ | Title of the work object |
| `visibility` | enum |  | The visibility of the object. If 'internal', the object is visible within the Dev organization. If 'external', it is visible to both the Dev organization and Rev users. If not set, the default visibility is 'external'. |

#### Enum values

**channels**

| Value | Name | Description |
|-----|------|-------------|
| `email` | - | - |
| `plug` | - | - |
| `slack` | - | - |

**severity**

| Value | Name | Description |
|-----|------|-------------|
| `blocker` | Blocker | - |
| `high` | High | - |
| `low` | Low | - |
| `medium` | Medium | - |

**stage**

| Value | Name | Description |
|-----|------|-------------|
| `awaiting_customer_response` | Awaiting Customer Response | - |
| `awaiting_development` | Awaiting Development | - |
| `awaiting_product_assist` | Awaiting Product Assist | - |
| `canceled` | Canceled | - |
| `in_development` | In Development | - |
| `queued` | Queued | - |
| `resolved` | Resolved | - |
| `work_in_progress` | Work In Progress | - |

**visibility**

| Value | Name | Description |
|-----|------|-------------|
| `1` | internal | - |
| `2` | external | - |


---