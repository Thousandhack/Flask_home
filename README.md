# Flask_home
以蓝图的方式建立视图(蓝图就是路由系统这块)

home 相当于项目的代码目录

# 运行项目的命令 
python manager.py runserver


数据库运行第一次命令
>python manage.py db init

数据库第一个初始化命令
>python manage.py db migrate -m "init tables"

把数据结构更新到数据库中
>>python manage.py db upgrade

mysql> use home ;
Database changed
mysql> show tables;
+-------------------+
| Tables_in_home    |
+-------------------+
| alembic_version   |
| ih_area_info      |
| ih_facility_info  |
| ih_house_facility |
| ih_house_image    |
| ih_house_info     |
| ih_order_info     |
| ih_user_profile   |
+-------------------+
8 rows in set (0.00 sec)

mysql>


redis:字符串，列表，哈希，set
“key”:"***"
redis命令设置图片验证码键值对
设置键值对
hset image_codes id1 abc
获取键值对
hget image_codes id1

# 使用clelery需要安装
pip install eventlet

运行项目命令为
>python manage.py runserver
