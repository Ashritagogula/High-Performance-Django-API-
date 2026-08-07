# N+1 Queries Optimization with Django REST API

This project provides a practical demonstration of identifying, understanding, and resolving the common N+1 query problem within a Django REST API. It showcases three different implementation strategies—ranging from a naive approach to highly optimized database aggregations using eager loading and subqueries.

## Project Structure and Setup

The project is fully containerized utilizing Docker and Docker Compose. It provisions two primary services:
1. **db**: A PostgreSQL instance acting as the backend relational database.
2. **web**: A Django application configured with Gunicorn, which automatically runs migrations and seeds the database with test data upon startup.

### Running the Project

To build the images and start the services, simply run:

```bash
docker-compose up --build
```

The `web` service will automatically perform the following steps:
- Apply all database migrations.
- Execute a custom management command (`seed_db`) to clear old data and uniformly seed 20 Authors, 200 Posts, and 2000 Comments.
- Spin up the development server on port 8000.

## Endpoints and Implementations

The application exposes three API endpoints to demonstrate various levels of query efficiency:

1. **Naive Endpoint (`GET /api/posts/naive`)**
   - **Strategy**: Iterates through all posts and fetches the author and comments for each post individually.
   - **Result**: Suffers heavily from the N+1 problem, producing over 401 separate SQL queries for our dataset.

2. **Optimized Endpoint (`GET /api/posts/optimized`)**
   - **Strategy**: Utilizes Django's `select_related('author')` to eagerly load foreign key relationships via a SQL JOIN. It also utilizes `annotate(comment_count=Count('comments'))` to compute comment counts at the database level.
   - **Result**: Drastically cuts down queries from ~401 to just 1 single query.

3. **Advanced Endpoint (`GET /api/posts/advanced`)**
   - **Strategy**: Builds on the optimized query by injecting a Subquery to calculate author-wide metrics (`total_author_views`). This calculates the sum of all post views associated with a specific author without resulting in incorrect GROUP BY behavior.
   - **Result**: Efficiently extracts highly complex relational data while retaining a constant query count (1 query).

## Benchmarking Findings

A benchmarking script (`benchmark.py`) is included to track metrics across 50 requests. The results clearly illustrate the performance discrepancy:

- **Naive Endpoint**: Averages around ~240ms per request, triggering 401 SQL queries.
- **Optimized/Advanced Endpoints**: Average around ~16-18ms per request, triggering a stable 1 SQL query.

This stark difference highlights the latency penalties associated with N+1 bottlenecks and demonstrates that pushing operations down to the database level unlocks a scalable application capable of handling high loads.
