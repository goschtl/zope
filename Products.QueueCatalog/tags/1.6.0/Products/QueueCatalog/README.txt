A QueueCatalog delegates most requests to a ZCatalog that is named as part of the QueueCatalog configuration.

Requests to catalog or uncatalog objects are queued. They must be processed by a separate process (or thread).

The queuing provides benefits:

* Content-management operations, performed by humans, complete much faster, this making the content-management system more effiecient for it's users.
* Catalog updates are batched, which makes indexing much more efficient.
* Indexing is performed by a single thread, allowing more effecient catalog document generation and avoiding conflict errors from occuring during indexing.
* When used with ZEO, indexing might e performed on the same machine as the storage server, making updates faster.


