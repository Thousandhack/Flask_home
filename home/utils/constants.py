# 常量数据的保存的文件

# 图片验证码的redis有效期，单位：秒
IMAGE_CODE_REDIS_EXPIRES = 180

# 短信验证码有效期 单位:秒
SMS_CODE_REDIS_EXPIRES = 300

# 发送短信验证码的间隔,单位：秒
SEND_SMS_CODE_INTERVAL = 60

# 登录错误尝试次数
LOGIN_ERROR_MAX_TIMES = 5

# 登录错误禁止时间 单位：秒
LOGIN_ERROR_FORBIN_TIME = 300

# 七牛云域名
QINIU_URL_DOMAIN = 'http://o92qujngh.bkt.clouddn.cpm/'

# 城区信息的缓存时间 单位：秒
AREA_INFO_REDIS_CACHE_EXPIRES = 3600
