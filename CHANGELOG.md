# Changelog

## [0.2.0] - 2026-11-27

### Added

- Modular FastAPI device and alert endpoints with Pydantic validation, Swagger examples, and documented HTTP errors.
- Device service, repository, and event layers; duplicate and missing-device handling; one alert for an online-to-offline transition; pytest coverage.
- MySQL configuration via environment variables, SQLAlchemy sessions and ORM models, and a MySQL repository adapter with transaction handling.
- Alembic initial schema and follow-up optional device-location migration, plus isolated SQLite tests for service and repository behavior.