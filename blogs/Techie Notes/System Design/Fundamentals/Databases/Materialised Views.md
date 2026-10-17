A view is often described as a virtual table. It looks and behaves like a table when you query it, but it does not hold any data of its own. All the database stores is the query that defines it, which is why a view is best described as a stored query. Every time you read from the view, the database runs that stored query against the underlying tables and returns the result, so the data is always current.

A view takes almost no storage, since only its definition is saved, not the rows. It is useful for several reasons. It simplifies complex queries, since a long join can be written once and then used like a table. It improves security, since users can be given access to a view that exposes only certain columns or rows (for example hiding salary or personal data) without access to the full table. And it acts as an abstraction layer, so the underlying tables can change while the view keeps the old shape for applications that depend on it.

An important point: a view does not make a query faster. The database simply substitutes the view's query into yours, so an expensive query behind a view is still expensive every time.

## Read Only vs Updatable views
Views can be read-only or updatable, which means you can run INSERT, UPDATE and DELETE on the view and the change goes through to the underlying table. A view can only be updatable when the database can map each row of the view back to exactly one row in one table. That is true for simple views, and false when the view uses things like joins across several tables, GROUP BY, aggregate functions such as SUM, DISTINCT or UNION, since a row in the view may then represent many rows underneath, and the database cannot know which to change.

## Materialized Views
A normal view runs its query every single time. That is fine for simple filters, but not for heavy work such as aggregating hundreds of millions of rows, or joining several big tables. If a dashboard runs such a query every few seconds for many users, the database repeats the same expensive calculation again and again, even though the answer barely changes between runs.

A materialized view runs the query once and physically stores the result on disk, like a real table. Reading from it is then just reading stored rows, which is fast, and no calculation is repeated. Indexes can be created on it, just like on a table, to make lookups even faster.

The trade-off is that the stored result is a snapshot of the data at the time it was last computed. If the underlying tables change, the materialized view does not know, and it stays out of date until it is refreshed. In short, a view always gives fresh data but may be slow, while a materialized view gives fast data but may be stale.

### Normal View vs Material View

| Aspect         | View                                       | Materialized view                        |
| -------------- | ------------------------------------------ | ---------------------------------------- |
| What is stored | Only the query definition                  | The query and its result rows            |
| Storage used   | Almost none                                | Space for the result, similar to a table |
| Data freshness | Always current                             | A snapshot, stale until refreshed        |
| Read speed     | Same as running the query                  | Fast, since results are precomputed      |
| Indexes        | Not on the view itself                     | Can be created on it                     |
| Updatable      | Sometimes, if simple                       | Generally not, you refresh it instead    |
| Cost           | Paid on every read                         | Paid at refresh time                     |
| Best for       | Simplifying queries, security, abstraction | Heavy aggregations and joins read often  |

### Refreshing Strategies
|Strategy|How it works|Pros|Cons|
|---|---|---|---|
|Manual or on demand|Someone or some job runs the refresh when needed|Full control|Easy to forget, can go stale|
|Scheduled|Refresh at fixed intervals, such as every hour or night|Simple and predictable|Data is stale between refreshes|
|On commit|Updated whenever the source data changes (supported by some databases)|Always fresh|Slows down every write to the source tables|
|Full refresh|Recomputes the whole result from scratch|Simple and always correct|Slow and heavy on large data|
|Incremental refresh|Updates only the rows affected by changes|Much cheaper|More complex, and not supported for all queries or in all databases|