import os
import re
import sys
import pandas
import numpy
import argparse

lineOffset=0
add_child_card=True
groupby_use=False
add_aggregation=True
sql_path="origin.sql"
dir=os.path.join(os.getcwd(),"example_data")
plan_path="plan.txt"
feature_path="feature.txt"
sql_exe_path ="sql_exe.txt"
ad_list_path = "adjacency_list.txt"
edge_order_path="edge_order.txt"
node_order_path ="node_order.txt"
label_path="label.txt"
test_path="test.txt"
loops=-1
operation_file = None
metadata_file = None
join_file = None
filter_file = None
child_card = None
sql_label_file = None

df = pandas.read_csv('metadata.csv',index_col='name')
debug=False



idx=0
test_num=-1
aggregation="0 0 0 0 1"
nested_loop="0 0 0 1 0"
hash_join="0 0 1 0 0"
sequence_scan="0 1 0 0 0"
index_scan="1 0 0 0 0"
table_map={
'title t': '1 0 0 0 0 0 0 0 0' ,
'movie_companies mc': '0 1 0 0 0 0 0 0 0' ,
'cast_info ci': '0 0 1 0 0 0 0 0 0' ,
'movie_info mi': '0 0 0 1 0 0 0 0 0' ,
'movie_info_idx mi_idx': '0 0 0 0 1 0 0 0 0' ,
'movie_keyword mk': '0 0 0 0 0 1 0 0 0' ,
'keyword k': '0 0 0 0 0 0 1 0 0' ,
'person_info pi': '0 0 0 0 0 0 0 1 0' ,
'movie_link ml': '0 0 0 0 0 0 0 0 1'
}
# table_map={
# 'title t': '1 0 0 0 0 0' ,
# 'movie_companies mc': '0 1 0 0 0 0' ,
# 'cast_info ci': '0 0 1 0 0 0' ,
# 'movie_info mi': '0 0 0 1 0 0' ,
# 'movie_info_idx mi_idx': '0 0 0 0 1 0' ,
# 'movie_keyword mk': '0 0 0 0 0 1'
# }

table_full_dic = {
    "title t": {
        "short": "t",
        "col": ["t.id", "t.kind_id", "t.production_year"],
        "filter_col": [ "t.kind_id", "t.production_year"]

    },
    "movie_companies mc": {
        "short": "mc",
        "col": ["mc.id", "mc.company_id", "mc.movie_id", "mc.company_type_id"],
        "filter_col": [ "mc.company_id",  "mc.company_type_id"]

    },
    "cast_info ci": {
        "short": "ci",
        "col": ["ci.id", "ci.movie_id", "ci.person_id", "ci.role_id"],
        "filter_col": ["ci.person_id", "ci.role_id"]
    },
    "movie_info mi": {
        "short": "mi",
        "filter_col": [  "mi.info_type_id"],
        "col": ["mi.id",  "mi.movie_id","mi.info_type_id"]
    },
    "movie_info_idx mi_idx": {
        "short": "mi_idx",
        "col": ["mi_idx.id", "mi_idx.movie_id", "mi_idx.info_type_id"],
        "filter_col": [ "mi_idx.info_type_id"]
    },
    "movie_keyword mk": {
        "short": "mk",
        "col": ["mk.id", "mk.movie_id", "mk.keyword_id"],
        "filter_col": [  "mk.keyword_id"]
    },
    ##### new table
    "keyword k":{
        "short":"k",
        "col":["k.id","k.keyword"],
        "filter_col":["k.keyword"]
    },
    "person_info pi": {
        "short": "pi",
        "col": ["pi.id", "pi.person_id", "pi.info_type_id"],
        "filter_col": []
    },
    "movie_link ml":{
        "short":"ml",
        "col":["ml.id","ml.movie_id","ml.linked_movie_id","ml.link_type_id"],
        "filter_col":[]
    },
    "link_type lt": {
        "short": "lt",
        "col": ["lt.id", "lt.link"],
        "filter_col": ["lt.link"]
    },
    "info_type it": {
        "short": "it",
        "col": ["it.id", "it.info"],
        "filter_col": ["it.info"]
    },
    "aka_name an": {
        "short": "an",
        "col": ["an.id", "an.person_id","an.name"],
        "filter_col": ["an.name"]
    }
}
# column_map={
# 't.id': '1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
# 't.kind_id': '0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
# 't.production_year': '0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
# 'mc.id': '0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
# 'mc.company_id': '0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
# 'mc.movie_id': '0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
# 'mc.company_type_id': '0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0',
# 'ci.id': '0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0',
# 'ci.movie_id': '0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0',
# 'ci.person_id': '0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0',
# 'ci.role_id': '0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0',
# 'mi.id': '0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0',
# 'mi.movie_id': '0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0',
# 'mi.info_type_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0',
# 'mi_idx.id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0',
# 'mi_idx.movie_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0',
# 'mi_idx.info_type_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0',
# 'mk.id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0',
# 'mk.movie_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0',
# 'mk.keyword_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1'
# }
column_map={
't.id': '1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
't.kind_id': '0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
't.production_year': '0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'mc.id': '0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'mc.company_id': '0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'mc.movie_id': '0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'mc.company_type_id': '0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'ci.id': '0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'ci.movie_id': '0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'ci.person_id': '0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'ci.role_id': '0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'mi.id': '0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'mi.movie_id': '0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'mi.info_type_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'mi_idx.id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0 0',
'mi_idx.movie_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0 0',
'mi_idx.info_type_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0 0',
'mk.id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0 0',
'mk.movie_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0 0',
'mk.keyword_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0 0',
'k.id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0 0',
'k.keyword': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0 0',
'pi.id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0 0',
'pi.person_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0 0',
'pi.info_type_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0 0',
'ml.id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0 0',
'ml.movie_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0 0',
'ml.linked_movie_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1 0',
'ml.link_type_id': '0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 1'
}
operators={
    "=":"0 0 1",
    ">":"0 1 0",
    "<":"1 0 0"
}

result_path=os.path.join(dir,"result.txt")
filtered=False
def filter_timeout_sql(start=0,offset=100000):
    file = open(os.path.join(os.getcwd(), "addition/addition.sql"), "r")
    lines = file.readlines()[start:start + offset]
    file.close()
    if(not filtered):
        out_file = open(result_path, "w")
        count = 0
        line_num = len(lines)
        print("line_num:",line_num)
        for i in range(0,line_num):
            #check_and_reload_data(False)
            line=lines[i]
            print("count:", count,"execute: ", line)
            print("=================")
            process=None
            try:
                process = subprocess.Popen(["mclient", "-d", "imdb", "-f", "csv", "-s", line], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                output, unused_err = process.communicate(timeout=30)
                output = output.decode("utf-8")
                print("result:",output)
                try:
                    output=output.strip()
                    output=int(output)
                except:
                    print("no result, reload database")
                    check_and_reload_data(True)
                out_file.write(str(output)+"\n")
                out_file.flush()
                # process = subprocess.run(["pwd"], capture_output=True,timeout=1)
                # process = subprocess.run(["mclient", "-d", "imdb", "-f", "csv", "-s", line], capture_output=True,
                #                          timeout=10)
                # print("result:", process.stdout.decode())
                # out_file.write(process.stdout.decode().strip()+"\n")
                # out_file.flush()
            except Exception as e:
                process.kill()
                out_file.write("-1" + "\n")
                out_file.flush()
                print(e, e.__traceback__.tb_lineno, 'no result')
            count += 1
        out_file.close()
    result_file=open(result_path,"r")
    result_lines=result_file.readlines()[start:start+offset]
    result_file.close()
    line_num=len(result_lines)
    print("result linenum:",line_num)
    filtered_sql_file=open(os.path.join(dir,sql_path), "w")
    valid_count=0
    for i in range(0,line_num):
        try:
            line=result_lines[i]
            if (line.strip().isdigit()):
                number = int(line.strip())
                if number >0 and number < 200:
                    valid_count+=1
                    filtered_sql_file.write(lines[i].strip()+"\n")
        except:
            break
    print("valid count:",valid_count)
size_pattern=re.compile("(\d+)G\t[a-z/_]+mydbfarm")

class SQL:
    def __init__(self):
        self.table=set()
        self.filter=set()
        self.join=set()
    def print_sql(self,file=sys.stdout):
        table_list=list(self.table)
        table_list.sort()
        filter_list=list(self.filter)
        filter_list.sort()
        join_list=list(self.join)
        join_list.sort()
        print("select count(*) from ",end="",file=file)
        print(",".join(str(i) for i in table_list),end="",file=file)
        if(len(self.filter)>0 or len(self.join)>0):
            print(" where ",end="",file=file)
        print(" AND ".join(str(i) for i in join_list),end="",file=file)
        if(len(self.filter)>0 and len(self.join)>0):
            print(" AND ",end="",file=file)
        print(" AND ".join(str(i) for i in filter_list),end="",file=file)
        print(";\n",end="",file=file)

class MetaData:
    def __init__(self):
        self.table=set()
        self.columns=set()
        self.filter = set()

def eliminate_space(path):
    feature_file = open(path, "r")
    data_file = feature_file.readlines()
    feature_file.close()
    feature_file = open(path, "w")
    for i in data_file:
        if (len(i.strip()) > 0):
            print(i.strip(), file=feature_file)
def clean_dir():
    g = os.listdir(dir)
    for file_name in g:
        if(os.path.isfile(os.path.join(dir,file_name))):
            if(file_name.find("plan")==-1 and file_name.find("sql")==-1 and file_name.find(".py")==-1):
                print("reformat ",file_name,":")
                eliminate_space(os.path.join(dir,file_name))

join_filter_pattern=re.compile("([a-z._]+)\s*=\s*([a-z._]+)",re.IGNORECASE)
filter_pattern = re.compile("([a-z._]+)\s+([<>=])\s+(\d+)", re.IGNORECASE)
hash_pattern = re.compile("Hash Cond: \(([a-z._]+)\s+=\s+([a-z._]+)\)", re.IGNORECASE)
index_join_pattern=re.compile("on\s+([a-z._]+)\s([a-z]+)\s+.*\n.*Index Cond: \(([a-z_.]+) = ([a-z_.]+)\)", re.IGNORECASE)
index_join_pattern_replace=re.compile("on\s+([a-z._]+)\s([a-z]+)\s+.*\n.*Index Cond: \(([a-z_.]+) = (\d+)\)", re.IGNORECASE)

def get_metadata(treeNode):
    raw_data = treeNode.data.raw_data
    if (raw_data.find("Seq Scan") != -1 or raw_data.find("Index Scan") != -1 or raw_data.find("Index Only Scan") != -1):
        for i in table_full_dic.keys():
            if (raw_data.find(i) != -1):
                treeNode.data.tables.append(i)
        try:
            assert len(treeNode.data.tables)==1
        except:
            print("seq scan on more than one table or no table")
            for k in treeNode.data.tables:
                print(k)
        if (raw_data.find("Filter") != -1 and raw_data.find("Join Filter:") == -1):
            filter_list = filter_pattern.findall(raw_data)
            filter_num = len(filter_list)
            for filter in filter_list:
                table=treeNode.data.tables[0]
                treeNode.data.col_filter.append(table_full_dic[table]["short"]+"."+filter[0] + filter[1] + filter[2])
                colname=table_full_dic[table]["short"] + "." + filter[0].strip()
                treeNode.data.columns.add(colname)
                zi = int(filter[2].strip()) - int(df["min"].get(colname))
                mu = int(df["max"].get(colname)) - int(df["min"].get(colname))
                #print("fenzi:",colname,int(filter[2].strip()),int(df["min"].get(colname)),zi)
                #print("fenmu:",colname,int(df["max"].get(colname)),int(df["min"].get(colname)),mu)

                number_encode = zi / mu
                treeNode.data.filter_encode.append(column_map[colname]+" "+operators[filter[1]]+" "+str(number_encode))
    if (raw_data.find("Hash Join") != -1 ):
        match=hash_pattern.findall(raw_data)
        assert len(match)==1
        assert len(match[0])==2
        treeNode.data.join_filter.append(match[0][0]+"="+match[0][1])
        treeNode.data.columns.add(match[0][0])
        treeNode.data.columns.add(match[0][1])
        treeNode.data.join_encode.append(column_map[match[0][0]]+" "+operators["="]+" "+column_map[match[0][1]])
    elif(raw_data.find("Nested Loop")!=-1):
        if(raw_data.find("Join Filter")!=-1):
            match = join_filter_pattern.findall(raw_data)
            assert len(match) == 1
            treeNode.data.columns.add(match[0][0])
            treeNode.data.columns.add(match[0][1])
            treeNode.data.join_filter.append(match[0][0] + "=" + match[0][1])
            treeNode.data.join_encode.append(column_map[match[0][0]] +" "+ operators["="] +" "+ column_map[match[0][1]])
        elif treeNode.left.data.raw_data.find("Index Cond")!=-1 or treeNode.right.data.raw_data.find("Index Cond")!=-1:
            if(treeNode.left.data.raw_data.find("Index Cond")!=-1):
                match=index_join_pattern.findall(treeNode.left.data.raw_data)
                match2=index_join_pattern_replace.findall(treeNode.left.data.raw_data)
                print("len(match)",len(match))
                assert len(match)==1 or len(match2)==1
                if(len(match)==1):
                    col1 = match[0][1] + "." + match[0][2]
                    col2 = match[0][3]
                else:
                    col1 = match2[0][1] + "." + match2[0][2]
                    col2 = "mk.keyword_id"
                # treeNode.data.filter.add(match[0][1]+"."+match[0][2]+" = "+match[0][3])
                treeNode.data.join_encode.append(
                    column_map[col1] + " " + operators["="] + " " + column_map[col2])
                treeNode.data.join_filter.append(col1+ "=" +col2)
                treeNode.data.columns.add(col1)
                treeNode.data.columns.add(col2)
            else:
                assert treeNode.right!=None
                assert treeNode.right.data.raw_data.find("Index Cond") != -1 or treeNode.right.data.raw_data.find("person_id")!=-1
#                print("data:",treeNode.right.data.raw_data)
                match=index_join_pattern.findall(treeNode.right.data.raw_data)
                match2=index_join_pattern_replace.findall(treeNode.right.data.raw_data)
                print("len(match)",len(match))
                assert len(match)==1 or len(match2)==1
                if(len(match)==1):
                    col1 = match[0][1] + "." + match[0][2]
                    col2 = match[0][3]
                else:
                    col1 = match2[0][1] + "." + match2[0][2]
                    col2 = "mk.keyword_id"
                # treeNode.data.filter.add(match[0][1]+"."+match[0][2]+" = "+match[0][3])
                treeNode.data.join_encode.append(
                    column_map[col1] + " " + operators["="] + " " + column_map[col2])
                treeNode.data.join_filter.append(col1 + "=" + col2)
                treeNode.data.columns.add(col1)
                treeNode.data.columns.add(col2)
        elif treeNode.left.data.raw_data.find("person_id")!=-1 or treeNode.right.data.raw_data.find("person_id")!=-1:
            print("data verify:",treeNode.left.data.raw_data,treeNode.right.data.raw_data)
            col1="ci.person_id"
            col2="pi.person_id"
            treeNode.data.join_encode.append(
                column_map[col1] + " " + operators["="] + " " + column_map[col2])
            treeNode.data.join_filter.append(col1 + "=" + col2)
            treeNode.data.columns.add(col1)
            treeNode.data.columns.add(col2)

    data = numpy.zeros(len(column_map), dtype=int)
    for i in treeNode.data.columns:
        cur=numpy.array(column_map[i].split(),dtype='i')
        data=numpy.bitwise_or(data,cur)
    treeNode.data.metadata_encode=" ".join(str(i) for i in data)
def init_operation(treeNode):
    raw_data=treeNode.data.raw_data
    if (raw_data.find("Aggregate") != -1):
        treeNode.data.operation="aggregation"
        treeNode.data.operation_encode=aggregation
    if (raw_data.find("Nested Loop") != -1):
        treeNode.data.operation="nested_loop"
        treeNode.data.operation_encode=nested_loop
    if (raw_data.find("Hash Join") != -1):
        treeNode.data.operation="hash_join"
        treeNode.data.operation_encode=hash_join
    if (raw_data.find("Seq Scan") != -1):
        treeNode.data.operation="seq_scan"
        treeNode.data.operation_encode=sequence_scan
    if (raw_data.find("Index Scan") != -1 or raw_data.find("Index Only Scan") != -1):
        treeNode.data.operation="index_scan"
        treeNode.data.operation_encode=index_scan
def split_tree():
    f = open(os.path.join(dir,plan_path), "r")
    lines = f.readlines()
    f.close()
    line_num=len(lines)
    plans=[]
    for i in range(0,line_num):
        if(lines[i].find("QUERY PLAN") != -1):
            plans.append(list())
            plans[plans.__len__()-1].append(lines[i])
            continue
        else:
            plans[plans.__len__()-1].append(lines[i])
    return plans
def process_plan(plan:list):
    root=None
    levelDict = dict()
    for line_index in range(0, plan.__len__()):
        if (plan[line_index].find("QUERY PLAN") != -1):
            pass
        elif (plan[line_index].find("->") != -1):
            operation_info = plan[line_index]
            max_index = len(plan) - 1
            line_counter = 1
            while True:
                if ((line_index + line_counter) > max_index):
                    break
                if (plan[line_index + line_counter].find("QUERY PLAN") != -1):
                    break
                if (plan[line_index + line_counter].find("->") != -1):
                    break
                else:
                    operation_info += plan[line_index + line_counter]
                    line_counter += 1
            offset = plan[line_index].find("->")
            data = Data(offset, operation_info)
            newNode = TreeNode(data)
            if(root==None):
                root=newNode
                levelDict[offset]=newNode
            else:
                levelDict[offset] = newNode
                array = sorted(levelDict.keys())
                lastKey = None
                if (len(array) >= 1):
                    lastKey = array[0]
                for key in array:
                    if (key >= offset):
                        levelDict[lastKey].insert(newNode)
                        break
                    else:
                        lastKey = key
    return root
def generate_tree():
    plans=split_tree()
    treeRoots=list()
    for j in range(0,plans.__len__()):
        plan = plans[j]
        treeRoot=process_plan(plan)
        treeRoots.append(treeRoot)
    count = 0
    sql_file=open(os.path.join(dir,sql_exe_path),"w")
    adjacency_list_file = open(os.path.join(dir, ad_list_path), "w")
    edge_order_file = open(os.path.join(dir , edge_order_path), "w")
    execution_order_file=open(os.path.join(dir,"execution_order.txt"),"w")
    node_order_file = open(os.path.join(dir , node_order_path), "w")
    if(add_child_card):
        cardinality_lines=open(os.path.join(dir,label_path),"r").readlines()
    global lineOffset
    for i in treeRoots:
        lineOffset+=1
        count+=1
        preDelete(i) ## delete parallel hash
        if(i.data.raw_data.find("Hash Join")==-1
              and i.data.raw_data.find("Nested Loop")==-1
                and i.data.raw_data.find("Seq Scan")==-1
                and i.data.raw_data.find("Index Scan")==-1
                and i.data.raw_data.find("Index Only Scan") == -1
                and i.data.raw_data.find("Aggregate")==-1
        ):
            i.left.data.offset = i.data.offset
            i.left.parent = i.parent
            i = i.left
        if(not groupby_use):
            if (i.data.raw_data.find("Aggregate") != -1):
                i.left.data.offset = i.data.offset
                i.left.parent = i.parent
                i = i.left
        if(add_aggregation):
            data = Data(0, "Aggregate")
            newNode = TreeNode(data)
            i.parent=newNode
            newNode.left=i
            i=newNode
        exchangeUpandDown(i)
        exchange(i)  ## exchange hash join to the left

        global idx  ## used for node index
        idx=0

        if(add_child_card):
            get_cardinality(i, cardinality_lines)
        extract_feature(i)
        print_operation(count,i, file=operation_file)
        print_metadata(count,i, file=metadata_file)
        print_join(count,i, file=join_file)
        print_filter(count,i, file=filter_file)
        print_childcardinality(count,i, file=child_card)
        initNodeLevel(i,i)
        nodeAndAjancylist_depth(i,i)
        print("plan ",count,file=adjacency_list_file)
        for j in i.ajancylist:
            print(j[0],j[1],file=adjacency_list_file)
        initNodeOrder_depth(i)

        print("plan ",count,file=node_order_file)
        printTreeOrder_depth(i,file=node_order_file)
        print("",file=node_order_file)
        print("plan ",count,file=edge_order_file)
        printEdgeOrder_depth(i,i,edge_order_file)
        print("",file=edge_order_file)
        zero=[0]
        initExecutionOrder(i,zero)
        print("plan ",count,file=execution_order_file)
        printExecutionOrder(i,execution_order_file)
        print("",file=execution_order_file)
        ##order

        print("select \'plan "+str(count)+"\';", file=sql_file)
        foreOrder(i,file=sql_file)
        print("plan", count," done")
    sql_label_file.close()
def exchangeUpandDown(treeNode):
    if (treeNode == None):
        return
    if(treeNode.left!=None and treeNode.right!=None):
        temp=treeNode.left
        treeNode.left=treeNode.right
        treeNode.right=temp
    exchangeUpandDown(treeNode.left)
    exchangeUpandDown(treeNode.right)
def print_operation(count,treeNode,file):
    if(treeNode==None):
        return
    if(treeNode.parent==None):
        print("plan",count,file=file)
    assert treeNode.data.operation_encode!=None
    print(treeNode.data.operation_encode.strip(),file=file)
    print_operation(count,treeNode.left,file)
    print_operation(count,treeNode.right,file)
def print_metadata(count, treeNode, file):
    if(treeNode==None):
        return
    if(treeNode.parent==None):
        print("plan",count,file=file)
    assert treeNode.data.metadata_encode!=None
    print(treeNode.data.metadata_encode,file=file)
    print_metadata(count,treeNode.left,file)
    print_metadata(count,treeNode.right,file)

join_len=len(column_map.keys())+len(operators.keys())+len(column_map.keys())
no_join_list=[0]*join_len
no_join=' '.join(str(i) for i in no_join_list)
def print_join(count, treeNode, file):
    if(treeNode==None):
        return
    if(treeNode.parent==None):
        print("plan",count,file=file)
    if(len(treeNode.data.join_encode)==0):
        print(no_join,file=file)
    elif(len(treeNode.data.join_encode)==1):
        print(treeNode.data.join_encode[0], file=file)
    else:
        print("plan",count,"has more than 1 joins")
        print("raw_data:",treeNode.data.raw_data)
        assert False
    print_join(count,treeNode.left,file)
    print_join(count,treeNode.right,file)
one_filter_len=len(column_map.keys())+len(operators.keys())+1
one_filter_list=[0]*one_filter_len
one_filter=" ".join(str(i) for i in one_filter_list)
def print_filter(count, treeNode, file):
    if(treeNode==None):
        return
    if(treeNode.parent==None):
        print("plan",count,file=file)
    if(len(treeNode.data.filter_encode)==0):
        print(one_filter,one_filter,file=file)
    elif(len(treeNode.data.filter_encode)==1):
        print(treeNode.data.filter_encode[0],one_filter, file=file)
    elif (len(treeNode.data.filter_encode) == 2):
        print(treeNode.data.filter_encode[0],treeNode.data.filter_encode[1], file=file)
    else:
        print("plan",count,"has more than 2 filters")
        assert False
    print_filter(count,treeNode.left,file)
    print_filter(count,treeNode.right,file)

def print_childcardinality(count,treeNode,file):
    if(treeNode==None):
        return
    if(treeNode.parent==None):
        print("plan",count,file=file)
    if(treeNode.data.operation.find("aggregate")!=-1):
        print(0, 0, file=file)
    elif(treeNode.left!=None and treeNode.right!=None):
        print(treeNode.left.data.cardinality,treeNode.right.data.cardinality,file=file)
    elif(treeNode.left!=None and treeNode.right==None):
        print(treeNode.left.data.cardinality, treeNode.left.data.cardinality,file=file)
    elif(treeNode.left==None and treeNode.right!=None):
        print(treeNode.right.data.cardinality, treeNode.left.data.cardinality,file=file)
    else:
        print(treeNode.data.cardinality,treeNode.data.cardinality,file=file)
    print_childcardinality(count,treeNode.left,file)
    print_childcardinality(count,treeNode.right,file)


def foreOrder(treeNode,file):
    if(treeNode==None):
        return
    if(treeNode.data.operation.find("Hash")!=-1 and treeNode.data.operation.find("Hash Join")==-1):
        assert False
    sql=sql_deepOrder(treeNode)
    sql.print_sql(file=file)
    foreOrder(treeNode.left,file=file)
    foreOrder(treeNode.right,file=file)

def get_ChildCardinality(treeNode, file=sys.stdout):
    if(treeNode==None):
        return
    if(treeNode.left==None and treeNode.right==None):
        assert len(treeNode.data.tables)==1
        table_short=treeNode.data.tables[0].split(" ")[1]
        tableScale=df.at[table_short+".id",'cardinality']
        treeNode.data.childCardinality=(tableScale,tableScale)
    elif(treeNode.left!=None and treeNode.right==None):
        treeNode.data.childCardinality=(treeNode.left.data.cardinality,treeNode.left.data.cardinality)
        #print(treeNode.data.childCardinality[0],treeNode.data.childCardinality[1],file=file)
    elif(treeNode.left==None and treeNode.right!=None):
        treeNode.data.childCardinality=(treeNode.right.data.cardinality,treeNode.right.data.cardinality)
    else:
        treeNode.data.childCardinality = (treeNode.left.data.cardinality, treeNode.right.data.cardinality)




def sql_deepOrder(treeNode):

    if(treeNode==None):
        return SQL()
    if(treeNode.data.operation.find("Hash")!=-1 and treeNode.data.operation.find("Hash Join")==-1):
        assert False
    currentsql = SQL()
    for i in treeNode.data.tables:
        currentsql.table.add(i)
    for i in treeNode.data.join_filter:
        currentsql.join.add(i)
    for i in treeNode.data.col_filter:
        currentsql.filter.add(i)
    leftsql=sql_deepOrder(treeNode.left)
    rightsql=sql_deepOrder(treeNode.right)
    for i in leftsql.join:
        currentsql.join.add(i)
    for i in rightsql.join:
        currentsql.join.add(i)
    for i in leftsql.table:
        currentsql.table.add(i)
    for i in leftsql.filter:
        currentsql.filter.add(i)
    for i in rightsql.table:
        currentsql.table.add(i)
    for i in rightsql.filter:
        currentsql.filter.add(i)
    treeNode.sql=currentsql
    return currentsql



def nodeAndAjancylist(treeNode,root):
    ajancylist=root.ajancylist
    queue=list()
    queue.append(treeNode)
    while len(queue)>0:
        treeNode=queue.pop(0)
        if(treeNode.left!=None):
            ajancylist.append((treeNode.index,treeNode.left.index))
            queue.append(treeNode.left)
        if(treeNode.right!=None):
            ajancylist.append((treeNode.index,treeNode.right.index))
            queue.append(treeNode.right)

def nodeAndAjancylist_depth(treeNode,root):
    if(treeNode!=None):
        ajancylist=root.ajancylist
        if(treeNode.left!=None):
            ajancylist.append((treeNode.index,treeNode.left.index))
            nodeAndAjancylist_depth(treeNode.left, root)
        if(treeNode.right!=None):
            ajancylist.append((treeNode.index,treeNode.right.index))
            nodeAndAjancylist_depth(treeNode.right, root)

def mergeData():
    operations=open(os.path.join(dir,"operation.txt"),"r").readlines()
    meta_datas=open(os.path.join(dir,"metadata.txt"),"r").readlines()
    filters=open(os.path.join(dir,"filter.txt"),"r").readlines()
    joins=open(os.path.join(dir,"join.txt"),"r").readlines()
    child=None
    if(add_child_card):
        child=open(os.path.join(dir,"child_card.txt"),"r").readlines()

    feature=open(os.path.join(dir,feature_path),"w")
    old=sys.stdout
    sys.stdout=feature
    for i in range(0,len(operations)):
        if(i==loops):
            break
        if(operations[i].find("plan")!=-1):
            print(operations[i])
        else:
            print(operations[i].strip(),end=" ")
            #print(meta_datas[i].strip(),end=" ")
            print(filters[i].strip(),end=" ")
            print(joins[i].strip(),end=" ")
            if(add_child_card):
                print(child[i].strip(),end=" ")
            print("")
    sys.stdout=old

def extract_feature(treeNode):
    global idx
    if(treeNode!=None):
        treeNode.index=idx
        idx+=1
        init_operation(treeNode)
        print(file=operation_file)
        get_metadata(treeNode)
        print(file=metadata_file)
        if(add_child_card):
            get_ChildCardinality(treeNode, file=child_card)
        #get_sample(treeNode)
        extract_feature(treeNode.left)
        extract_feature(treeNode.right)
def get_cardinality(treeNode,data):
    if(treeNode!=None):
        global lineOffset
        treeNode.data.cardinality=int(data[lineOffset])
        lineOffset+=1
        #print("operation:",treeNode.data.operation,"cardinality:",treeNode.data.cardinality)
        get_cardinality(treeNode.left,data)
        get_cardinality(treeNode.right,data)
def printNodeLevel(treeNode,file):
    queue=list()
    queue.append(treeNode)
    while len(queue)>0:
        treeNode=queue.pop(0)
        print(treeNode.nodeLevel,end=" ",file=file)
        if(treeNode.left!=None):
            queue.append(treeNode.left)
        if(treeNode.right!=None):
            queue.append(treeNode.right)

def printNodeLevel_depth(treeNode,file):
    if(treeNode==None):
        return
    print(treeNode.nodeLevel, end=" ", file=file)
    printNodeLevel_depth(treeNode.left,file)
    printNodeLevel_depth(treeNode.right,file)

def printEdgeOrder(treeNode,root,file):
    queue=list()
    queue.append(treeNode)
    while len(queue)>0:
        treeNode=queue.pop(0)
        if(treeNode.parent!=None):
            print(root.maxDepth-treeNode.nodeLevel+1,end=" ",file=file)
        if(treeNode.left!=None):
            queue.append(treeNode.left)
        if(treeNode.right!=None):
            queue.append(treeNode.right)


def printEdgeOrder_depth(treeNode,root,file):
    if(treeNode!=None):
        if(treeNode.parent!=None):
            print(treeNode.parent.nodeOrder,end=" ",file=file)
        printEdgeOrder_depth(treeNode.left,root,file)
        printEdgeOrder_depth(treeNode.right,root,file)


def printTreeOrder(treeNode,file):
    queue=list()
    queue.append(treeNode)
    while len(queue)>0:
        treeNode=queue.pop(0)
        print(treeNode.nodeOrder,end=" ",file=file)
        if(treeNode.left!=None):
            queue.append(treeNode.left)
        if(treeNode.right!=None):
            queue.append(treeNode.right)

def printTreeOrder_depth(treeNode,file):
    if(treeNode==None):
        return
    print(treeNode.nodeOrder,end=" ",file=file)
    printTreeOrder_depth(treeNode.left,file)
    printTreeOrder_depth(treeNode.right,file)
def printExecutionOrder(treeNode,file):
    if(treeNode==None):
        return
    print(treeNode.data.execution_order,end=" ",file=file)
    printExecutionOrder(treeNode.left,file)
    printExecutionOrder(treeNode.right,file)
def printOrder(treeNode,file):
    queue=list()
    queue.append(treeNode)
    while len(queue)>0:
        treeNode=queue.pop(0)
        print(treeNode.nodeOrder,end=" ",file=file)
        if(treeNode.left!=None):
            queue.append(treeNode.left)
        if(treeNode.right!=None):
            queue.append(treeNode.right)


def preDelete(treeNode):
    if (treeNode == None):
        return
    if(treeNode.left!=None):
        while(treeNode.left.data.raw_data.find("Hash Join")==-1
              and treeNode.left.data.raw_data.find("Nested Loop")==-1
                and treeNode.left.data.raw_data.find("Seq Scan")==-1
                and treeNode.left.data.raw_data.find("Index Scan")==-1
              and treeNode.left.data.raw_data.find("Index Only Scan") == -1
                and  treeNode.left.data.raw_data.find("Aggregate")==-1
                ):
            treeNode.left.delete()
        if(not groupby_use):
            while(treeNode.left.data.raw_data.find("Aggregate")!=-1):
                treeNode.left.delete()
    if(treeNode.right!=None):
        while(treeNode.right.data.raw_data.find("Hash Join")==-1
              and treeNode.right.data.raw_data.find("Nested Loop")==-1
                and treeNode.right.data.raw_data.find("Seq Scan")==-1
                and treeNode.right.data.raw_data.find("Index Only Scan") == -1
                and treeNode.right.data.raw_data.find("Index Scan")==-1

              and treeNode.right.data.raw_data.find("Aggregate") == -1
        ):
            treeNode.right.delete()
        if (not groupby_use):
            while(treeNode.right.data.raw_data.find("Aggregate")!=-1):
                treeNode.right.delete()
    preDelete(treeNode.left)
    preDelete(treeNode.right)

def exchange(treeNode):
    if (treeNode == None):
        return
    if(treeNode.left!=None and treeNode.right!=None):
        if(
                (treeNode.left.data.raw_data.find("Seq Scan")!=-1
                and
                 treeNode.right.data.raw_data.find("Hash Join")!=-1
                )
            or (
                treeNode.left.data.raw_data.find("Seq Scan") != -1
                and treeNode.right.data.raw_data.find(
                "Nested Loop") != -1
        )
            or (
                treeNode.left.data.raw_data.find("Index Scan") != -1
                and treeNode.right.data.raw_data.find(
            "Nested Loop") != -1
        )
            or (
                (
                        treeNode.left.data.raw_data.find("Index Scan") != -1
                        and treeNode.right.data.raw_data.find(
                    "Hash Join") != -1
                )
        )
        ):
            #print("change:",treeNode.left.data.operation,treeNode.right.data.operation)
            temp=treeNode.left
            treeNode.left=treeNode.right
            treeNode.right=temp

    exchange(treeNode.left)
    exchange(treeNode.right)


def initNodeOrder(treeNode,root):
   # print()
    if(treeNode==None):
        return
    if(treeNode.parent==None):
        treeNode.nodeOrder=root.maxDepth
    else:
        treeNode.nodeOrder=treeNode.parent.nodeOrder-1
    initNodeOrder(treeNode.left,root)
    initNodeOrder(treeNode.right,root)
def initExecutionOrder(treeNode,count:list):
    if(treeNode==None):
        return
    initExecutionOrder(treeNode.left,count)
    initExecutionOrder(treeNode.right,count)
    treeNode.data.execution_order=count[0]
    count[0]+=1

def initNodeOrder_depth(treeNode):
    if(treeNode==None):
        return
    initNodeOrder_depth(treeNode.left)
    initNodeOrder_depth(treeNode.right)
    if(treeNode.left==None and treeNode.right==None):
        treeNode.nodeOrder=0
    else:
        if(treeNode.right==None or treeNode.left.nodeOrder>treeNode.right.nodeOrder):
            treeNode.nodeOrder=treeNode.left.nodeOrder+1
        else:
            treeNode.nodeOrder = treeNode.right.nodeOrder + 1

def initNodeLevel(treeNode,root):
    if(treeNode==None):
        return
    if( treeNode.parent==None):
        treeNode.nodeLevel=0
    else:
        treeNode.nodeLevel=treeNode.parent.nodeLevel+1
    if(root.maxDepth<treeNode.nodeLevel):
        root.maxDepth = treeNode.nodeLevel
    initNodeLevel(treeNode.left,root)
    initNodeLevel(treeNode.right,root)
class TreeNode():
    def delete(self):
        # print("data offset:",self.data.offset)
        # print("children data offset:",self.left.data.offset)
        if(self.parent!=None):
            if(self.parent.left==self):
                if(self.left!=None):
                    self.left.data.offset=self.data.offset
                    self.left.parent=self.parent
                self.parent.left=self.left
            if(self.parent.right==self):
                if(self.left!=None):
                    self.left.data.offset=self.data.offset
                    self.left.parent = self.parent
                self.parent.right=self.left

    def __init__(self,data,left =None, right =None, parent=None):
        self.ajancylist=[]
        self.index=0
        self.maxDepth=0
        self.data=data
        self.left=left
        self.right=parent
        self.parent=None
        self.sql=None
        self.nodeOrder=0
        self.nodeLevel=0
    def insert(self,treeNode):
        treeNode.parent=self
        if(self.left==None):
            self.left=treeNode
        elif(self.right==None):
            self.right=treeNode
        else:
            print("this is not bitree, please check!")
            assert False
class Data():
    def __init__(self,offset:int,raw_data:str):
       # self.lastOffset=lastOffset
        self.tables=list()
        self.offset=offset
        self.raw_data=raw_data
        self.join_filter=list()
        self.col_filter=list()
        self.operation_encode=None
        self.columns=set()
        self.filter_encode=list()
        self.join_encode=list()
        self.cardinality=0
        self.childCardinality=(0,0)
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_dir", help="input_dir", type=str, default=os.path.join(os.getcwd(),"example_data"))
    parser.add_argument("--add_child", help="add_child_cardinality", type=bool, default=False)
    parser.add_argument("--add_agg", help="add aggregation operation", type=bool, default=True)
    args=parser.parse_args()
    global dir,add_child_card,add_aggregation
    dir=args.input_dir
    add_child_card=args.add_child
    add_aggregation=args.add_agg
    global operation_file,metadata_file,join_file,filter_file,child_card,sql_label_file
    operation_file = open(os.path.join(dir, "operation.txt"), "w")
    metadata_file = open(os.path.join(dir, "metadata.txt"), "w")
    join_file = open(os.path.join(dir, "join.txt"), "w")
    filter_file = open(os.path.join(dir, "filter.txt"), "w")
    child_card = open(os.path.join(dir, 'child_card.txt'), "w")
    sql_label_file = open(os.path.join(dir, "sql_exe.txt"), "w")
    generate_tree()
    operation_file.close()
    metadata_file.close()
    join_file.close()
    filter_file.close()
    child_card.close()
    clean_dir()
    mergeData()
    clean_dir()
main()



