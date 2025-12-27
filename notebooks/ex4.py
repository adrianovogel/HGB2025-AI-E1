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

