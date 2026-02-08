<style>
    h1 {color: #7F2F29}
    h2 {color: #9E3A33}
    h3 {color: #C1473E}
    h4 {color: #CC6861}
</style>

# Big Data Processing Architectures and Their Role in the Future of AI Systems 

In this essay I especially want to go into detail on how Big Data Processing Architectures will evolve regarding current and future Artificial Intelligence workloads. 

## Analytical Processing Foundations
In this first part I want to emphazise the difference between analytical processing and traditional transactional processing. 

### Differences between analytical and transactional processing
This comparison is also often denoted as OLAP (online analytical processing) versus OLTP (online transactional processing). 

Important to note is that not one type of data processing system is the better choice for any use-case. Often the question is how to make the best use of both types for your situation. 

OLAP systems, such as data warehouses, are optimized for conducting complex data analysis for smarter decision-making by running queries at high speeds on large volumes of data. They are used by data scientists, business analysts and knoweldge workers. 

On the contrary, OLTP is optimized for processing massive number of transactions and use by frontline workers or customer self-service applications.

<tbc?>

### How indexes, materialized views, and query optimization support analytical workloads
There are many different ways on how one can optimize the query response time, not only in OLTP, but also in OLAP. I want to focus on analytical processing in this essay. 

#### Indexing
One of the purposes of OLAP databases is to make huge amounts of data easily queryable with minimal latencies. To decrease these latencies, indexing is often used. An index is generally a tree-based structure based on a column that directly provides you the row containing the data rather than having you scan all the rows. 

#### Materialized Views
By storing the results of complex queries in so-called materialized views, you reduce the need to recompute the results each time. Contrary to normal views, materialized views are updated periodically. 

#### Query Optimization
There are many ways to optimize a query, meaning rewriting it to be more efficient by using appropriate join strategies, avoiding selecting unnecessary columns, etc. 

#### Other methods to minimize latency
By dividing large tables into smaller, more manageable pieces, queries only have to scan the relevant partition, rather than the entire table. This is called **Partitioning**. 

Another way to provide fast responses is an **optimized infrastructure** of the OLAP system. 

## Streaming, Event Processing, and CDC
In this section I analyze how stream processing systems, event streaming platforms, and Change Data Capture pipelines complement or replace batch-oriented analytics. 

In batch processing, all the data is gathered and processed at set times, such as every day, week, or month. This approach is used in banking, where batch loads are used to process large volumes of transactions overnight. However, it also increases latency and consumes excessive resources. 

### Differences between stream processing and incremental analytics 
In stream processing, data is processed in the chunks as they flow in. That works very well for log-heavy or monitoring tasks, but there are also some downsides to this approach. Dealing with state snapshots, failover, and jumbled event orders requires many resources and demands constant monitoring, inflating costs and skill requirements beyond simpler batch setups. Furthermore, the concept of eventual consistency can glitch at window cutoffs, where accurate results are wanted. 

Incremental analytics like Change Data Capture (CDC) detect inserts, updates, or deletes from sources in real time and refreshes only what is affected. 

Where stream processing is event-reactive, focused on minimal lag and uses windowing with watermarks to achieve this, incremental analytics is delta-driven, updates the changes and needs no windowing. 

<tbc: what similarities?>

### Trade-offs between Latency and Consistency 
Batch-oriented analytics ensures consistency, what leads to high latencies. Stream Processing prioritizes low latency over consistency, incremental analytics balances both very well. ö


## Implications for AI Systems


## Technical Positioning and Future Outlook 



## References
https://www.ibm.com/think/topics/olap-vs-oltp
https://medium.com/data-science/learning-multi-dimensional-indices-a7aaa2044d8e
https://tapdata.io/blog/stream-processing-vs-incremental-computing