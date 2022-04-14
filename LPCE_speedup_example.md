### Example 1 of speeding up long-time execution with LPCE
The query execution time drops from 253265.179ms on PostgreSQL to 7745.517ms with LPCE-I,
and 4106.392ms with LPCE-R.

Query:
```
SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id 
AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.production_year=1963 AND mc.id>1552707 AND ci.person_id<295875 AND mi.info_type_id=45 AND mi_idx.id>369503 AND mk.id>269298 AND k.keyword>118444;
```

QUERY PLAN with PostgreSQL
```
 ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
  Aggregate  (cost=1150815.50..1150815.51 rows=1 width=8) (actual time=253264.251..253264.273 rows=1 loops=1)
    ->  Nested Loop  (cost=347329.26..1150815.50 rows=1 width=0) (actual time=3557.091..253263.471 rows=4525 loops=1)
          Join Filter: (mk.movie_id = t.id)
          Rows Removed by Join Filter: 164750321
          ->  Hash Join  (cost=344862.35..1040157.36 rows=1 width=20) (actual time=1249.397..3255.693 rows=373 loops=1)
                Hash Cond: (ci.movie_id = t.id)
                ->  Seq Scan on cast_info ci  (cost=0.00..683910.90 rows=3035762 width=4) (actual time=44.163..1899.057 rows=3049411 loops=1)
                      Filter: (person_id < 295875)
                      Rows Removed by Filter: 33194933
                ->  Hash  (cost=344862.33..344862.33 rows=1 width=16) (actual time=1191.498..1191.498 rows=52 loops=1)
                      Buckets: 1024  Batches: 1  Memory Usage: 11kB
                      ->  Hash Join  (cost=294144.18..344862.33 rows=1 width=16) (actual time=1119.081..1191.469 rows=52 loops=1)
                            Hash Cond: (mc.movie_id = t.id)
                            ->  Seq Scan on movie_companies mc  (cost=0.00..46718.11 rows=1066676 width=4) (actual time=75.275..148.570 rows=1056422 loops=1)
                                  Filter: (id > 1552707)
                                  Rows Removed by Filter: 1552707
                            ->  Hash  (cost=294144.16..294144.16 rows=1 width=12) (actual time=985.960..985.960 rows=37 loops=1)
                                  Buckets: 1024  Batches: 1  Memory Usage: 10kB
                                  ->  Nested Loop  (cost=265643.07..294144.16 rows=1 width=12) (actual time=977.337..985.928 rows=37 loops=1)
                                        Join Filter: (mi.movie_id = t.id)
                                        ->  Hash Join  (cost=265642.64..294143.06 rows=2 width=8) (actual time=811.316..971.921 rows=4370 loops=1)
                                              Hash Cond: (mi_idx.movie_id = mi.movie_id)
                                              ->  Seq Scan on movie_info_idx mi_idx  (cost=0.00..24710.44 rows=1010657 width=4) (actual time=19.252..105.870 rows=1010532 loops=1)
                                                    Filter: (id > 369503)
                                                    Rows Removed by Filter: 369503
                                              ->  Hash  (cost=265642.62..265642.62 rows=1 width=4) (actual time=791.313..791.313 rows=1424 loops=1)
                                                    Buckets: 2048 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 67kB
                                                    ->  Seq Scan on movie_info mi  (cost=0.00..265642.62 rows=1 width=4) (actual time=547.131..791.055 rows=1424 loops=1)
                                                          Filter: (info_type_id = 45)
                                                          Rows Removed by Filter: 14834296
                                        ->  Index Scan using title_pkey on title t  (cost=0.43..0.54 rows=1 width=4) (actual time=0.002..0.002 rows=0 loops=4370)
                                              Index Cond: (id = mi_idx.movie_id)
                                              Filter: (production_year = 1963)
                                              Rows Removed by Filter: 1
          ->  Hash Join  (cost=2466.91..104436.33 rows=497744 width=4) (actual time=0.040..653.430 rows=441702 loops=373)
                Hash Cond: (mk.keyword_id = k.id)
                ->  Seq Scan on movie_keyword mk  (cost=0.00..81003.12 rows=4263695 width=8) (actual time=0.005..309.784 rows=4254632 loops=373)
                      Filter: (id > 269298)
                      Rows Removed by Filter: 269298
                ->  Hash  (cost=2271.12..2271.12 rows=15663 width=4) (actual time=9.343..9.343 rows=15725 loops=1)
                      Buckets: 16384  Batches: 1  Memory Usage: 681kB
                      ->  Seq Scan on keyword k  (cost=0.00..2271.12 rows=15663 width=4) (actual time=0.012..7.797 rows=15725 loops=1)
                            Filter: (keyword > 118444)
                            Rows Removed by Filter: 118445
  Planning Time: 9.143 ms
  Execution Time: 253265.179 ms
```

QUERY PLAN with LPCE-I
```
 Aggregate  (cost=1117238.19..1117238.20 rows=1 width=8) (actual time=8057.194..8100.199 rows=1 loops=1)
   ->  Hash Join  (cost=160394.74..1117233.74 rows=1779 width=0) (actual time=7676.848..8051.043 rows=4525 loops=1)
         Hash Cond: (t.id = mc.movie_id)
         ->  Nested Loop  (cost=113083.68..1069918.26 rows=494 width=20) (actual time=5577.013..7385.247 rows=2968 loops=1)
               Join Filter: (t.id = mi.movie_id)
               Rows Removed by Join Filter: 25358472
               ->  Hash Join  (cost=113083.68..797420.61 rows=803 width=16) (actual time=2807.769..4808.616 rows=17810 loops=1)
                     Hash Cond: (ci.movie_id = t.id)
                     ->  Seq Scan on cast_info ci  (cost=0.00..683910.90 rows=113582 width=4) (actual time=0.030..1819.596 rows=3049411 loops=1)
                           Filter: (person_id < 295875)
                           Rows Removed by Filter: 33194933
                     ->  Hash  (cost=113080.94..113080.94 rows=219 width=12) (actual time=2807.062..2807.062 rows=4236 loops=1)
                           Buckets: 8192 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 247kB
                           ->  Nested Loop  (cost=27577.26..113080.94 rows=219 width=12) (actual time=1325.028..2806.289 rows=4236 loops=1)
                                 Join Filter: (mi_idx.movie_id = t.id)
                                 ->  Hash Join  (cost=27576.83..109207.89 rows=3528 width=8) (actual time=274.032..1091.531 rows=991795 loops=1)
                                       Hash Cond: (mk.movie_id = mi_idx.movie_id)
                                       ->  Hash Join  (cost=2310.09..83881.63 rows=8233 width=4) (actual time=20.511..673.250 rows=441702 loops=1)
                                             Hash Cond: (mk.keyword_id = k.id)
                                             ->  Seq Scan on movie_keyword mk  (cost=0.00..81003.12 rows=142735 width=8) (actual time=12.351..312.192 rows=4254632 loops=1)
                                                   Filter: (id > 269298)
                                                   Rows Removed by Filter: 269298
                                             ->  Hash  (cost=2271.12..2271.12 rows=3117 width=4) (actual time=8.130..8.130 rows=15725 loops=1)
                                                   Buckets: 16384 (originally 4096)  Batches: 1 (originally 1)  Memory Usage: 681kB
                                                   ->  Seq Scan on keyword k  (cost=0.00..2271.12 rows=3117 width=4) (actual time=0.006..6.873 rows=15725 loops=1)
                                                         Filter: (keyword > 118444)
                                                         Rows Removed by Filter: 118445
                                       ->  Hash  (cost=24710.44..24710.44 rows=44504 width=4) (actual time=202.629..202.629 rows=1010532 loops=1)
                                             Buckets: 131072 (originally 65536)  Batches: 16 (originally 1)  Memory Usage: 3250kB
                                             ->  Seq Scan on movie_info_idx mi_idx  (cost=0.00..24710.44 rows=44504 width=4) (actual time=17.774..104.749 rows=1010532 loops=1)
                                                   Filter: (id > 369503)
                                                   Rows Removed by Filter: 369503
                                 ->  Index Scan using title_pkey on title t  (cost=0.43..1.09 rows=1 width=4) (actual time=0.001..0.001 rows=0 loops=991795)
                                       Index Cond: (id = mk.movie_id)
                                       Filter: (production_year = 1963)
                                       Rows Removed by Filter: 1
               ->  Materialize  (cost=0.00..265645.47 rows=569 width=4) (actual time=0.025..0.083 rows=1424 loops=17810)
                     ->  Seq Scan on movie_info mi  (cost=0.00..265642.62 rows=569 width=4) (actual time=449.472..716.945 rows=1424 loops=1)
                           Filter: (info_type_id = 45)
                           Rows Removed by Filter: 14834296
         ->  Hash  (cost=46718.11..46718.11 rows=47436 width=4) (actual time=270.276..270.276 rows=1056422 loops=1)
               Buckets: 131072 (originally 65536)  Batches: 16 (originally 1)  Memory Usage: 3345kB
               ->  Seq Scan on movie_companies mc  (cost=0.00..46718.11 rows=47436 width=4) (actual time=74.572..164.291 rows=1056422 loops=1)
                     Filter: (id > 1552707)
                     Rows Removed by Filter: 1552707
 Execution Time: 8145.517 ms
```

QUERY PLAN with LPCE-R 
```  
  Aggregate  (cost=1006616.76..1006616.77 rows=1 width=8) (actual time=3851.728..3856.732 rows=1 loops=1)
    ->  Hash Join  (cost=322279.42..1006616.36 rows=160 width=0) (actual time=2122.160..3850.522 rows=4525 loops=1)
          Hash Cond: (ci.movie_id = t.id)
          ->  Seq Scan on cast_info ci  (cost=0.00..683910.90 rows=113582 width=4) (actual time=0.022..1820.681 rows=3049411 loops=1)
                Filter: (person_id < 295875)
                Rows Removed by Filter: 33194933
          ->  Hash  (cost=322276.31..322276.31 rows=249 width=20) (actual time=2114.517..2114.517 rows=580 loops=1)
                Buckets: 1024  Batches: 1  Memory Usage: 38kB
                ->  Hash Join  (cost=271592.42..322276.31 rows=249 width=20) (actual time=1949.250..2114.456 rows=580 loops=1)
                      Hash Cond: (mc.movie_id = t.id)
                      ->  Seq Scan on movie_companies mc  (cost=0.00..46718.11 rows=1056422 width=4) (actual time=0.008..139.695 rows=1056422 loops=1)
                            Filter: (id > 1552707)
                            Rows Removed by Filter: 1552707
                      ->  Hash  (cost=271579.88..271579.88 rows=1003 width=16) (actual time=1917.484..1917.484 rows=388 loops=1)
                            Buckets: 1024  Batches: 1  Memory Usage: 27kB
                            ->  Hash Join  (cost=270339.79..271579.88 rows=1003 width=16) (actual time=1766.008..1917.441 rows=388 loops=1)
                                  Hash Cond: (mi_idx.movie_id = t.id)
                                  ->  Hash Join  (cost=43757.78..165698.48 rows=991796 width=8) (actual time=235.648..1083.879 rows=991795 loops=1)
                                        Hash Cond: (mk.movie_id = mi_idx.movie_id)
                                        ->  Hash Join  (cost=2467.69..104412.20 rows=441702 width=4) (actual time=23.407..684.246 rows=441702 loops=1)
                                              Hash Cond: (mk.keyword_id = k.id)
                                              ->  Seq Scan on movie_keyword mk  (cost=0.00..81003.12 rows=4254632 width=8) (actual time=0.011..310.236 rows=4254632 loops=1)
                                                    Filter: (id > 269298)
                                                    Rows Removed by Filter: 269298
                                              ->  Hash  (cost=2271.12..2271.12 rows=15725 width=4) (actual time=23.246..23.246 rows=15725 loops=1)
                                                    Buckets: 16384  Batches: 1  Memory Usage: 681kB
                                                    ->  Seq Scan on keyword k  (cost=0.00..2271.12 rows=15725 width=4) (actual time=0.010..19.214 rows=15725 loops=1)
                                                          Filter: (keyword > 118444)
                                                          Rows Removed by Filter: 118445
                                        ->  Hash  (cost=24710.44..24710.44 rows=1010532 width=4) (actual time=211.572..211.572 rows=1010532 loops=1)
                                              Buckets: 131072  Batches: 16  Memory Usage: 3250kB
                                              ->  Seq Scan on movie_info_idx mi_idx  (cost=0.00..24710.44 rows=1010532 width=4) (actual time=21.914..114.480 rows=1010532 loops=1)
                                                    Filter: (id > 369503)
                                                    Rows Removed by Filter: 369503
                                  ->  Hash  (cost=270338.69..270338.69 rows=88 width=8) (actual time=789.134..789.134 rows=12 loops=1)
                                        Buckets: 1024  Batches: 1  Memory Usage: 9kB
                                        ->  Nested Loop  (cost=0.43..270338.69 rows=88 width=8) (actual time=784.870..789.126 rows=12 loops=1)
                                              ->  Seq Scan on movie_info mi  (cost=0.00..265642.62 rows=569 width=4) (actual time=110.670..783.388 rows=1424 loops=1)
                                                    Filter: (info_type_id = 45)
                                                    Rows Removed by Filter: 14834296
                                              ->  Index Scan using title_pkey on title t  (cost=0.43..8.25 rows=1 width=4) (actual time=0.003..0.003 rows=0 loops=1424)
                                                    Index Cond: (id = mi.movie_id)
                                                    Filter: (production_year = 1963)
                                                    Rows Removed by Filter: 1
  Execution Time: 3906.392 ms   
```





### Example 2 of speeding up long-time execution with LPCE
The query execution time drops from 24779.757ms on PostgreSQL to 8388.941ms with LPCE-I, and 6281.196ms with LPCE-R.

Query:
``` 
SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_keyword mk,keyword k,movie_link ml WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=ml.movie_id AND t.production_year<1968 AND mc.id<494049 AND ci.role_id=3 AND mi.info_type_id=17 AND mk.id<933418 AND k.keyword>42312 AND ml.linked_movie_id>976930;
``` 

QUERY PLAN on PostgreSQL
``` 
 Aggregate  (cost=970680.16..970680.17 rows=1 width=8) (actual time=24779.447..24779.453 rows=1 loops=1)
   ->  Hash Join  (cost=271178.51..970679.93 rows=91 width=0) (actual time=16755.930..24480.245 rows=9313020 loops=1)
         Hash Cond: (ci.movie_id = t.id)
         ->  Seq Scan on cast_info ci  (cost=0.00..683910.90 rows=4157232 width=4) (actual time=0.123..2220.102 rows=4008037 loops=1)
               Filter: (role_id = 3)
               Rows Removed by Filter: 32236307
         ->  Hash  (cost=271177.83..271177.83 rows=55 width=20) (actual time=16721.305..16721.305 rows=28828944 loops=1)
               Buckets: 131072 (originally 1024)  Batches: 128 (originally 1)  Memory Usage: 851780kB
               ->  Hash Join  (cost=3780.66..271177.83 rows=55 width=20) (actual time=672.583..13375.511 rows=28828944 loops=1)
                     Hash Cond: (mk.keyword_id = k.id)
                     ->  Hash Join  (cost=0.00..267034.30 rows=81 width=24) (actual time=653.341..5635.640 rows=43863146 loops=1)
                           Hash Cond: (mi.movie_id = t.id)
                           ->  Seq Scan on movie_info mi  (cost=0.00..265642.62 rows=370897 width=4) (actual time=0.025..753.127 rows=368218 loops=1)
                                 Filter: (info_type_id = 17)
                                 Rows Removed by Filter: 14467502
                           ->  Hash  (cost=144855.14..144855.14 rows=551 width=20) (actual time=647.584..647.584 rows=697640 loops=1)
                                 Buckets: 131072 (originally 1024)  Batches: 256 (originally 1)  Memory Usage: 17831kB
                                 ->  Hash Join  (cost=60419.11..144855.14 rows=551 width=20) (actual time=230.269..563.158 rows=697640 loops=1)
                                       Hash Cond: (mk.movie_id = t.id)
                                       ->  Seq Scan on movie_keyword mk  (cost=0.00..81003.12 rows=913972 width=8) (actual time=0.014..222.893 rows=933417 loops=1)
                                             Filter: (id < 933418)
                                             Rows Removed by Filter: 3590513
                                       ->  Hash  (cost=60400.05..60400.05 rows=1525 width=12) (actual time=230.221..230.221 rows=20496 loops=1)
                                             Buckets: 32768 (originally 2048)  Batches: 1 (originally 1)  Memory Usage: 1137kB
                                             ->  Hash Join  (cost=11808.82..60400.05 rows=1525 width=12) (actual time=69.227..228.346 rows=20496 loops=1)
                                                   Hash Cond: (mc.movie_id = t.id)
                                                   ->  Seq Scan on movie_companies mc  (cost=0.00..46718.11 rows=495431 width=4) (actual time=0.009..128.688 rows=494048 l
oops=1)
                                                         Filter: (id < 494049)
                                                         Rows Removed by Filter: 2115081
                                                   ->  Hash  (cost=11711.57..11711.57 rows=7780 width=8) (actual time=69.186..69.186 rows=5166 loops=1)
                                                         Buckets: 8192  Batches: 1  Memory Usage: 266kB
                                                         ->  Merge Join  (cost=4336.90..11711.57 rows=7780 width=8) (actual time=9.476..68.733 rows=5166 loops=1)
                                                               Merge Cond: (t.id = ml.movie_id)
                                                               ->  Index Scan using title_pkey on title t  (cost=0.43..94082.89 rows=463574 width=4) (actual time=0.045..5
4.151 rows=21949 loops=1)
                                                                     Filter: (production_year < 1968)
                                                                     Rows Removed by Filter: 164310
                                                               ->  Sort  (cost=4336.43..4442.51 rows=42432 width=4) (actual time=9.397..11.365 rows=42300 loops=1)
                                                                     Sort Key: ml.movie_id
                                                                     Sort Method: quicksort  Memory: 3349kB
                                                                     ->  Seq Scan on movie_link ml  (cost=0.00..1074.93 rows=42432 width=4) (actual time=0.003..4.522 rows
=42300 loops=1)
                                                                           Filter: (linked_movie_id > 976930)
                                                                           Rows Removed by Filter: 17694
                     ->  Hash  (cost=2271.12..2271.12 rows=91963 width=4) (actual time=19.046..19.046 rows=91857 loops=1)
                           Buckets: 131072  Batches: 2  Memory Usage: 2649kB
                           ->  Seq Scan on keyword k  (cost=0.00..2271.12 rows=91963 width=4) (actual time=0.008..10.199 rows=91857 loops=1)
                                 Filter: (keyword > 42312)
                                 Rows Removed by Filter: 42313
 Execution Time: 24779.757 ms
``` 

QUERY PLAN with LPCE-I
```  
 Aggregate  (cost=1086055.44..1086055.45 rows=1 width=8) (actual time=8381.899..8381.905 rows=1 loops=1)
   ->  Hash Join  (cost=401549.26..1086030.80 rows=9857 width=0) (actual time=4193.562..8097.349 rows=9313020 loops=1)
         Hash Cond: (t.id = mc.movie_id)
         ->  Hash Join  (cost=354583.80..1039054.02 rows=1282 width=20) (actual time=3999.075..7158.346 rows=808454 loops=1)
               Hash Cond: (ci.movie_id = t.id)
               ->  Seq Scan on cast_info ci  (cost=0.00..683910.90 rows=148852 width=4) (actual time=1189.282..2244.184 rows=4008037 loops=1)
                     Filter: (role_id = 3)
                     Rows Removed by Filter: 32236307
               ->  Hash  (cost=354560.10..354560.10 rows=1896 width=16) (actual time=2777.111..2777.111 rows=3361800 loops=1)
                     Buckets: 131072 (originally 2048)  Batches: 256 (originally 1)  Memory Usage: 131044kB
                     ->  Merge Join  (cost=353778.03..354560.10 rows=1896 width=16) (actual time=1880.648..2401.951 rows=3361800 loops=1)
                           Merge Cond: (t.id = ml.movie_id)
                           ->  Nested Loop  (cost=352023.30..361836.87 rows=3104 width=12) (actual time=1870.100..2000.274 rows=9151 loops=1)
                                 Join Filter: (mi.movie_id = t.id)
                                 ->  Merge Join  (cost=352022.87..352216.29 rows=3658 width=8) (actual time=1397.579..1640.184 rows=953286 loops=1)
                                       Merge Cond: (mk.movie_id = mi.movie_id)
                                       ->  Sort  (cost=85545.43..85607.77 rows=24936 width=4) (actual time=559.068..603.817 rows=598942 loops=1)
                                             Sort Key: mk.movie_id
                                             Sort Method: external merge  Disk: 8280kB
                                             ->  Hash Join  (cost=2505.81..83724.36 rows=24936 width=4) (actual time=21.770..468.870 rows=598943 loops=1)
                                                   Hash Cond: (mk.keyword_id = k.id)
                                                   ->  Seq Scan on movie_keyword mk  (cost=0.00..81003.12 rows=41836 width=8) (actual time=0.032..238.307 rows=933417 loops=1)
                                                         Filter: (id < 933418)
                                                         Rows Removed by Filter: 3590513
                                                   ->  Hash  (cost=2271.12..2271.12 rows=18775 width=4) (actual time=21.653..21.653 rows=91857 loops=1)
                                                         Buckets: 131072 (originally 32768)  Batches: 2 (originally 1)  Memory Usage: 3073kB
                                                         ->  Seq Scan on keyword k  (cost=0.00..2271.12 rows=18775 width=4) (actual time=0.014..11.077 rows=91857 loops=1)
                                                               Filter: (keyword > 42312)
                                                               Rows Removed by Filter: 42313
                                       ->  Sort  (cost=266477.44..266508.16 rows=12290 width=4) (actual time=838.498..913.801 rows=1262322 loops=1)
                                             Sort Key: mi.movie_id
                                             Sort Method: external sort  Disk: 6528kB
                                             ->  Seq Scan on movie_info mi  (cost=0.00..265642.62 rows=12290 width=4) (actual time=418.886..758.851 rows=368218 loops=1)
                                                   Filter: (info_type_id = 17)
                                                   Rows Removed by Filter: 14467502
                                 ->  Index Scan using title_pkey on title t  (cost=0.43..2.62 rows=1 width=4) (actual time=0.001..0.001 rows=0 loops=93531)
                                       Index Cond: (id = mk.movie_id)
                                       Filter: (production_year < 1968)
                                       Rows Removed by Filter: 1
                           ->  Sort  (cost=1754.72..1780.24 rows=10209 width=4) (actual time=9.400..122.169 rows=3401690 loops=1)
                                 Sort Key: ml.movie_id
                                 Sort Method: quicksort  Memory: 3349kB
                                 ->  Seq Scan on movie_link ml  (cost=0.00..1074.93 rows=10209 width=4) (actual time=0.010..4.835 rows=42300 loops=1)
                                       Filter: (linked_movie_id > 976930)
                                       Rows Removed by Filter: 17694
         ->  Hash  (cost=46718.11..46718.11 rows=19788 width=4) (actual time=194.307..194.307 rows=494048 loops=1)
               Buckets: 131072 (originally 32768)  Batches: 8 (originally 1)  Memory Usage: 3168kB
               ->  Seq Scan on movie_companies mc  (cost=0.00..46718.11 rows=19788 width=4) (actual time=0.026..143.217 rows=494048 loops=1)
                     Filter: (id < 494049)
                     Rows Removed by Filter: 2115081
 Execution Time: 8388.941 ms
```  

QUERY PLAN with LPCE-R
``` 
 Aggregate  (cost=743747.35..743747.36 rows=1 width=8) (actual time=6279.508..6279.513 rows=1 loops=1)
   ->  Hash Join  (cost=52904.35..743739.33 rows=3206 width=0) (actual time=2087.795..5994.297 rows=9313020 loops=1)
         Hash Cond: (t.id = ml.movie_id)
         ->  Hash Join  (cost=51701.81..737697.31 rows=3414 width=20) (actual time=2061.201..5291.344 rows=3018028 loops=1)
               Hash Cond: (ci.movie_id = t.id)
               ->  Seq Scan on cast_info ci  (cost=0.00..683910.90 rows=148852 width=4) (actual time=0.171..2275.868 rows=4008037 loops=1)
                     Filter: (role_id = 3)
                     Rows Removed by Filter: 32236307
               ->  Hash  (cost=50897.54..50897.54 rows=64342 width=16) (actual time=2060.540..2060.540 rows=1406185 loops=1)
                     Buckets: 131072 (originally 65536)  Batches: 2 (originally 1)  Memory Usage: 37345kB
                     ->  Hash Join  (cost=409.97..50897.54 rows=64342 width=16) (actual time=1612.273..1911.305 rows=1406185 loops=1)
                           Hash Cond: (mc.movie_id = t.id)
                           ->  Seq Scan on movie_companies mc  (cost=0.00..46718.11 rows=494048 width=4) (actual time=43.139..136.581 rows=494048 loops=1)
                                 Filter: (id < 494049)
                                 Rows Removed by Filter: 2115081
                           ->  Hash  (cost=400188.24..400188.24 rows=32798 width=12) (actual time=1568.522..1568.522 rows=141166 loops=1)
                                 Buckets: 131072 (originally 65536)  Batches: 4 (originally 1)  Memory Usage: 3073kB
                                 ->  Hash Join  (cost=132710.22..400188.24 rows=32798 width=12) (actual time=1373.571..1551.723 rows=141166 loops=1)
                                       Hash Cond: (mk.keyword_id = k.id)
                                       ->  Hash Join  (cost=128931.88..395968.61 rows=3991 width=16) (actual time=1353.703..1489.265 rows=222699 loops=1)
                                             Hash Cond: (mi.movie_id = t.id)
                                             ->  Seq Scan on movie_info mi  (cost=0.00..265642.62 rows=368218 width=4) (actual time=691.267..762.087 rows=368218 loops=1)
                                                   Filter: (info_type_id = 17)
                                                   Rows Removed by Filter: 14467502
                                             ->  Hash  (cost=128817.82..128817.82 rows=9125 width=12) (actual time=660.750..660.750 rows=132105 loops=1)
                                                   Buckets: 131072 (originally 16384)  Batches: 2 (originally 1)  Memory Usage: 3852kB
                                                   ->  Hash Join  (cost=45364.47..128817.82 rows=9125 width=12) (actual time=371.971..645.923 rows=132105 loops=1)
                                                         Hash Cond: (mk.movie_id = t.id)
                                                         ->  Seq Scan on movie_keyword mk  (cost=0.00..81003.12 rows=933417 width=8) (actual time=162.265..231.233 rows=933417 loops=1)
                                                               Filter: (id < 933418)
                                                               Rows Removed by Filter: 3590513
                                                         ->  Hash  (cost=45270.90..45270.90 rows=7486 width=4) (actual time=209.478..209.478 rows=461335 loops=1)
                                                               Buckets: 131072 (originally 8192)  Batches: 8 (originally 1)  Memory Usage: 3073kB
                                                               ->  Seq Scan on title t  (cost=0.00..45270.90 rows=7486 width=4) (actual time=0.008..158.525 rows=461335 loops=1)
                                                                     Filter: (production_year < 1968)
                                                                     Rows Removed by Filter: 2066977
                                       ->  Hash  (cost=2271.12..2271.12 rows=91857 width=4) (actual time=19.406..19.406 rows=91857 loops=1)
                                             Buckets: 131072  Batches: 2  Memory Usage: 2649kB
                                             ->  Seq Scan on keyword k  (cost=0.00..2271.12 rows=91857 width=4) (actual time=0.007..9.839 rows=91857 loops=1)
                                                   Filter: (keyword > 42312)
                                                   Rows Removed by Filter: 42313
         ->  Hash  (cost=1074.93..1074.93 rows=10209 width=4) (actual time=23.642..23.642 rows=42300 loops=1)
               Buckets: 65536 (originally 16384)  Batches: 1 (originally 1)  Memory Usage: 2000kB
               ->  Seq Scan on movie_link ml  (cost=0.00..1074.93 rows=10209 width=4) (actual time=0.029..13.089 rows=42300 loops=1)
                     Filter: (linked_movie_id > 976930)
                     Rows Removed by Filter: 17694
 Execution Time: 6381.196 ms
``` 








### Example 3 of speeding up long-time execution with LPCE
The query execution time drops from 96493.755ms on PostgreSQL to 38027.132ms with LPCE-I,
and 4271.519ms with LPCE-R.


Query: 
```
SELECT COUNT(*) FROM title t,movie_companies mc,cast_info ci,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k,aka_title at,complete_cast cc WHERE t.id=mc.movie_id AND t.id=ci.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=at.movie_id AND t.id=cc.movie_id AND mc.id>2036223 AND ci.person_id>3350233 AND mi.info_type_id=42 AND mi_idx.id>987738 AND mk.id>1671144 AND k.keyword>115271 AND at.kind_id=4 AND cc.status_id=3;
```


QUERY PLAN on PostgreSQL                                                                                     
```
 Aggregate  (cost=1162732.94..1162732.95 rows=1 width=8) (actual time=96490.189..96490.308 rows=1 loops=1)
   ->  Nested Loop  (cost=141940.83..1162732.94 rows=1 width=0) (actual time=47268.840..96489.892 rows=312 loops=1)
         Join Filter: (t.id = mc.movie_id)
         Rows Removed by Join Filter: 178746360
         ->  Nested Loop  (cost=141940.83..1108931.12 rows=1 width=28) (actual time=27358.194..47245.406 rows=312 loops=1)
               Join Filter: (t.id = mi.movie_id)
               Rows Removed by Join Filter: 460875942
               ->  Seq Scan on movie_info mi  (cost=0.00..265642.62 rows=8407 width=4) (actual time=704.096..722.337 rows=6509 loops=1)
                     Filter: (info_type_id = 42)
                     Rows Removed by Filter: 14829211
               ->  Materialize  (cost=141940.83..840388.13 rows=23 width=24) (actual time=0.419..4.259 rows=70806 loops=6509)
                     ->  Nested Loop  (cost=141940.83..840388.02 rows=23 width=24) (actual time=2723.866..2826.537 rows=70806 loops=1)
                           ->  Hash Join  (cost=141940.40..840018.23 rows=809 width=20) (actual time=622.785..2702.433 rows=70806 loops=1)
                                 Hash Cond: (ci.movie_id = mi_idx.movie_id)
                                 ->  Seq Scan on cast_info ci  (cost=0.00..683910.90 rows=3752141 width=4) (actual time=0.012..1842.812 rows=3878229 loops=1)
                                       Filter: (person_id > 3350233)
                                       Rows Removed by Filter: 32366115
                                 ->  Hash  (cost=141907.11..141907.11 rows=2663 width=16) (actual time=621.952..621.952 rows=4464 loops=1)
                                       Buckets: 8192 (originally 4096)  Batches: 1 (originally 1)  Memory Usage: 274kB
                                       ->  Hash Join  (cost=49907.68..141907.11 rows=2663 width=16) (actual time=196.872..621.393 rows=4464 loops=1)
                                             Hash Cond: (mk.keyword_id = k.id)
                                             ->  Hash Join  (cost=47400.46..139302.32 rows=18917 width=20) (actual time=187.161..609.053 rows=35448 loops=1)
                                                   Hash Cond: (mk.movie_id = mi_idx.movie_id)
                                                   ->  Seq Scan on movie_keyword mk  (cost=0.00..81003.12 rows=2855883 width=8) (actual time=0.015..264.760 rows=2852786 loops=1)
                                                         Filter: (id > 1671144)
                                                         Rows Removed by Filter: 1671144
                                                   ->  Hash  (cost=47362.89..47362.89 rows=3006 width=12) (actual time=186.468..186.468 rows=1641 loops=1)
                                                         Buckets: 4096  Batches: 1  Memory Usage: 103kB
                                                         ->  Hash Join  (cost=44497.25..47362.89 rows=3006 width=12) (actual time=175.102..186.321 rows=1641 loops=1)
                                                               Hash Cond: (cc.movie_id = mi_idx.movie_id)
                                                               ->  Seq Scan on complete_cast cc  (cost=0.00..2419.57 rows=110933 width=4) (actual time=0.007..10.459 rows=110494 loops=1)
                                                                     Filter: (status_id = 3)
                                                                     Rows Removed by Filter: 24592
                                                               ->  Hash  (cost=44343.54..44343.54 rows=12297 width=8) (actual time=169.296..169.296 rows=11070 loops=1)
                                                                     Buckets: 16384  Batches: 1  Memory Usage: 561kB
                                                                     ->  Hash Join  (cost=31244.59..44343.54 rows=12297 width=8) (actual time=117.452..168.160 rows=11070 loops=1)
                                                                           Hash Cond: (at.movie_id = mi_idx.movie_id)
                                                                           ->  Seq Scan on aka_title at  (cost=0.00..11222.40 rows=14013 width=4) (actual time=0.011..30.557 rows=13497 loops=1)
                                                                                 Filter: (kind_id = 4)
                                                                                 Rows Removed by Filter: 347975
                                                                           ->  Hash  (cost=24710.44..24710.44 rows=398252 width=4) (actual time=116.846..116.846 rows=392297 loops=1)
                                                                                 Buckets: 131072  Batches: 8  Memory Usage: 2759kB
                                                                                 ->  Seq Scan on movie_info_idx mi_idx  (cost=0.00..24710.44 rows=398252 width=4) (actual time=14.611..80.304 rows=392297 loops=1)
                                                                                       Filter: (id > 987738)
                                                                                       Rows Removed by Filter: 987738
                                             ->  Hash  (cost=2271.12..2271.12 rows=18888 width=4) (actual time=9.529..9.529 rows=18898 loops=1)
                                                   Buckets: 32768  Batches: 1  Memory Usage: 921kB
                                                   ->  Seq Scan on keyword k  (cost=0.00..2271.12 rows=18888 width=4) (actual time=0.008..7.592 rows=18898 loops=1)
                                                         Filter: (keyword > 115271)
                                                         Rows Removed by Filter: 115272
                           ->  Index Only Scan using title_pkey on title t  (cost=0.43..0.46 rows=1 width=4) (actual time=0.001..0.001 rows=1 loops=70806)
                                 Index Cond: (id = ci.movie_id)
                                 Heap Fetches: 0
         ->  Seq Scan on movie_companies mc  (cost=0.00..46718.11 rows=566697 width=4) (actual time=0.002..133.500 rows=572906 loops=312)
               Filter: (id > 2036223)
               Rows Removed by Filter: 2036223
 Planning Time: 35.354 ms
 Execution Time: 96493.755 ms
(58 rows)
```

QUERY PLAN on PostgreSQL with LPCE-I
```                                                                            
 Aggregate  (cost=1127603.58..1127603.59 rows=1 width=8) (actual time=37018.939..37019.013 rows=1 loops=1)
   ->  Nested Loop  (cost=88096.67..1127601.50 rows=832 width=0) (actual time=37018.442..37018.985 rows=312 loops=1)
         Join Filter: (mc.movie_id = t.id)
         ->  Nested Loop  (cost=88096.24..1127417.26 rows=259 width=28) (actual time=35710.605..37018.319 rows=312 loops=1)
               Join Filter: (mc.movie_id = ci.movie_id)
               Rows Removed by Join Filter: 64694568
               ->  Hash Join  (cost=51966.96..133511.38 rows=1585 width=12) (actual time=386.551..998.562 rows=224635 loops=1)
                     Hash Cond: (mk.keyword_id = k.id)
                     ->  Hash Join  (cost=49649.73..131154.91 rows=9750 width=16) (actual time=376.867..873.484 rows=1661574 loops=1)
                           Hash Cond: (mk.movie_id = mc.movie_id)
                           ->  Seq Scan on movie_keyword mk  (cost=0.00..81003.12 rows=129590 width=8) (actual time=79.713..294.430 rows=2852786 loops=1)
                                 Filter: (id > 1671144)
                                 Rows Removed by Filter: 1671144
                           ->  Hash  (cost=49570.61..49570.61 rows=6330 width=8) (actual time=261.749..261.749 rows=55505 loops=1)
                                 Buckets: 65536 (originally 8192)  Batches: 1 (originally 1)  Memory Usage: 2681kB
                                 ->  Hash Join  (cost=2672.81..49570.61 rows=6330 width=8) (actual time=120.630..255.987 rows=55505 loops=1)
                                       Hash Cond: (mc.movie_id = cc.movie_id)
                                       ->  Seq Scan on movie_companies mc  (cost=0.00..46718.11 rows=33290 width=4) (actual time=95.839..139.697 rows=572906 loops=1)
                                             Filter: (id > 2036223)
                                             Rows Removed by Filter: 2036223
                                       ->  Hash  (cost=2419.57..2419.57 rows=20259 width=4) (actual time=24.599..24.599 rows=110494 loops=1)
                                             Buckets: 131072 (originally 32768)  Batches: 2 (originally 1)  Memory Usage: 3073kB
                                             ->  Seq Scan on complete_cast cc  (cost=0.00..2419.57 rows=20259 width=4) (actual time=0.015..12.229 rows=110494 loops=1)
                                                   Filter: (status_id = 3)
                                                   Rows Removed by Filter: 24592
                     ->  Hash  (cost=2271.12..2271.12 rows=3688 width=4) (actual time=9.608..9.608 rows=18898 loops=1)
                           Buckets: 32768 (originally 4096)  Batches: 1 (originally 1)  Memory Usage: 921kB
                           ->  Seq Scan on keyword k  (cost=0.00..2271.12 rows=3688 width=4) (actual time=0.015..7.751 rows=18898 loops=1)
                                 Filter: (keyword > 115271)
                                 Rows Removed by Filter: 115272
               ->  Materialize  (cost=36129.28..990244.92 rows=154 width=16) (actual time=0.082..0.148 rows=288 loops=224635)
                     ->  Nested Loop  (cost=36129.28..990244.15 rows=154 width=16) (actual time=18466.713..31180.646 rows=288 loops=1)
                           Join Filter: (ci.movie_id = mi.movie_id)
                           Rows Removed by Join Filter: 367751703
                           ->  Seq Scan on movie_info mi  (cost=0.00..265642.62 rows=719 width=4) (actual time=490.472..782.691 rows=6509 loops=1)
                                 Filter: (info_type_id = 42)
                                 Rows Removed by Filter: 14829211
                           ->  Materialize  (cost=36129.28..720579.65 rows=373 width=12) (actual time=0.252..2.112 rows=56499 loops=6509)
                                 ->  Hash Join  (cost=36129.28..720577.79 rows=373 width=12) (actual time=1639.877..2406.452 rows=56499 loops=1)
                                       Hash Cond: (ci.movie_id = mi_idx.movie_id)
                                       ->  Seq Scan on cast_info ci  (cost=0.00..683910.90 rows=143277 width=4) (actual time=1431.216..1935.982 rows=3878229 loops=1)
                                             Filter: (person_id > 3350233)
                                             Rows Removed by Filter: 32366115
                                       ->  Hash  (cost=36126.39..36126.39 rows=231 width=8) (actual time=208.537..208.537 rows=11070 loops=1)
                                             Buckets: 16384 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 561kB
                                             ->  Hash Join  (cost=24900.11..36126.39 rows=231 width=8) (actual time=162.222..207.553 rows=11070 loops=1)
                                                   Hash Cond: (at.movie_id = mi_idx.movie_id)
                                                   ->  Seq Scan on aka_title at  (cost=0.00..11222.40 rows=589 width=4) (actual time=2.369..31.815 rows=13497 loops=1)
                                                         Filter: (kind_id = 4)
                                                         Rows Removed by Filter: 347975
                                                   ->  Hash  (cost=24710.44..24710.44 rows=15174 width=4) (actual time=143.591..143.591 rows=392297 loops=1)
                                                         Buckets: 131072 (originally 16384)  Batches: 8 (originally 1)  Memory Usage: 3073kB
                                                         ->  Seq Scan on movie_info_idx mi_idx  (cost=0.00..24710.44 rows=15174 width=4) (actual time=65.635..102.968 rows=392297 loops=1)
                                                               Filter: (id > 987738)
                                                               Rows Removed by Filter: 987738
         ->  Index Only Scan using title_pkey on title t  (cost=0.43..0.70 rows=1 width=4) (actual time=0.001..0.001 rows=1 loops=312)
               Index Cond: (id = ci.movie_id)
               Heap Fetches: 0
Execution Time: 38027.132 ms
```



QUERY PLAN on PostgreSQL with LPCE-R
```         
 Aggregate  (cost=1127603.58..1127603.59 rows=1 width=8) (actual time=4186.006..4186.014 rows=1 loops=1)
   ->  Nested Loop  (cost=88096.67..1127601.50 rows=832 width=0) (actual time=4186.002..4186.009 rows=0 loops=1)
         Join Filter: (mc.movie_id = t.id)
         ->  Nested Loop  (cost=88096.24..1127417.26 rows=259 width=28) (actual time=4185.968..4185.975 rows=0 loops=1)
               Join Filter: (mc.movie_id = ci.movie_id)
               ->  Hash Join  (cost=51966.96..133511.38 rows=1585 width=12) (actual time=349.938..978.898 rows=224635 loops=1)
                     Hash Cond: (mk.keyword_id = k.id)
                     ->  Hash Join  (cost=49649.73..131154.91 rows=9750 width=16) (actual time=339.659..853.639 rows=1661574 loops=1)
                           Hash Cond: (mk.movie_id = mc.movie_id)
                           ->  Seq Scan on movie_keyword mk  (cost=0.00..81003.12 rows=129590 width=8) (actual time=49.389..277.374 rows=2852786 loops=1)
                                 Filter: (id > 1671144)
                                 Rows Removed by Filter: 1671144
                           ->  Hash  (cost=49570.61..49570.61 rows=6330 width=8) (actual time=254.576..254.576 rows=55505 loops=1)
                                 Buckets: 65536 (originally 8192)  Batches: 1 (originally 1)  Memory Usage: 2681kB
                                 ->  Hash Join  (cost=2672.81..49570.61 rows=6330 width=8) (actual time=80.622..248.775 rows=55505 loops=1)
                                       Hash Cond: (mc.movie_id = cc.movie_id)
                                       ->  Seq Scan on movie_companies mc  (cost=0.00..46718.11 rows=33290 width=4) (actual time=56.550..132.244 rows=572906 loops=1)
                                             Filter: (id > 2036223)
                                             Rows Removed by Filter: 2036223
                                       ->  Hash  (cost=2419.57..2419.57 rows=20259 width=4) (actual time=23.896..23.896 rows=110494 loops=1)
                                             Buckets: 131072 (originally 32768)  Batches: 2 (originally 1)  Memory Usage: 3073kB
                                             ->  Seq Scan on complete_cast cc  (cost=0.00..2419.57 rows=20259 width=4) (actual time=0.007..11.526 rows=110494 loops=1)
                                                   Filter: (status_id = 3)
                                                   Rows Removed by Filter: 24592
                     ->  Hash  (cost=2271.12..2271.12 rows=3688 width=4) (actual time=10.198..10.198 rows=18898 loops=1)
                           Buckets: 32768 (originally 4096)  Batches: 1 (originally 1)  Memory Usage: 921kB
                           ->  Seq Scan on keyword k  (cost=0.00..2271.12 rows=3688 width=4) (actual time=0.016..8.356 rows=18898 loops=1)
                                 Filter: (keyword > 115271)
                                 Rows Removed by Filter: 115272
               ->  Materialize  (cost=36129.28..990244.92 rows=154 width=16) (actual time=0.014..0.014 rows=0 loops=224635)
                     ->  Nested Loop  (cost=36129.28..990244.15 rows=154 width=16) (actual time=3051.850..3051.852 rows=0 loops=1)
                           Join Filter: (ci.movie_id = mi.movie_id)
                           Rows Removed by Join Filter: 56499
                           ->  Seq Scan on movie_info mi  (cost=0.00..265642.62 rows=719 width=4) (actual time=30.392..737.858 rows=6509 loops=1)
                                 Filter: (info_type_id = 42)
                                 Rows Removed by Filter: 14829211
                           ->  Materialize  (cost=36129.28..720579.65 rows=373 width=12) (actual time=0.028..0.354 rows=9 loops=6509)
                                 ->  Hash Join  (cost=36129.28..720577.79 rows=373 width=12) (actual time=183.584..2279.596 rows=56499 loops=1)
                                       Hash Cond: (ci.movie_id = mi_idx.movie_id)
                                       ->  Seq Scan on cast_info ci  (cost=0.00..683910.90 rows=143277 width=4) (actual time=0.041..1838.793 rows=3878229 loops=1)
                                             Filter: (person_id > 3350233)
                                             Rows Removed by Filter: 32366115
                                       ->  Hash  (cost=36126.39..36126.39 rows=231 width=8) (actual time=183.424..183.424 rows=11070 loops=1)
                                             Buckets: 16384 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 561kB
                                             ->  Hash Join  (cost=24900.11..36126.39 rows=231 width=8) (actual time=137.653..182.438 rows=11070 loops=1)
                                                   Hash Cond: (at.movie_id = mi_idx.movie_id)
                                                   ->  Seq Scan on aka_title at  (cost=0.00..11222.40 rows=589 width=4) (actual time=0.028..28.639 rows=13497 loops=1)
                                                         Filter: (kind_id = 4)
                                                         Rows Removed by Filter: 347975
                                                   ->  Hash  (cost=24710.44..24710.44 rows=15174 width=4) (actual time=121.651..121.651 rows=392297 loops=1)
                                                         Buckets: 131072 (originally 16384)  Batches: 8 (originally 1)  Memory Usage: 3073kB
                                                         ->  Seq Scan on movie_info_idx mi_idx  (cost=0.00..24710.44 rows=15174 width=4) (actual time=46.279..81.654 rows=392297 loops=1)
                                                               Filter: (id > 987738)
                                                               Rows Removed by Filter: 987738
         ->  Index Only Scan using title_pkey on title t  (cost=0.43..0.70 rows=1 width=4) (never executed)
               Index Cond: (id = ci.movie_id)
               Heap Fetches: 0
 Execution Time: 4271.519 ms
```




###  Example of speeding up long-time execution with LPCE
The query execution time drops from 723889.536ms on PostgreSQL to 1869.996ms with LPCE.

Query: 
```
SELECT COUNT(*) FROM title t,movie_companies mc,movie_info mi,movie_info_idx mi_idx,movie_keyword mk,keyword k,movie_link ml WHERE t.id=mc.movie_id AND t.id=mi.movie_id AND t.id=mi_idx.movie_id 
AND t.id=mk.movie_id AND mk.keyword_id=k.id AND t.id=ml.movie_id AND t.production_year<1980 AND mc.id>967215 AND mi.info_type_id=42 AND mi_idx.id<1073108 AND mk.id<323877 AND ml.linked_movie_id<1142364;
```

QUERY PLAN on PostgreSQL                                                                                     
```
 Aggregate  (cost=438085.18..438085.19 rows=1 width=8) (actual time=723887.508..723887.573 rows=1 loops=1)
   ->  Nested Loop  (cost=352282.24..438085.17 rows=1 width=0) (actual time=1537.609..723869.880 rows=62484 loops=1)
         Join Filter: (mk.keyword_id = k.id)
         Rows Removed by Join Filter: 8383415796
         ->  Hash Join  (cost=352282.24..434472.35 rows=1 width=4) (actual time=1382.189..1522.423 rows=62484 loops=1)
               Hash Cond: (mk.movie_id = t.id)
               ->  Seq Scan on movie_keyword mk  (cost=0.00..81003.12 rows=316526 width=8) (actual time=121.044..241.584 rows=323876 loops=1)
                     Filter: (id < 323877)
                     Rows Removed by Filter: 4200054
               ->  Hash  (cost=352282.18..352282.18 rows=5 width=20) (actual time=1257.629..1257.629 rows=1884 loops=1)
                     Buckets: 2048 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 112kB
                     ->  Hash Join  (cost=299378.17..352282.18 rows=5 width=20) (actual time=1098.082..1257.407 rows=1884 loops=1)
                           Hash Cond: (mc.movie_id = t.id)
                           ->  Seq Scan on movie_companies mc  (cost=0.00..46718.11 rows=1649559 width=4) (actual time=0.018..169.145 rows=1641914 loops=1)
                                 Filter: (id > 967215)
                                 Rows Removed by Filter: 967215
                           ->  Hash  (cost=299378.08..299378.08 rows=7 width=16) (actual time=992.582..992.582 rows=1656 loops=1)
                                 Buckets: 2048 (originally 1024)  Batches: 1 (originally 1)  Memory Usage: 94kB
                                 ->  Hash Join  (cost=270658.21..299378.08 rows=7 width=16) (actual time=851.140..992.423 rows=1656 loops=1)
                                       Hash Cond: (mi_idx.movie_id = t.id)
                                       ->  Seq Scan on movie_info_idx mi_idx  (cost=0.00..24710.44 rows=1069165 width=4) (actual time=16.579..98.994 rows=1073107 loops=1)
                                             Filter: (id < 1073108)
                                             Rows Removed by Filter: 306928
                                       ->  Hash  (cost=270657.99..270657.99 rows=17 width=12) (actual time=832.516..832.516 rows=552 loops=1)
                                             Buckets: 1024  Batches: 1  Memory Usage: 32kB
                                             ->  Nested Loop  (cost=268711.92..270657.99 rows=17 width=12) (actual time=831.343..832.465 rows=552 loops=1)
                                                   Join Filter: (mi.movie_id = t.id)
                                                   ->  Merge Join  (cost=268711.49..268817.82 rows=405 width=8) (actual time=829.655..831.048 rows=766 loops=1)
                                                         Merge Cond: (mi.movie_id = ml.movie_id)
                                                         ->  Sort  (cost=266190.65..266211.67 rows=8407 width=4) (actual time=822.496..822.501 rows=27 loops=1)
                                                               Sort Key: mi.movie_id
                                                               Sort Method: quicksort  Memory: 498kB
                                                               ->  Seq Scan on movie_info mi  (cost=0.00..265642.62 rows=8407 width=4) (actual time=710.332..821.258 rows=6509 loops=1)
                                                                     Filter: (info_type_id = 42)
                                                                     Rows Removed by Filter: 14829211
                                                         ->  Sort  (cost=2520.54..2571.07 rows=20214 width=4) (actual time=6.795..7.523 rows=20658 loops=1)
                                                               Sort Key: ml.movie_id
                                                               Sort Method: quicksort  Memory: 1720kB
                                                               ->  Seq Scan on movie_link ml  (cost=0.00..1074.93 rows=20214 width=4) (actual time=0.010..3.996 rows=20298 loops=1)
                                                                     Filter: (linked_movie_id < 1142364)
                                                                     Rows Removed by Filter: 39696
                                                   ->  Index Scan using title_pkey on title t  (cost=0.43..4.53 rows=1 width=4) (actual time=0.001..0.001 rows=1 loops=766)
                                                         Index Cond: (id = ml.movie_id)
                                                         Filter: (production_year < 1980)
                                                         Rows Removed by Filter: 0
         ->  Seq Scan on keyword k  (cost=0.00..1935.70 rows=134170 width=4) (actual time=0.001..5.600 rows=134170 loops=62484)
 Planning Time: 8.576 ms
 Execution Time: 723889.536 ms
 ```
 
 
QUERY PLAN on PostgreSQL with LPCE-I
```                                                                                
 Aggregate  (cost=427264.85..427264.86 rows=1 width=8) (actual time=1868.557..1868.562 rows=1 loops=1)
   ->  Hash Join  (cost=160193.88..427258.47 rows=2550 width=0) (actual time=1832.465..1866.497 rows=62484 loops=1)
         Hash Cond: (t.id = mi_idx.movie_id)
         ->  Hash Join  (cost=134873.05..401930.37 rows=1129 width=20) (actual time=1556.481..1573.421 rows=20828 loops=1)
               Hash Cond: (mk.keyword_id = k.id)
               ->  Hash Join  (cost=130735.23..397247.37 rows=740 width=24) (actual time=1533.831..1542.797 rows=20828 loops=1)
                     Hash Cond: (t.id = mk.movie_id)
                     ->  Nested Loop  (cost=49524.12..315718.35 rows=187 width=16) (actual time=1257.635..1258.970 rows=628 loops=1)
                           ->  Hash Join  (cost=49523.69..315169.05 rows=343 width=12) (actual time=972.402..1257.143 rows=976 loops=1)
                                 Hash Cond: (mi.movie_id = mc.movie_id)
                                 ->  Seq Scan on movie_info mi  (cost=0.00..265642.62 rows=719 width=4) (actual time=478.885..763.107 rows=6509 loops=1)
                                       Filter: (info_type_id = 42)
                                       Rows Removed by Filter: 14829211
                                 ->  Hash  (cost=49485.71..49485.71 rows=3038 width=8) (actual time=493.463..493.463 rows=35786 loops=1)
                                       Buckets: 65536 (originally 4096)  Batches: 1 (originally 1)  Memory Usage: 1910kB
                                       ->  Hash Join  (cost=48010.51..49485.71 rows=3038 width=8) (actual time=352.841..490.290 rows=35786 loops=1)
                                             Hash Cond: (ml.movie_id = mc.movie_id)
                                             ->  Seq Scan on movie_link ml  (cost=0.00..1074.93 rows=5078 width=4) (actual time=0.008..3.610 rows=20298 loops=1)
                                                   Filter: (linked_movie_id < 1142364)
                                                   Rows Removed by Filter: 39696
                                             ->  Hash  (cost=46718.11..46718.11 rows=78752 width=4) (actual time=352.388..352.388 rows=1641914 loops=1)
                                                   Buckets: 131072 (originally 131072)  Batches: 32 (originally 2)  Memory Usage: 3073kB
                                                   ->  Seq Scan on movie_companies mc  (cost=0.00..46718.11 rows=78752 width=4) (actual time=45.319..186.238 rows=1641914 loops=1)
                                                         Filter: (id > 967215)
                                                         Rows Removed by Filter: 967215
                           ->  Index Scan using title_pkey on title t  (cost=0.43..1.60 rows=1 width=4) (actual time=0.001..0.001 rows=1 loops=976)
                                 Index Cond: (id = mc.movie_id)
                                 Filter: (production_year < 1980)
                                 Rows Removed by Filter: 0
                     ->  Hash  (cost=81003.12..81003.12 rows=16639 width=8) (actual time=260.203..260.203 rows=323876 loops=1)
                           Buckets: 131072 (originally 32768)  Batches: 8 (originally 1)  Memory Usage: 3073kB
                           ->  Seq Scan on movie_keyword mk  (cost=0.00..81003.12 rows=16639 width=8) (actual time=0.031..225.671 rows=323876 loops=1)
                                 Filter: (id < 323877)
                                 Rows Removed by Filter: 4200054
               ->  Hash  (cost=1935.70..1935.70 rows=134170 width=4) (actual time=22.335..22.335 rows=134170 loops=1)
                     Buckets: 131072  Batches: 2  Memory Usage: 3392kB
                     ->  Seq Scan on keyword k  (cost=0.00..1935.70 rows=134170 width=4) (actual time=0.007..9.339 rows=134170 loops=1)
         ->  Hash  (cost=24710.44..24710.44 rows=48831 width=4) (actual time=215.226..215.226 rows=1073107 loops=1)
               Buckets: 131072 (originally 65536)  Batches: 16 (originally 1)  Memory Usage: 3380kB
               ->  Seq Scan on movie_info_idx mi_idx  (cost=0.00..24710.44 rows=48831 width=4) (actual time=0.025..111.016 rows=1073107 loops=1)
                     Filter: (id < 1073108)
                     Rows Removed by Filter: 306928
 Execution Time: 2169.996 ms
```
