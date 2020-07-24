
from flask_session import Session

from flask_wtf import CSRFProtect
from config import config_map
from home import create_app

# 创建falsk 应用对象
app = create_app("develop")



# 获取redis数据库连接
redis_store = redis.StrictRedis(host=Config.REDIS_HOST, port=Config.REDIS_PORT, db=0, password=Config.REDIS_PASSWORD)

# 利用flask-session，将session数据保存到redis中
Session(app)

# 为flask 补充csrf 防护  以钩子的方式
CSRFProtect(app)


@app.route("/index")
def index():
    return "index page"


if __name__ == "__main__":
    app.run()
