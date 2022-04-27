# PG_NestedLoopJoin_BlockedProcessing
This code is for changing the nested loop join implementation of PostgreSQL from pipeline processing to nested loop processing.



For details, you might check my technical report at ZhiHu: [[PostgreSQL源码]Nested loop join源码讲解及blocked processing的实验](https://zhuanlan.zhihu.com/p/456245221)



 What I want to achieve is to make nested loop join of PostgreSQL from pipeline processing to nested loop processing, as shown in the Figure.
 * Collect all the outer tuples from the outer plan of nested loop join, and materialize the tuples at a tuplestorestate.
 * Fetch one outer tuple, and scan all the inner tuples to match join result tuples.
![image](https://user-images.githubusercontent.com/52020936/155877242-6c00f05a-5223-4fd4-b1fc-03f4a43ca24d.png)



## Usage
 * The code is based on PostgreSQL v13.0, you can replace the folder **src/backend/exectuor** directly, and then its supposed to work. 
 * There are some comment that marked as "Fang ...", which denotes the details that I modified the code.


## Author
Fang WANG. The Hong Kong Polytechnic University.


If you are user of Wechat, you may follow my public account "LearnDB".

![qrcode_for_gh_e6d9389929b9_258](https://user-images.githubusercontent.com/52020936/147086636-6c6a5d22-b2b2-4d60-baf0-06303cbbde40.jpg)

