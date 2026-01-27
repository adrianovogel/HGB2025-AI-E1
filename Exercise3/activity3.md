### Activity 3 – Monitoring user experience in near real-time

#### Overview

In this activity, a Spark Structured Streaming application was implemented to continuously monitor critical crash events in near real time. The application consumes log events from a Kafka topic, filters relevant crash events, aggregates them by user, and reports users that experience frequent crashes within short time windows.

The solution was executed using a standalone Spark cluster running inside Docker containers. Kafka was used as the streaming source, and a load generator continuously produced log events.

---

### Implementation Description

The streaming application reads JSON-formatted log records from the Kafka topic `logs`. Each record contains the following relevant fields:

* timestamp
* severity
* user_id
* content

The processing logic performs the following steps:

1. Parse incoming Kafka messages using a predefined schema.
2. Filter events where:

   * the content field contains the substring `"crash"` (case-insensitive)
   * the severity level is either `"High"` or `"Critical"`
3. Convert the timestamp field into an event-time column.
4. Group events by:

   * user_id
   * fixed 10-second event-time windows
5. Count the number of crash events per user within each window.
6. Output only users with more than 2 crash events per 10-second interval.

The results are written to the console using complete output mode, which allows inspection of the aggregated results for each completed window.

---

### Example Output (Console)

The following output was observed while the application was running:

```
-------------------------------------------
Batch: 1
-------------------------------------------
+------------------------------------------+---------+-----------+
|interval                                  |user_id  |crash_count|
+------------------------------------------+---------+-----------+
|{2026-01-27 22:35:50, 2026-01-27 22:36:00}|user_1503|5          |
|{2026-01-27 22:35:20, 2026-01-27 22:35:30}|user_1712|4          |
|{2026-01-27 22:22:50, 2026-01-27 22:23:00}|user_1177|3          |
```

This confirms that only users exceeding the crash threshold are reported, and that aggregation is performed per completed 10-second window.

---

### Handling of Event Time and Late-Arriving Records

The aggregation is based strictly on the event timestamp contained in each log record, not on the system arrival time. This ensures that events are assigned to the correct 10-second interval even if they arrive slightly late.

Spark Structured Streaming maintains state for open windows until they are finalized. Late-arriving records that fall within an active window can still be processed correctly. Once a window is completed and its state is finalized, further late records for that interval are ignored, which prevents incorrect recomputation and keeps the system stable.

This behavior ensures correct event-time semantics and predictable aggregation results.

---

### Performance and Scalability

The application uses Spark’s distributed execution model and can scale horizontally by:

* Increasing the number of executors
* Increasing executor cores
* Increasing Kafka partitions
* Adjusting shuffle partitions

Each micro-batch is processed independently, allowing the system to handle high input rates while keeping latency low. The aggregation logic is stateful but limited to short 10-second windows, which keeps memory usage manageable.

In a multi-machine environment, the workload would be distributed across multiple executors and workers, improving throughput and fault tolerance.

---

### Fault Tolerance

Spark Structured Streaming provides fault tolerance through:

* Checkpointing of streaming state
* Replay of Kafka offsets on restart
* Automatic recovery of failed executors

If a worker node fails, Spark can reschedule tasks on other available workers, ensuring continuous processing without data loss.

---

### Conclusion

This activity demonstrates a real-time monitoring solution for detecting users experiencing frequent crash events. The implementation satisfies all functional and non-functional requirements, including event-time processing, scalability, and fault tolerance. The system successfully aggregates crash events per user in near real time and highlights critical user experience issues as they occur.

