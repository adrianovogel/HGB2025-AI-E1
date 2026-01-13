# Part 1 — Environment Setup and Basics

## 1. Start the environment

Download the repository and start the environment:

```bash
docker compose up -d
```

Check if the **four containers** are running:
- postgres
- kafka
- kafka-ui
- connect

## 2. Access PostgreSQL

```bash
docker exec -it postgres psql -U postgres
```


# Kafka Quick Start (Docker)

## A. Check Kafka is running
```bash
docker ps
```
**Explanation**  
Confirms that the Kafka broker container is running and shows its container name (e.g. `kafka`).

---

## B. Create a topic with multiple partitions
```bash
docker exec -it kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --create \
  --topic activity.streaming \
  --partitions 4 \
  --replication-factor 1
```
**Explanation**
- `--topic`: Name of the Kafka topic  
- `--partitions 4`: Creates three partitions to allow parallelism  
- `--replication-factor 1`: One replica per partition (suitable for local development)

---

## C. List all topics
```bash
docker exec -it kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --list
```
**Explanation**  
Displays all topics currently available in the Kafka cluster.

---

## D. Describe a topic
```bash
docker exec -it kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --topic activity.streaming
```
**Explanation**  
Shows partition count, leaders, replicas, and in-sync replicas (ISR).

---

## E. List topic configuration
```bash
docker exec -it kafka kafka-configs.sh \
  --bootstrap-server localhost:9092 \
  --entity-type topics \
  --entity-name activity.streaming \
  --describe
```
**Explanation**  
Displays topic-level configurations such as retention and cleanup policies.  
Configurations not listed inherit Kafka broker defaults.

---

## F. Produce messages to the topic

### F.1 Basic producer
```bash
docker exec -it kafka kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic activity.streaming
```

Example input:
```text
{"id":1,"name":"Alice"}
{"id":2,"name":"Bob"}
```

**Explanation**  
Messages are distributed across partitions in a round-robin fashion when no key is provided.

---

### F.2 Producer with keys
```bash
docker exec -it kafka kafka-console-producer.sh \
  --bootstrap-server localhost:9092 \
  --topic activity.streaming \
  --property parse.key=true \
  --property key.separator=:
```

Example input:
```text
1:{"id":1,"name":"Alice"}
1:{"id":1,"name":"Alice-updated"}
2:{"id":2,"name":"Bob"}
```

**Explanation**  
Messages with the same key are routed to the same partition, preserving per-key ordering.

---

## G. Consume messages from the topic

### G.1 Consume from the beginning
```bash
docker exec -it kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic activity.streaming \
  --from-beginning
```

**Explanation**  
Reads all messages from the beginning of the topic.

---

### G.2 Consume using a consumer group
```bash
docker exec -it kafka kafka-console-consumer.sh \
  --bootstrap-server localhost:9092 \
  --topic activity.streaming \
  --group customers-service
```

**Explanation**  
Consumers in the same group share partitions and automatically commit offsets.

---

## H. Inspect consumer group status
```bash
docker exec -it kafka kafka-consumer-groups.sh \
  --bootstrap-server localhost:9092 \
  --describe \
  --group customers-service
```

**Explanation**  
Shows partition assignments, current offsets, and consumer lag.

---

## I. Delete the topic (optional)
```bash
docker exec -it kafka kafka-topics.sh \
  --bootstrap-server localhost:9092 \
  --delete \
  --topic activity.streaming
```

**Explanation**  
Deletes the topic and all stored data (requires `delete.topic.enable=true` on the broker).



# Debezium CDC with PostgreSQL and Kafka


## Verify the services
- Kafka UI: http://localhost:8080  
- Connector plugins endpoint: http://localhost:8083/connector-plugins  

Ensure that the Connect service responds successfully.

## Example: Insert a row in PostgreSQL

### Create a new database
```sql
CREATE DATABASE activity;
```

### Connect to the new database
```sql
\c activity
```

### Create the table
```sql
CREATE TABLE activity (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255)
);
```

## Register the Debezium Connector

The Docker Compose file only starts the Kafka Connect engine.  
You must explicitly register a Debezium connector so it starts watching PostgreSQL.

In **another terminal**, run:

```bash
curl -i -X POST   -H "Accept:application/json"   -H "Content-Type:application/json"   localhost:8083/connectors/   -d '{
    "name": "activity-connector",
    "config": {
      "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
      "tasks.max": "1",
      "database.hostname": "postgres",
      "database.port": "5432",
      "database.user": "postgres",
      "database.password": "postgrespw",
      "database.dbname": "activity",
      "slot.name": "activityslot",
      "topic.prefix": "dbserver1",
      "plugin.name": "pgoutput",
      "database.replication.slot.name": "debeziumactivity"
    }
  }'
```

### Check Debezium status
The connector and its tasks should be in the `RUNNING` state:

```bash
curl -s http://localhost:8083/connectors/activity-connector/status | jq
```

In the Kafka UI (http://localhost:8080), verify that new topics appear.

Ouput:
```bash
{"name":"activity-connector","connector":{"state":"RUNNING","worker_id":"172.22.0.4:8083"},"tasks":[{"id":0,"state":"RUNNING","worker_id":"172.22.0.4:8083"}],"type":"source"}
```

## Insert a record into PostgreSQL

Back in the PostgreSQL console, insert a record:

```sql
INSERT INTO activity(id, name) VALUES (1, 'Alice');
```

Debezium will produce a Kafka message on the topic:

```
dbserver1.public.activity
```

With a payload similar to:

```json
{
  "op": "c",
  "after": {
    "id": 1,
    "name": "Alice"
  }
}
```

## Consume from the Kafka topic

```bash
docker exec -it kafka kafka-console-consumer.sh   --bootstrap-server localhost:9092   --topic dbserver1.public.activity  --from-beginning
```

# Activity 1
Considering the above part ```Debezium CDC with PostgreSQL and Kafka```, explain with your own words what it does and why it is a relevant software architecture for Big Data in the AI era and for which use cases.

# Answer - Activity 1
Debezium reads PostgreSQL’s WAL (write-ahead log) and converts each database change (insert,update and delete) into an event in Kafka. That means consumers dont need to constantly query the database. they can subscribe to Kafka topics and react immediately. This is relevant for Big Data in the AI because it enables real time pipelines, multiple independent consumers (feature stores, fraud detection, monitoring, dashboards), and scalable streaming without overloading the OLTP database.

# Activity 2
## Scenario:
You run a temperature logging system in a small office. Sensors report the temperature once per minute and write the sensor readings into a PostgreSQL table

## Running instructions
It is recommended to run the scripts (e.g., ```temperature_data_producer.py``` file) in a Python virtual environments venv, basic commands from the ```activity.streaming``` folder:
```bash
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
```
Then one can run the python scripts.

## Characteristics:

Low volume (~1 row per minute)

Single consumer (reporting script)

No real-time streaming needed

## Part 1
In a simple use case where sensor readings need to be processed every 10 minutes to calculate the average temperature over that time window, describe which software architecture would be most appropriate for fetching the data from PostgreSQL, and explain the rationale behind your choice.

## Part 2
From the architectural choice made in ```Part 1```, implement the solution to consume and processing the data generated by the ```temperature_data_producer.py``` file (revise its features!). The basic logic from the file ```temperature_data_consumer.py``` should be extended with the conection to data source defined in ```Part 1```'s architecture..

```bash
$ python ./temperature_data_producer.py
```

Output:

```bash
2026-01-13 23:27:19.168196 - Inserted temperature: 27.3 °C
2026-01-13 23:28:19.175509 - Inserted temperature: 25.26 °C
2026-01-13 23:29:19.180460 - Inserted temperature: 26.71 °C
2026-01-13 23:30:19.186248 - Inserted temperature: 25.8 °C
```


```bash
python temperature_data_consumer.py
```

Ouput:
```bash
2026-01-13 23:44:25.851127 - Average temperature last 10 minutes: 22.87 °C
```

## Part 3
Discuss the proposed architecture in terms of resource efficiency, operability, and deployment complexity. This includes analyzing how well the system utilizes compute, memory, and storage resources; how easily it can be operated, monitored, and debugged in production.

## Part 3 — Architecture Discussion

This architecture is resource-efficient because it processes low data volumes using simple batch queries, requiring minimal CPU, memory, and storage. It is easy to operate and debug due to its small number of components and straightforward logic. Deployment is simple, relying only on PostgreSQL and Python, making it suitable for small-scale, non–real-time use cases.

# Activity 3
## Scenario:
A robust fraud detection system operating at high scale must be designed to handle extremely high data ingestion rates while enabling near real-time analysis by multiple independent consumers. In this scenario, potentially hundreds of thousands of transactional records per second are continuously written into an OLTP PostgreSQL database (see an example simulating it with a data generator inside the folder ```Activity3```), which serves as the system of record and guarantees strong consistency, durability, and transactional integrity. Moreover, the records generated are needed by many consumers in near real-time (see inside the folder ```Activity3``` two examples simulating agents consuming the records and generating alerts).  Alerts or enriched events generated by these agents can then be forwarded to downstream systems, such as alerting services, dashboards, or case management tools.

## Running instructions
It is recommended to run the scripts in a Python virtual environments venv, basic commands from the ```Activity3``` folder:
```bash
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install --upgrade pip
pip install -r requirements.txt
```
Then one can run the python scripts.

## Characteristics:

High data volume (potentially hundreds of thousands of records per second)

Multiple consumer agents

Near real-time streaming needed

## Part 1

Describe which software architecture would be most appropriate for fetching the data from PostgreSQL and generate alerts in real-time. Explain the rationale behind your choice.

## Activity 3 - part 1
Best architecture wist real-time alerts

- PostgreSQL (OLTP) → Debezium (CDC) → Kafka → multiple consumer agents.

- Postgres stays the system of record (ACID, durability).

- Debezium streams row-level changes as events (no polling queries).

- Kafka buffers + fans out to many independent consumers in near real-time (consumer groups, replay, backpressure).

## Part 2
From the architectural choice made in ```Part 1```, implement the 'consumer' to fetch and process the records generated by the ```fraud_data_producer.py``` file (revise its features!). The basic logic from the files ```fraud_consumer_agent1.py.py``` and ```fraud_consumer_agent2.py.py``` should be extended with the conection to data source defined in ```Part 1```'s architecture.

```bash
$ python ./fraud_data_producer.py
```
Output:
```bash
Inserted 1000 transactions...
Inserted 1000 transactions...
Inserted 1000 transactions...
Inserted 1000 transactions...
Inserted 1000 transactions...
Inserted 1000 transactions...
Inserted 1000 transactions...
...
```

Setup connector:
```bash
{
  "name": "fraud-connector",
  "config": {
    "connector.class": "io.debezium.connector.postgresql.PostgresConnector",
    "tasks.max": "1",
    "database.hostname": "postgres",
    "database.port": "5432",
    "database.user": "postgres",
    "database.password": "postgrespw",
    "database.dbname": "fraud_db",
    "topic.prefix": "dbserver1",
    "plugin.name": "pgoutput",
    "table.include.list": "public.transactions"
  }
}
  ```

 two fraud detection agents:

```bash
python fraud_consumer_agent1.py
```
Output:
```bash
📈 Updated profile for user 1155
🚨 Anomaly: user=3241 amount=4257.63

```

```bash
python fraud_consumer_agent2.py
```
Output:
```bash
✅ Transaction accepted (score=50)
⚠️ FRAUD ALERT: user=1032 score=90 amount=4213.54

```

## Part 3
Discuss the proposed architecture in terms of resource efficiency, operability, maintainability, deployment complexity, and overall performance and scalability. This includes discussing how well the system utilizes compute, memory, and storage resources; how easily it can be operated, monitored, and debugged in production; how maintainable and evolvable the individual components are over time; the effort required to deploy and manage the infrastructure; and the system’s ability to sustain increasing data volumes, higher ingestion rates, and a growing number of fraud detection agents without degradation of latency or reliability.

## Part 3 – Architecture Evaluation

Resource efficiency
The proposed CDC-based architecture optimizes resource usage by avoiding repeated read queries on the OLTP PostgreSQL database. Instead of polling, changes are captured directly from the write-ahead log and streamed to Kafka. This significantly reduces database load while allowing compute resources to be shifted toward fraud detection logic. Consumer agents keep only lightweight in-memory state, and Kafka’s disk usage is a deliberate trade-off that enables durability and event replay.

Operability
From an operational perspective, the system is well suited for continuous operation. Kafka Connect exposes a REST API for managing and monitoring connectors, while Kafka UI provides visibility into topics, partitions, and consumer lag. The decoupled nature of producers and consumers allows individual components to be restarted or debugged independently, without interrupting the entire pipeline.

Maintainability
The architecture is modular and loosely coupled. Fraud detection agents are independent services that consume the same event stream but apply different detection strategies. This makes it easy to extend the system by adding new agents or modifying existing logic without impacting other components. Schema evolution can be handled in a controlled way, supporting long-term maintainability.

Deployment complexity
Compared to a simple database-centric solution, this approach requires more infrastructure components, including Kafka, Kafka Connect, and Debezium. Initial setup is therefore more complex and requires careful configuration. However, once deployed, scaling and operational changes are largely configuration-driven and do not require architectural redesign.

Performance and scalability
The system is designed to handle high ingestion rates with low latency. Kafka enables parallel consumption through partitions and consumer groups, allowing the number of fraud detection agents to scale horizontally. As data volumes or consumer count increase, throughput can be increased without overloading the transactional database, maintaining reliable near real-time processing.

## Part 4
Compare the proposed architecture to Exercise 3 from previous lecture where the data from PostgreSQL was loaded to Spark (as a consumer) using the JDBC connector. Discuss both approaches at least in terms of performance, resource efficiency, and deployment complexity.

## Part 4 – Comparison

Performance
A Kafka-based CDC pipeline provides near real-time event delivery, as changes are streamed immediately after being committed to PostgreSQL. In contrast, Spark using a JDBC connector typically operates in batch or micro-batch mode, where latency depends on query intervals and job execution time. For time-sensitive use cases such as fraud detection, CDC offers significantly lower and more predictable latency.

Resource efficiency
The CDC approach minimizes impact on PostgreSQL by reading from the WAL instead of issuing frequent SELECT queries. Kafka consumers generally require limited memory and CPU, as they process records incrementally. Spark JDBC ingestion, however, requires a full Spark runtime, including driver and executors, and may involve expensive scans, shuffles, and in-memory caching, leading to higher overall resource consumption.

Deployment complexity
The CDC-based solution involves deploying and managing Kafka and Kafka Connect, which increases initial setup effort. Spark JDBC ingestion instead requires a Spark environment and job scheduling infrastructure. While Spark is powerful for large analytical workloads, it introduces additional operational overhead when used for continuous ingestion. Kafka provides built-in offset management and replay, whereas Spark relies on job state and checkpointing mechanisms.

Appropriate use cases
The CDC and Kafka architecture is better suited for event-driven, near real-time systems with many independent consumers, such as fraud detection pipelines. Spark with JDBC is more appropriate for batch analytics, periodic reporting, or large-scale transformations where real-time guarantees are not required.

# Submission
Send the exercises' resolution on Moodle and be ready to shortly present your solutions (5-8 minutes) in the next Exercise section (14.01.2026).
