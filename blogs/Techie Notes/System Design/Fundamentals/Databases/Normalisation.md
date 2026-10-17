Database normalization is the process of organizing relational database tables to reduce data redundancy, prevent data anomalies, and maintain data integrity. It involves decomposing tables into smaller, logically related tables and defining relationships using primary keys and foreign keys.

Normalization is particularly important in transactional databases, where the same information may otherwise be repeated across thousands of records.

## 1NF - First Form
A table is in First Normal Form when each column contains a single value for each row, and there are no repeating groups or multivalued attributes within a cell.

In practical relational database design, each row should also be identifiable through a key.
### Example

| Student ID | Student Name | Phone Numbers          |
| ---------- | ------------ | ---------------------- |
| 101        | Arun         | 9876543210, 9876500000 |
| 102        | Bala         | 9876511111             |

The `Phone Numbers` column stores multiple values in a single cell, making individual numbers difficult to query and maintain.

But after converting to 1NF:

| Student ID | Student Name | Phone Number |
| ---------- | ------------ | ------------ |
| 101        | Arun         | 9876543210   |
| 101        | Arun         | 9876500000   |
| 102        | Bala         | 9876511111   |

## 2NF - Second Form

A table is in Second Normal Form if:

1. It is already in 1NF.
2. Every non-prime attribute is fully functionally dependent on every candidate key. In simpler terms, no non-key attribute depends on only part of a composite candidate key.

Partial dependencies are relevant when a candidate key contains multiple columns.

### Example
Consider a table that records student enrollments.

|Student ID|Course ID|Student Name|Course Name|Grade|
|---|---|---|---|---|
|101|C01|Arun|SQL|A|
|101|C02|Arun|Python|B|
|102|C01|Bala|SQL|A|

Assume the composite primary key is `(Student ID, Course ID)`.

The functional dependencies are:

- `Student ID → Student Name`
- `Course ID → Course Name`
- `(Student ID, Course ID) → Grade

Student Name depends only on Student ID, while Course Name depends only on Course ID. These are partial dependencies because neither attribute requires the entire composite key to be determined.

After converting to 2NF:

**Students**

|Student ID (PK)|Student Name|
|---|---|
|101|Arun|
|102|Bala|

**Courses**

|Course ID (PK)|Course Name|
|---|---|
|C01|SQL|
|C02|Python|

**Enrollments**

|Student ID (FK)|Course ID (FK)|Grade|
|---|---|---|
|101|C01|A|
|101|C02|B|
|102|C01|A|

The `Enrollments` table uses `(Student ID, Course ID)` as its composite primary key. Grade depends on the complete key.

## 3NF - Third Normal Form
A table is in Third Normal Form if:

1. It is already in 2NF.
2. For every non-trivial functional dependency (X \rightarrow A), either (X) is a superkey or (A) is a prime attribute (an attribute belonging to at least one candidate key).    

A useful introductory rule is to eliminate transitive dependencies of non-key attributes on candidate keys.

### Example

Consider an employee table.

|Employee ID (PK)|Employee Name|Department ID|Department Name|
|---|---|---|---|
|E01|Arun|D01|Engineering|
|E02|Bala|D02|Finance|
|E03|Chitra|D01|Engineering|

Assume each department has exactly one department name.

The functional dependencies are:

- `Employee ID → Employee Name, Department ID`
- `Department ID → Department Name`

Therefore:
`Employee ID → Department ID → Department Name`
Department Name depends on Employee ID through Department ID. It is a transitive dependency, and Department Name is repeated for every employee in the same department.

Converting to 3NF:

**Employees**

|Employee ID (PK)|Employee Name|Department ID (FK)|
|---|---|---|
|E01|Arun|D01|
|E02|Bala|D02|
|E03|Chitra|D01|

**Departments**

|Department ID (PK)|Department Name|
|---|---|
|D01|Engineering|
|D02|Finance|


## BCNF - Boyce-Codd Normal Form

BCNF is a stricter version of 3NF. A table is in BCNF if, for every non-trivial functional dependency (X \rightarrow Y), (X) is a superkey. Unlike 3NF, BCNF does not provide an exception for a dependency whose right-hand-side attribute is prime.

### Example
Suppose instructors can teach multiple courses, but each instructor teaches in only one room. A course can have multiple instructors, and each instructor-course assignment is recorded.

| Student ID | Course | Instructor | Room |
| ---------- | ------ | ---------- | ---- |
| S01        | SQL    | Ravi       | R101 |
| S02        | SQL    | Ravi       | R101 |
| S01        | Python | Meera      | R202 |

For a simplified version of this example, assume:

- `(Student ID, Course) → Instructor`    
- `Instructor → Room`

Also assume a student can take multiple courses and a course may have multiple students.

The candidate key is `(Student ID, Course)`, while `Instructor → Room` holds because each instructor has one room. Instructor alone is not a superkey of the original table, so this dependency violates BCNF.

### Example
Separate instructor room assignments from student-course enrolments.

**Instructor Rooms**

| Instructor (PK) | Room |
| --------------- | ---- |
| Ravi            | R101 |
| Meera           | R202 |

**Student Courses**

|Student ID|Course|Instructor|
|---|---|---|
|S01|SQL|Ravi|
|S02|SQL|Ravi|
|S01|Python|Meera|

In `Instructor Rooms`, Instructor determines Room and is the primary key. In `Student Courses`, the key is `(Student ID, Course)`, under the stated assumptions. This decomposition is lossless for the stated dependencies and preserves the instructor-room dependency.
## 4NF - Fourth Normal Form

A table is in Fourth Normal Form if it is already in BCNF and has no non-trivial multivalued dependency (X -> Y) unless (X) is a superkey. Multivalued dependencies arise when two or more independent sets of values are associated with the same entity.
### Example

Suppose an employee has multiple skills and multiple languages, and the skills are independent of the languages.

| Employee ID | Skill  | Language |
| ----------- | ------ | -------- |
| E01         | Python | English  |
| E01         | Python | Japanese |
| E01         | SQL    | English  |
| E01         | SQL    | Japanese |

The employee has two skills and two languages. All four combinations appear because the two relationships are independent.

The dependencies are:

- `Employee ID →→ Skill`
- `Employee ID →→ Language`

The employee ID alone is not a superkey of the combined table, so these independent multivalued dependencies violate 4NF.

### Convert to 4NF

**Employee Skills**

|Employee ID|Skill|
|---|---|
|E01|Python|
|E01|SQL|

**Employee Languages**

| Employee ID | Language |
| ----------- | -------- |
| E01         | English  |
| E01         | Japanese |
## Fifth Normal Form (5NF)

Fifth Normal Form, also called Project-Join Normal Form (PJ/NF), addresses redundancy caused by join dependencies that cannot be explained adequately by ordinary functional or multivalued dependencies. A table is in 5NF if every non-trivial join dependency is implied by its candidate keys.

### Example
Consider a supplier, part, and project relationship. Suppose the business rules guarantee that a supplier can supply a part to a project whenever all three of the following pairwise relationships exist:

- The supplier supplies the part.
- The supplier is approved for the project.
- The project uses the part.

Under this specific rule, the ternary relationship can be reconstructed from three pairwise relationships.

**Supplier-Part-Project**

|Supplier|Part|Project|
|---|---|---|
|S1|P1|J1|
|S1|P1|J2|
|S1|P2|J1|

Assume the complete set of valid triples is exactly the join of the three pairwise relationships described below. Without this business rule, decomposing the table this way could create invalid combinations.

After converting to 5NF:

**Supplier-Part**

|Supplier|Part|
|---|---|
|S1|P1|
|S1|P2|

**Supplier-Project**

|Supplier|Project|
|---|---|
|S1|J1|
|S1|J2|

**Project-Part**

|Project|Part|
|---|---|
|J1|P1|
|J1|P2|
|J2|P1|

Joining these three tables reconstructs the original triples under the stated business rule.

## Summary: All Normal Forms

|Normal Form|Main Requirement|Problem Addressed|
|---|---|---|
|1NF|Atomic column values; no repeating groups|Multivalued cells and repeating groups|
|2NF|1NF + no partial dependency of non-prime attributes on a candidate key|Partial dependencies on composite keys|
|3NF|For every non-trivial FD, determinant is a superkey or dependent is prime|Transitive dependencies in common cases|
|BCNF|Every determinant of a non-trivial functional dependency is a superkey|Remaining functional-dependency anomalies|
|4NF|Every non-trivial multivalued dependency has a superkey as determinant|Independent multivalued relationships|
|5NF|Every non-trivial join dependency is implied by candidate keys|Join-dependency redundancy|

Normalization does not necessarily mean that every possible table should be decomposed as much as possible. Excessive decomposition may require more joins and can complicate query execution. In read-heavy systems, carefully chosen denormalization may be justified for performance, provided consistency is maintained.

The central principle is to ensure that each fact is stored in the appropriate relation, dependencies are represented correctly, and decompositions preserve information and, where possible, the relevant constraints.