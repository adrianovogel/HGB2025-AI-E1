# Part 1 — Environment Setup and Basics

## 1. Start the environment

Download the repository and start the environment:

```bash
docker compose up -d
```

## 2. Access PostgreSQL

```bash
docker exec -it pg-bigdata psql -U postgres
```

## 3. Load and query data in PostgreSQL

### 3.1 Create a large dataset

```bash
cd data
python3 expand.py
```

Creates `data/people_1M.csv` with ~1 million rows.

```bash
wc -l people_1M.csv
```

### 3.2 Enter PostgreSQL

```bash
docker exec -it pg-bigdata psql -U postgres
```

### 3.3 Create and load the table

```sql
DROP TABLE IF EXISTS people_big;

CREATE TABLE people_big (
  id SERIAL PRIMARY KEY,
  first_name TEXT,
  last_name TEXT,
  gender TEXT,
  department TEXT,
  salary INTEGER,
  country TEXT
);

\COPY people_big(first_name,last_name,gender,department,salary,country)
FROM '/data/people_1M.csv' DELIMITER ',' CSV HEADER;
```

### 3.4 Enable timing

```sql
\timing on
```

## 4. Verification

```sql
SELECT COUNT(*) FROM people_big;
SELECT * FROM people_big LIMIT 10;
```

```output

  count
---------
 1000000
(1 row)

Time: 129.244 ms
 id | first_name | last_name | gender |     department     | salary |   country
----+------------+-----------+--------+--------------------+--------+--------------
  1 | Andreas    | Scott     | Male   | Audit              |  69144 | Bosnia
  2 | Tim        | Lopez     | Male   | Energy Management  |  62082 | Taiwan
  3 | David      | Ramirez   | Male   | Quality Assurance  |  99453 | South Africa
  4 | Victor     | Sanchez   | Male   | Level Design       |  95713 | Cuba
  5 | Lea        | Edwards   | Female | Energy Management  |  60425 | Iceland
  6 | Oliver     | Baker     | Male   | Payroll            |  74110 | Poland
  7 | Emily      | Lopez     | Female | SOC                |  83526 | Netherlands
  8 | Tania      | King      | Female | IT                 |  95142 | Thailand
  9 | Max        | Hernandez | Male   | Workforce Planning | 101198 | Latvia
 10 | Juliana    | Harris    | Female | Compliance         | 103336 | Chile

```

## 5. Analytical queries

### (a) Simple aggregation

```sql
SELECT department, AVG(salary)
FROM people_big
GROUP BY department
LIMIT 10;
```

```output

      department       |         avg
-----------------------+---------------------
 Accounting            |  85150.560834888851
 Alliances             |  84864.832756437315
 Analytics             | 122363.321232406454
 API                   |  84799.041690986409
 Audit                 |  84982.559610499577
 Backend               |  84982.349086542585
 Billing               |  84928.436430727944
 Bioinformatics        |  85138.080510264425
 Brand                 |  85086.881434454358
 Business Intelligence |  85127.097446808511

```

### (b) Nested aggregation

```sql
SELECT country, AVG(avg_salary)
FROM (
  SELECT country, department, AVG(salary) AS avg_salary
  FROM people_big
  GROUP BY country, department
) sub
GROUP BY country
LIMIT 10;
```

```output
  country   |        avg
------------+--------------------
 Algeria    | 87230.382040504578
 Argentina  | 86969.866763623360
 Armenia    | 87245.059590528218
 Australia  | 87056.715662987876
 Austria    | 87127.824046597584
 Bangladesh | 87063.832793583033
 Belgium    | 86940.103641985310
 Bolivia    | 86960.615658334041
 Bosnia     | 87102.274664951815
 Brazil     | 86977.731228862018
```

### (c) Top-N sort

```sql
SELECT *
FROM people_big
ORDER BY salary DESC
LIMIT 10;
```

```output

   id   | first_name | last_name | gender |    department    | salary |   country
--------+------------+-----------+--------+------------------+--------+--------------
 764650 | Tim        | Jensen    | Male   | Analytics        | 160000 | Bulgaria
  10016 | Anastasia  | Edwards   | Female | Analytics        | 159998 | Kuwait
 754528 | Adrian     | Young     | Male   | Game Analytics   | 159997 | UK
 893472 | Mariana    | Cook      | Female | People Analytics | 159995 | South Africa
 240511 | Diego      | Lopez     | Male   | Game Analytics   | 159995 | Malaysia
 359891 | Mariana    | Novak     | Female | Game Analytics   | 159992 | Mexico
  53102 | Felix      | Taylor    | Male   | Data Science     | 159989 | Bosnia
 768143 | Teresa     | Campbell  | Female | Game Analytics   | 159988 | Spain
 729165 | Antonio    | Weber     | Male   | Analytics        | 159987 | Moldova
 952549 | Adrian     | Harris    | Male   | Analytics        | 159986 | Georgia
```

# Part 2 — Exercises

## Exercise 1 - PostgreSQL Analytical Queries (E-commerce)

In the `ecommerce` folder:

1. Generate a new dataset by running the provided Python script.
2. Load the generated data into PostgreSQL in a **new table**.

Using SQL ([see the a list of supported SQL commands](https://www.postgresql.org/docs/current/sql-commands.html)), answer the following questions:

**A.** What is the single item with the highest `price_per_unit`?

```
 customer_name | product_category | price_per_unit
---------------+------------------+----------------
 Emma Brown    | Automotive       |        2000.00
```

**B.** What are the top 3 products with the highest total quantity sold across all orders?

```
 product_category | total_qty
------------------+-----------
 Health & Beauty  |    300842
 Electronics      |    300804
 Toys             |    300598
```

**C.** What is the total revenue per product category?  
(Revenue = `price_per_unit × quantity`)

```
 product_category | total_revenue
------------------+---------------
 Automotive       |  306589798.86
 Electronics      |  241525009.45
 Home & Garden    |   78023780.09
 Sports           |   61848990.83
 Health & Beauty  |   46599817.89
 Office Supplies  |   38276061.64
 Fashion          |   31566368.22
 Toys             |   23271039.02
 Grocery          |   15268355.66
 Books            |   12731976.04
```

**D.** Which customers have the highest total spending?

```
 customer_name  | total_spent
----------------+-------------
 Carol Taylor   |   991179.18
 Nina Lopez     |   975444.95
 Daniel Jackson |   959344.48
 Carol Lewis    |   947708.57
 Daniel Young   |   946030.14
 Alice Martinez |   935100.02
 Ethan Perez    |   934841.24
 Leo Lee        |   934796.48
 Eve Young      |   933176.86
 Ivy Rodriguez  |   925742.64
```


## Exercise 2
Assuming there are naive joins executed by users, such as:
```sql
SELECT COUNT(*)
FROM people_big p1
JOIN people_big p2
  ON p1.country = p2.country;
```
## Problem Statement

This query takes more than **10 minutes** to complete, significantly slowing down the entire system. Additionally, the **OLTP database** currently in use has inherent limitations in terms of **scalability and efficiency**, especially when operating in **large-scale cloud environments**.

## Discussion Question

Considering the requirements for **scalability** and **efficiency**, what **approaches and/or optimizations** can be applied to improve the system’s:

- Scalability  
- Performance  
- Overall efficiency  

Please **elaborate with a technical discussion**.

> **Optional:** Demonstrate your proposed solution in practice (e.g., architecture diagrams, SQL examples, or code snippets).

Here is a **compact, technical, assignment-ready answer** you can paste directly under **Exercise 2**. It is short, clear, and addresses **scalability, performance, and efficiency** without unnecessary detail.

---

## Solution

The given query performs a self-join on the "people_big" table using a low-cardinality attribute "country". This causes a quadratic explosion of intermediate results, as all rows within the same country are paired with each other (n × n per country). With a dataset of 1,000,000 rows, this leads to extremely high execution time and system load.

**Query optimization**
If only aggregated results are required, the join can be avoided entirely by using pre-aggregation:

```sql
SELECT SUM(cnt::bigint * cnt::bigint)
FROM (
  SELECT country, COUNT(*) AS cnt
  FROM people_big
  GROUP BY country
) s;
```

This reduces the complexity from quadratic to linear.

**Database optimizations**

* Create indexes on join keys to reduce scan cost.
* Apply table partitioning to improve data locality and parallelism.

**Conclusion**
The main performance issue is caused by an inefficient query pattern rather than missing indexes. Avoiding unnecessary joins and separating OLTP from analytical workloads significantly improves scalability, performance, and efficiency.

---

## Exercise 3
## Run with Spark (inside Jupyter)

Open your **Jupyter Notebook** environment:

- **URL:** http://localhost:8888/?token=lab  
- **Action:** Create a new notebook

Then run the following **updated Spark example**, which uses the same data stored in **PostgreSQL**.

---

## Spark Example Code

```python
# ============================================
# 0. Imports & Spark session
# ============================================

import time
import builtins  # <-- IMPORTANT
from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    avg,
    round as spark_round,   # Spark round ONLY for Columns
    count,
    col,
    sum as _sum
)

spark = (
    SparkSession.builder
    .appName("PostgresVsSparkBenchmark")
    .config("spark.jars.packages", "org.postgresql:postgresql:42.7.2")
    .config("spark.eventLog.enabled", "true")
    .config("spark.eventLog.dir", "/tmp/spark-events")
    .config("spark.history.fs.logDirectory", "/tmp/spark-events")
    .config("spark.sql.shuffle.partitions", "4")
    .config("spark.default.parallelism", "4")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

# ============================================
# 1. JDBC connection config
# ============================================

jdbc_url = "jdbc:postgresql://postgres:5432/postgres"
jdbc_props = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}

# ============================================
# 2. Load data from PostgreSQL
# ============================================

print("\n=== Loading people_big from PostgreSQL ===")

start = time.time()

df_big = spark.read.jdbc(
    url=jdbc_url,
    table="people_big",
    properties=jdbc_props
)

# Force materialization
row_count = df_big.count()

print(f"Rows loaded: {row_count}")
print("Load time:", builtins.round(time.time() - start, 2), "seconds")

# Register temp view
df_big.createOrReplaceTempView("people_big")

# ============================================
# 3. Query (a): Simple aggregation
# ============================================

print("\n=== Query (a): AVG salary per department ===")

start = time.time()

q_a = (
    df_big
    .groupBy("department")
    .agg(spark_round(avg("salary"), 2).alias("avg_salary"))
    .orderBy("department", ascending=False)
    .limit(10)
)

q_a.collect()
q_a.show(truncate=False)
print("Query (a) time:", builtins.round(time.time() - start, 2), "seconds")

# ============================================
# 4. Query (b): Nested aggregation
# ============================================

print("\n=== Query (b): Nested aggregation ===")

start = time.time()

q_b = spark.sql("""
SELECT country, AVG(avg_salary) AS avg_salary
FROM (
    SELECT country, department, AVG(salary) AS avg_salary
    FROM people_big
    GROUP BY country, department
) sub
GROUP BY country
ORDER BY avg_salary DESC
LIMIT 10
""")

q_b.collect()
q_b.show(truncate=False)
print("Query (b) time:", builtins.round(time.time() - start, 2), "seconds")

# ============================================
# 5. Query (c): Sorting + Top-N
# ============================================

print("\n=== Query (c): Top 10 salaries ===")

start = time.time()

q_c = (
    df_big
    .orderBy(col("salary").desc())
    .limit(10)
)

q_c.collect()
q_c.show(truncate=False)
print("Query (c) time:", builtins.round(time.time() - start, 2), "seconds")

# ============================================
# 6. Query (d): Heavy self-join (COUNT only)
# ============================================

print("\n=== Query (d): Heavy self-join COUNT (DANGEROUS) ===")

start = time.time()

q_d = (
    df_big.alias("p1")
    .join(df_big.alias("p2"), on="country")
    .count()
)

print("Join count:", q_d)
print("Query (d) time:", builtins.round(time.time() - start, 2), "seconds")

# ============================================
# 7. Query (d-safe): Join-equivalent rewrite
# ============================================

print("\n=== Query (d-safe): Join-equivalent rewrite ===")

start = time.time()

grouped = df_big.groupBy("country").agg(count("*").alias("cnt"))

q_d_safe = grouped.select(
    _sum(col("cnt") * col("cnt")).alias("total_pairs")
)

q_d_safe.collect()
q_d_safe.show()
print("Query (d-safe) time:", builtins.round(time.time() - start, 2), "seconds")

# ============================================
# 8. Cleanup
# ============================================

spark.stop()
```
## Analysis and Discussion

Now, explain in your own words:

- **What the Spark code does:**  
  Describe the workflow, data loading, and the types of queries executed (aggregations, sorting, self-joins, etc.).

- **Architectural contrasts with PostgreSQL:**  
  Compare the Spark distributed architecture versus PostgreSQL’s single-node capabilities, including scalability, parallelism, and data processing models.

- **Advantages and limitations:**  
  Highlight the benefits of using Spark for large-scale data processing (e.g., in-memory computation, distributed processing) and its potential drawbacks (e.g., setup complexity, overhead for small datasets).

- **Relation to Exercise 2:**  
  Connect this approach to the concepts explored in Exercise 2, such as performance optimization and scalability considerations.

## Exercise 3 - Solution

# Terminal Output 

```
=== Loading people_big from PostgreSQL ===
Rows loaded: 1000000
Load time: 15.69 seconds

=== Query (a): AVG salary per department ===
+------------------+----------+
|department        |avg_salary|
+------------------+----------+
|Workforce Planning|85090.82  |
|Web Development   |84814.36  |
|UX Design         |84821.2   |
|UI Design         |85164.64  |
|Treasury          |84783.27  |
|Training          |85148.1   |
|Tax               |85018.57  |
|Sustainability    |85178.99  |
|Supply Chain      |84952.89  |
|Subscriptions     |84899.19  |
+------------------+----------+

Query (a) time: 8.25 seconds

=== Query (b): Nested aggregation ===
+------------+-----------------+
|country     |avg_salary       |
+------------+-----------------+
|Egypt       |87382.229633112  |
|Kuwait      |87349.3517377211 |
|Saudi Arabia|87348.80512175433|
|Panama      |87345.00623707911|
|Denmark     |87328.03514120901|
|Jamaica     |87305.437352083  |
|Lebanon     |87292.76891750695|
|Turkey      |87290.69043798617|
|Malaysia    |87253.78746341489|
|Kazakhstan  |87251.74274968785|
+------------+-----------------+

Query (b) time: 8.62 seconds

=== Query (c): Top 10 salaries ===
+------+----------+---------+------+----------------+------+------------+
|id    |first_name|last_name|gender|department      |salary|country     |
+------+----------+---------+------+----------------+------+------------+
|764650|Tim       |Jensen   |Male  |Analytics       |160000|Bulgaria    |
|10016 |Anastasia |Edwards  |Female|Analytics       |159998|Kuwait      |
|754528|Adrian    |Young    |Male  |Game Analytics  |159997|UK          |
|240511|Diego     |Lopez    |Male  |Game Analytics  |159995|Malaysia    |
|893472|Mariana   |Cook     |Female|People Analytics|159995|South Africa|
|359891|Mariana   |Novak    |Female|Game Analytics  |159992|Mexico      |
|53102 |Felix     |Taylor   |Male  |Data Science    |159989|Bosnia      |
|768143|Teresa    |Campbell |Female|Game Analytics  |159988|Spain       |
|729165|Antonio   |Weber    |Male  |Analytics       |159987|Moldova     |
|952549|Adrian    |Harris   |Male  |Analytics       |159986|Georgia     |
+------+----------+---------+------+----------------+------+------------+

Query (c) time: 16.39 seconds

=== Query (d): Heavy self-join COUNT (DANGEROUS) ===
Join count: 10983941260
Query (d) time: 27.29 seconds

=== Query (d-safe): Join-equivalent rewrite ===
+-----------+
|total_pairs|
+-----------+
|10983941260|
+-----------+

Query (d-safe) time: 2.37 seconds
```
## Analysis and Discussion

# Spark workflow and executed queries
The Spark application connects to PostgreSQL via JDBC and loads the people_big table into a Spark DataFrame. Once loaded, the data is processed in memory using Spark’s distributed execution model. The code executes multiple analytical queries, including simple aggregations (average salary per department), nested aggregations (average salary per country based on department level averages), sorting operations (top salaries), and a self-join operation on the country attribute. Additionally, an optimized rewrite of the self join is implemented using pre aggregation to avoid generating large intermediate results.

# Architectural contrast with PostgreSQL
PostgreSQL operates primarily as a single node OLTP database optimized for transactional workloads, where complex analytical queries and large joins can become performance bottlenecks. Spark, in contrast, is a distributed data processing engine that parallelizes computation across multiple executors and processes data in memory. This allows Spark to scale horizontally and handle large analytical workloads more efficiently, especially when dealing with full table scans and aggregations.

# Advantages and limitations of Spark
Spark’s main advantages include distributed processing, in-memory computation, and efficient execution of large scale analytical queries. These characteristics make it well suited for data intensive workloads and batch analytics. However, Spark introduces additional setup complexity and runtime overhead, which may not be justified for small datasets or simple transactional queries where a traditional database like PostgreSQL is sufficient.

# Relation to Exercise 2
This exercise directly extends the concepts from Exercise 2 by demonstrating the impact of inefficient query patterns, such as naive self joins, at scale. While Spark can handle large workloads better than PostgreSQL, the experiment shows that poor query design still leads to high execution times. The optimized rewrite using pre aggregation achieves the same result significantly faster, reinforcing the importance of query optimization and scalable design regardless of the underlying system.


## Exercise 4
Port the SQL queries from exercise 1 to spark.

## Exercise 4 — Port Exercise 1 SQL queries to Spark

### Spark code (JDBC load + queries)

```python
import time
import builtins
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, sum as _sum, max as _max

spark = (
    SparkSession.builder
    .appName("EcommerceQueriesSpark")
    .config("spark.jars.packages", "org.postgresql:postgresql:42.7.2")
    .getOrCreate()
)

spark.sparkContext.setLogLevel("WARN")

jdbc_url = "jdbc:postgresql://postgres:5432/postgres"
jdbc_props = {
    "user": "postgres",
    "password": "postgres",
    "driver": "org.postgresql.Driver"
}

# Load ecommerce orders table from PostgreSQL
df_orders = spark.read.jdbc(url=jdbc_url, table="orders_1m", properties=jdbc_props)
df_orders.createOrReplaceTempView("orders_1m")

print("Rows loaded:", df_orders.count())

# A) Highest price_per_unit
print("\n=== (A) Highest price_per_unit ===")
q_a = spark.sql("""
SELECT customer_name, product_category, price_per_unit
FROM orders_1m
ORDER BY price_per_unit DESC
LIMIT 1
""")
q_a.show(truncate=False)

# B) Top 3 categories by total quantity sold
print("\n=== (B) Top 3 categories by total quantity ===")
q_b = spark.sql("""
SELECT product_category, SUM(quantity) AS total_qty
FROM orders_1m
GROUP BY product_category
ORDER BY total_qty DESC
LIMIT 3
""")
q_b.show(truncate=False)

# C) Total revenue per category
print("\n=== (C) Total revenue per category ===")
q_c = spark.sql("""
SELECT product_category,
       SUM(price_per_unit * quantity) AS total_revenue
FROM orders_1m
GROUP BY product_category
ORDER BY total_revenue DESC
""")
q_c.show(truncate=False)

# D) Top customers by total spending
print("\n=== (D) Top customers by total spending ===")
q_d = spark.sql("""
SELECT customer_name,
       SUM(price_per_unit * quantity) AS total_spent
FROM orders_1m
GROUP BY customer_name
ORDER BY total_spent DESC
LIMIT 10
""")
q_d.show(truncate=False)

spark.stop()
```

## Spark output

```
=== (A) Highest price_per_unit ===
+-------------+----------------+--------------+
|customer_name|product_category|price_per_unit|
+-------------+----------------+--------------+
|Emma Brown   |Automotive      |2000.00       |
+-------------+----------------+--------------+


=== (B) Top 3 categories by total quantity ===
+----------------+---------+
|product_category|total_qty|
+----------------+---------+
|Health & Beauty |300842   |
|Electronics     |300804   |
|Toys            |300598   |
+----------------+---------+


=== (C) Total revenue per category ===
+----------------+-------------+
|product_category|total_revenue|
+----------------+-------------+
|Automotive      |306589798.86 |
|Electronics     |241525009.45 |
|Home & Garden   |78023780.09  |
|Sports          |61848990.83  |
|Health & Beauty |46599817.89  |
|Office Supplies |38276061.64  |
|Fashion         |31566368.22  |
|Toys            |23271039.02  |
|Grocery         |15268355.66  |
|Books           |12731976.04  |
+----------------+-------------+


=== (D) Top customers by total spending ===
+--------------+-----------+
|customer_name |total_spent|
+--------------+-----------+
|Carol Taylor  |991179.18  |
|Nina Lopez    |975444.95  |
|Daniel Jackson|959344.48  |
|Carol Lewis   |947708.57  |
|Daniel Young  |946030.14  |
|Alice Martinez|935100.02  |
|Ethan Perez   |934841.24  |
|Leo Lee       |934796.48  |
|Eve Young     |933176.86  |
|Ivy Rodriguez |925742.64  |
+--------------+-----------+
```

The Spark results match the PostgreSQL results from Exercise 1, confirming the correctness of the ported queries.