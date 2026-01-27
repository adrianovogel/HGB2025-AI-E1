from pyspark.sql import SparkSession
from pyspark.sql.functions import (
    col, from_json, lower, count, window, to_timestamp
)
from pyspark.sql.types import StructType, StructField, StringType, LongType

# 1. Configuration & Session Setup
CHECKPOINT_PATH = "/tmp/spark-checkpoints/logs-processing"

spark = (
    SparkSession.builder
    .appName("LogsProcessor")
    .config("spark.sql.streaming.checkpointLocation", CHECKPOINT_PATH)
    .getOrCreate()
)
spark.sparkContext.setLogLevel("ERROR")

# 2. Define schema
schema = StructType([
    StructField("timestamp", LongType()),
    StructField("status", StringType()),
    StructField("severity", StringType()),
    StructField("source_ip", StringType()),
    StructField("user_id", StringType()),
    StructField("content", StringType())
])

# 3. Read Stream (Kafka)
raw_df = (
    spark.readStream
    .format("kafka")
    .option("kafka.bootstrap.servers", "kafka:9092")
    .option("subscribe", "logs")
    .option("startingOffsets", "earliest")
    .option("failOnDataLoss", "false")
    .load()
)

# 4. Parse JSON and converting event time timestamp
parsed_df = (
    raw_df
    .select(from_json(col("value").cast("string"), schema).alias("data"))
    .select("data.*")
)

# If timestamp is in milliseconds, divide by 1000.
# If it's already in seconds, remove the "/ 1000".
events_df = parsed_df.withColumn(
    "event_time",
    to_timestamp((col("timestamp") / 1000).cast("double"))
)

# 5. Activity 3 logic:
# - content contains "crash" (case-insensitive)
# - severity is High or Critical
# - group by user_id and 10s event-time windows
# - output only crash_count > 2
result_df = (
    events_df
    .filter(
        lower(col("content")).contains("crash") &
        (col("severity").isin("High", "Critical"))
    )
    .withWatermark("event_time", "30 seconds")
    .groupBy(
        window(col("event_time"), "10 seconds").alias("interval"),
        col("user_id")
    )
    .agg(count("*").alias("crash_count"))
    .filter(col("crash_count") > 2)
    .select(
        col("interval"),
        col("user_id"),
        col("crash_count")
    )
)

# 6. Writing
# "append" works when watermark is present for windowed aggregations
query = (
    result_df.writeStream
    .outputMode("append")
    .format("console")
    .option("truncate", "false")
    .start()
)

query.awaitTermination()
