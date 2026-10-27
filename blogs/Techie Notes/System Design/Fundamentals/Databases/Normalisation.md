Database normalization is the process of organizing relational database tables to reduce data redundancy, prevent data anomalies, and maintain data integrity. It involves decomposing tables into smaller, logically related tables and defining relationships using primary keys and foreign keys.

Normalization is particularly important in transactional databases, where the same information may otherwise be repeated across thousands of records.

## 1NF - First Form
A table is in First Normal Form when each column contains a single value for each row, and there are no repeating groups or multivalued attributes within a cell.

In practical relational database design, each row should also be identifiable through a key.
### Example
![1NF](../../../../assets/excalidraw/System Design/Fundamentals/Databases/1NF.excalidraw)

## 2NF - Second Form

A table is in Second Normal Form if:

1. It is already in 1NF.
2. Every non-prime attribute is fully functionally dependent on every candidate key. In simpler terms, no non-key attribute depends on only part of a composite candidate key.

Partial dependencies are relevant when a candidate key contains multiple columns.

### Example
![2NF](../../../../assets/excalidraw/System Design/Fundamentals/Databases/2NF.excalidraw)


## 3NF - Third Normal Form
A table is in Third Normal Form if:

1. It is already in 2NF.
2. For every non-trivial functional dependency (X - > A), either (X) is a superkey or (A) is a prime attribute (an attribute belonging to at least one candidate key).    

A useful introductory rule is to eliminate transitive dependencies of non-key attributes on candidate keys.

### Example
![3NF](../../../../assets/excalidraw/System Design/Fundamentals/Databases/3NF.excalidraw)


**Note:**
BCNF is a stricter version of 3NF. A table is in BCNF if, for every non-trivial functional dependency (X - > Y), (X) is a superkey. Unlike 3NF, BCNF does not provide an exception for a dependency whose right-hand-side attribute is prime.

## 4NF - Fourth Normal Form
A table is in Fourth Normal Form if it is already in BCNF and has no non-trivial multivalued dependency (X -> Y) unless (X) is a superkey. Multivalued dependencies arise when two or more independent sets of values are associated with the same entity.
### Example
![4NF](../../../../assets/excalidraw/System Design/Fundamentals/Databases/4NF.excalidraw)

## Fifth Normal Form (5NF)
Fifth Normal Form, also called Project-Join Normal Form (PJ/NF), addresses redundancy caused by join dependencies that cannot be explained adequately by ordinary functional or multivalued dependencies. A table is in 5NF if every non-trivial join dependency is implied by its candidate keys.

### Example
![5NF](../../../../assets/excalidraw/System Design/Fundamentals/Databases/5NF.excalidraw)


## Summary: All Normal Forms

| Normal Form | Requirement                                                               | Almost always required?               | When you might skip or relax it                                                                                                                                                                                                              |
| ----------- | ------------------------------------------------------------------------- | ------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **1NF**     | Atomic column values; no repeating groups                                 | Yes, nearly always                    | Deliberate use of JSON/array columns for semi-structured data (e.g., tags, flexible attributes) where you never query inside the value relationally. Note this technically violates 1NF, so do it knowingly.                                 |
| **2NF**     | 1NF + no partial dependency of non-prime attributes on a candidate key    | Yes                                   | Rarely skipped by choice; partial dependencies usually just mean a design mistake. Only relax in read-only reporting tables.                                                                                                                 |
| **3NF**     | For every non-trivial FD, determinant is a superkey or dependent is prime | Standard target for OLTP              | Reporting/analytics tables, or when a transitive dependency is stable and the join cost is measurable (e.g., storing `city` alongside `zip_code` that never changes).                                                                        |
| **BCNF**    | Every determinant of a non-trivial functional dependency is a superkey    | Good default, but optional            | When decomposing would **lose a functional dependency** (some BCNF decompositions are not dependency-preserving), forcing you to enforce the constraint in application code or with expensive multi-table checks. In that case, stay at 3NF. |
| **4NF**     | Every non-trivial multivalued dependency has a superkey as determinant    | Only when the problem actually exists | Needed when a table stores two _independent_ multivalued facts (e.g., employee → skills and employee → languages in one table, causing a cross-product). If you don’t have that pattern, 4NF is satisfied automatically.                     |
| **5NF**     | Every non-trivial join dependency is implied by candidate keys            | Rarely worth pursuing                 | Only for genuine join dependencies, usually in complex many-to-many-to-many relationships. Most real schemas never need explicit 5NF work, and over-decomposing here adds joins for little gain.                                             |

Normalization does not necessarily mean that every possible table should be decomposed as much as possible. Excessive decomposition may require more joins and can complicate query execution. In read-heavy systems, carefully chosen denormalization may be justified for performance, provided consistency is maintained.

The central principle is to ensure that each fact is stored in the appropriate relation, dependencies are represented correctly, and decompositions preserve information and, where possible, the relevant constraints.