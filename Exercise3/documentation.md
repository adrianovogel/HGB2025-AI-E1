
# Activities 1 and 2 – Spark Structured Streaming

## Activity 1 – Analysis of Spark Application Execution

### Experimental Setup

The Spark Structured Streaming application was deployed in a Docker-based standalone Spark cluster.
Kafka acted as the streaming ingestion layer, while a dedicated load generator continuously produced log events into a Kafka topic.

The Spark job was launched from the `spark-client` container using `spark-submit`, and runtime behavior was observed via the Spark Driver Web UI available at `http://localhost:4040`.

---

### Streaming Runtime Behavior

After starting the load generator, the Structured Streaming UI reported a stable input stream with an input rate of several thousand events per second.
Under the initial configuration, the processing rate was slightly lower than the input rate, indicating that the application was operating close to its capacity limit.

This behavior suggested that the system could process the stream but had limited headroom for higher loads.

---

### Job Execution and DAG Structure

Each micro-batch produced by Spark Structured Streaming resulted in the execution of a Spark job.

By inspecting the DAG visualization for a job, two main execution stages were identified:

* **Stage 1:** Kafka ingestion, log parsing, filtering, and column selection
* **Stage 2:** Window-based aggregation and grouping logic

The DAG clearly showed a shuffle boundary between the two stages, confirming that stateful operations such as windowed aggregations introduce additional execution complexity.

---

### Bottleneck Analysis

The **Stages** tab revealed that the aggregation stage consistently exhibited the longest execution time.

This behavior can be explained by:

* Network-intensive shuffle operations
* Maintenance of state for time windows
* Repartitioning of records across executors

These operations dominate execution time compared to stateless transformations.

---

### Executor and Resource Utilization

The application ran with a single executor using one CPU core.

Observations from the **Executors** tab showed:

* Limited CPU usage
* Low overall memory pressure
* Minimal parallel task execution

This indicated that the available hardware resources were not fully exploited in the baseline configuration.

---

### Activity 1 Summary

This activity demonstrated how Spark Structured Streaming executes applications as a series of micro-batches composed of jobs and stages.
The results highlighted that shuffle-heavy, stateful stages are the primary performance bottleneck and that insufficient parallelism restricts throughput even when resources are available.

---

## Activity 2 – Performance Optimization and Scaling

### Baseline Configuration Constraints

The initial execution parameters were:

* 1 executor
* 1 core per executor
* 1 GB executor memory
* Default shuffle partitioning

This configuration limited task parallelism and prevented Spark from utilizing the system’s full computational capacity.

---

### Optimization Strategy

To improve throughput, the application was reconfigured by:

* Increasing the number of executors
* Assigning multiple cores per executor
* Adjusting the number of shuffle partitions to better distribute workload

These changes aimed to increase parallelism and reduce shuffle-related delays.

---

### Observed Performance Improvements

After tuning:

* The processing rate reached or exceeded the input rate
* Micro-batch durations decreased
* Shuffle stages completed faster due to improved task distribution
* Executors showed higher CPU utilization, with idle time appearing only between batches

The Structured Streaming UI confirmed that the application was able to sustain higher data volumes without accumulating backlog.

---

### Activity 2 Summary

Performance tuning significantly enhanced the application’s ability to process high-throughput streams.
By increasing executor parallelism and optimizing shuffle behavior, Spark Structured Streaming was able to handle the incoming data efficiently while maintaining acceptable latency.

---

### Practical Issues Encountered

During experimentation, several practical issues were observed:

* Initially, no data was processed because the load generator had not been started
* The Spark Master UI (port 8080) did not reflect streaming metrics accurately, while the Driver UI (port 4040) provided correct insights
* Some container restarts were required due to misconfigured ports and resource conflicts

These issues did not affect the final outcome and provided useful experience with operating Spark in containerized environments.

---

### Final Observations on Performance and Scalability

* The primary execution bottleneck was caused by shuffle and state management
* CPU resources were underutilized in the baseline setup
* Spark Structured Streaming scales effectively through horizontal parallelism
* Increasing executors, cores, and partitions allows the system to process higher data rates while maintaining stable micro-batch latency

---

