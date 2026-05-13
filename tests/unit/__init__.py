"""Unit tests for services and pure logic.

Conventions:

- No database, no http, no FastAPI dependency injection wiring.
- Fakes go in-process: implement ``BaseRepository`` with plain Python
  data structures rather than reaching for mocking libraries.
- Test the service's contract (returns, raises, ordering), not its
  call sequence against the repository.
"""
