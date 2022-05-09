# PG_NestedLoopJoin_BlockedProcessing
This code is for modifying the PostgreSQL to support query re-optimization with LCPE.

The modification are mostly at: 
* changing the nested loop join implementation of PostgreSQL from pipeline processing to nested loop processing.
* considering the cost of done executed subplan into cost calculation at re-optimization stage.


For details, you might check our technical report.



 What I want to achieve is to make nested loop join of PostgreSQL from pipeline processing to nested loop processing, as shown in the Figure.
 * Collect all the outer tuples from the outer plan of nested loop join, and materialize the tuples at a tuplestorestate.
 * Fetch one outer tuple, and scan all the inner tuples to match join result tuples.
 ![WeChat Image_20220427202256](https://user-images.githubusercontent.com/52020936/165517189-22b4be00-31b8-4d64-a5ee-bc24e7692c20.png)






## Usage
 * The code is based on PostgreSQL v13.0, you can replace the folder *src/* directly, and then its supposed to work. 
 * There are some comment that marked as "LPCE ...", which denotes the details that I modified the code.





