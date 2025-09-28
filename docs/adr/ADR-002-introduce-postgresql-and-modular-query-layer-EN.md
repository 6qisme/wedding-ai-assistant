ADR-002: Introduce PostgreSQL and Modular Query Layer
Status: Accepted
Date: 2025-09-28

1. Context
Originally, the project stored all data in wedding_data.json. As requirements grew, problems appeared:
- JSON was hard to maintain and update.
- No convenient way to query or support fuzzy search.
- Sending full JSON to GPT wasted tokens.

2. Decision
- Switch the data layer to PostgreSQL.
- Add a new db/ folder, separating db_connection, queries, and formatters.
- Use simple rule-based intent detection first, reducing API costs.

3. Alternatives Considered
- Keep JSON: easy, but not sustainable.
- Fully rely on GPT: flexible, but costly and unstable.

4. Consequences
- Clearer architecture, easier to grow.
- I need to learn SQL, but it brings scalability and stability.
