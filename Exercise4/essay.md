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

<tbh?>

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



## References
https://www.ibm.com/think/topics/olap-vs-oltp
https://medium.com/data-science/learning-multi-dimensional-indices-a7aaa2044d8e
