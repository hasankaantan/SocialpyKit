"""Data-access repositories for SocialpyKit.

Conventions for this layer:

- One repository class per aggregate root.
- Repositories implement the ``BaseRepository[EntityT, IdT]`` abstract
  base from ``app.core.essentials`` — services depend on that interface,
  not on concrete classes.
- Only SQLAlchemy queries live here; no business logic.
- Methods return domain models or typed DTOs, never raw SQLAlchemy
  ``Row`` objects.
- Every relationship is loaded explicitly via ``selectinload`` or
  ``joinedload``. No lazy loading.
- All methods are ``async def`` and accept an injected
  ``AsyncSession``; never construct sessions inside the repository.
"""
