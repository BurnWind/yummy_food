import redis

#注意默认情况下，设置的值或取得的值都为bytes类型,如果想改为str类型,需要在连接时添加上decode_responses=True
pool = redis.ConnectionPool(host='localhost',port=6379,decode_responses=True)

r = redis.Redis(connection_pool=pool)
pipeline = r.pipeline()
# with pipeline as p:
#     p.set("haha","dsa")
#     p.expire("haha", 60)
#     p.execute()

# print(r.get("haha"))