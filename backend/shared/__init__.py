"""
Shared package for Footprint Manager cross-cutting utilities.

This package provides foundational building blocks used across all domain
apps.  It must NOT import from ``apps.*`` or ``common`` to avoid circular
dependencies.

Sub-packages
------------
constants     Global platform constants (API version, page sizes, headers).
enums         Platform-wide enumeration types.
exceptions    Exception hierarchy rooted at FootprintBaseException.
events        Domain event base class (BaseDomainEvent).
event_bus     EventHandler protocol, EventDispatcher ABC, InProcessEventDispatcher.
pagination    PagedResult, CursorPage, FootprintPageNumberPagination.
permissions   BasePermissionPolicy interface.
security      SecurityContext, TokenClaims, masking helpers.
validators    Email, UUID, slug, URL, phone validators.
types         Shared type aliases (UUID4, ISODatetime, JSONDict, …).
utils         Pure utility functions (slugify_safe, deep_merge, …).
cache         CacheBackend abstract interface.
search        SearchBackend abstract interface with SearchQuery / SearchResult.
storage       StorageBackend abstract interface with StoredFile.
"""
