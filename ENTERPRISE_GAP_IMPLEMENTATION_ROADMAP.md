# Enterprise Gap Implementation Roadmap

This roadmap closes the gap between the current DocPro codebase and the target enterprise architecture.

## Phase 1: Authentication Alignment

Goal: make frontend auth, protected Flask routes, and admin APIs use the same token model.

Tasks:
- Initialize Flask-JWT-Extended in the app factory.
- Return a real JWT access token from login/register endpoints.
- Keep API keys as a separate integration credential instead of treating them as the session token.
- Update auth middleware to validate JWTs consistently and fail clearly.
- Keep session logout compatibility for existing clients.

Definition of done:
- Frontend stores a JWT in localStorage.
- Admin and protected routes accept that JWT.
- API keys remain usable for automation and external integrations.

## Phase 2: CMS Backend Foundation

Goal: replace frontend-only CMS state with database-backed content management.

Tasks:
- Add Page, Widget, and SEOMetadata models.
- Add CMS service layer for CRUD and ordering.
- Add CMS API routes for admin editing and public page retrieval.
- Persist page blocks and metadata instead of storing them in React state only.

Definition of done:
- Admin CMS reads/writes persisted pages.
- Public pages can request content by slug.

## Phase 3: Dynamic Public Rendering

Goal: render public pages from CMS content instead of static-only page definitions.

Tasks:
- Add DynamicPage route in the public frontend.
- Add widget renderer registry.
- Load page payloads by slug from CMS API.
- Support fallback SEO metadata from backend.

Definition of done:
- New pages can be created in the admin CMS and rendered publicly without code changes.

## Phase 4: SEO Automation

Goal: move from basic sitemap support to a real SEO service.

Tasks:
- Add SEO service for titles, descriptions, canonical URLs, and JSON-LD.
- Generate sitemap from CMS pages and tools data.
- Replace mock SEO admin metrics with live data.
- Add background jobs for sitemap refresh and metadata refresh.

Definition of done:
- SEO dashboard shows real page status.
- Sitemap and robots reflect database-backed public content.

## Phase 5: AEO Engine

Goal: add answer-engine optimization workflows missing from the current repo.

Tasks:
- Add AEO data model and service.
- Extract candidate question-answer blocks from CMS content.
- Store recommendations and approval state.
- Add admin UI for reviewing and publishing approved answers.

Definition of done:
- Pages can carry structured answer content and tracked AEO recommendations.

## Phase 6: Monitoring and Data Realism

Goal: replace mock dashboard values with backend-backed metrics.

Tasks:
- Wire Prometheus-compatible metrics endpoint for the Flask app.
- Replace mocked user dashboard stats/history with API responses.
- Replace mocked admin SEO/CMS counts with database queries.
- Add health and queue visibility for workers and Celery tasks.

Definition of done:
- Dashboards show real platform state instead of demo data.
