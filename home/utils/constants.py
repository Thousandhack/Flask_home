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

# 首页展示最多的房屋数量
HOME_PAGE_MAX_HOUSES = 5

# 首页房屋数据的redis缓存时间，单位：秒
HOME_PAGE_DATA_REDIS_EXPIRES = 7200

# 房屋详情页展示的评论最大数
HOUSE_DETAIL_COMMENT_DISPLAY_COUNTS = 30

# 房屋详情页面数据Redis缓存时间，单位：秒
HOUSE_DETAIL_REDIS_EXPIRE_SECOND = 7200

# 房屋列表页面每页数据容量
HOUSE_LIST_PAGE_CAPACITY = 2

# 房屋列表页面页数缓存时间，单位秒
HOUES_LIST_PAGE_REDIS_CACHE_EXPIRES = 7200

# 房屋列表页数缓存时间，单位：秒
HOUSE_LIST_PAGE_REDIS_CACHE_EXPIRES = 7200

# 支付宝支付地址域名 https://openapi.alipay.com/gateway.do? # 真是环境
ALIPAY_URL_PREFIX = "https://openapi.alipaydev.com/gateway.do?",  # 沙箱支付宝网关地址

#

app_private_key = """
-----BEGIN RSA PRIVATE KEY-----
MIIEowIBAAKCAQEA7oz2Q7NeUzA0B5FXuRghqWjlslnHHpize82qYbaG2/eKpMKp
M6IXeIKBfZ/x7ggPUVFFMvcupkONQKjvVkqk0vgJ14aDGuSCjJZHgIvnDDIt02Tq
9GB6tVVZkylBzhVvbWxuEl7iAuylw92/FAqDZ/oyx1wGM+ioCKaPJ9v0vybWXlV8
lRiPpRF5UD6ZTgYm5nJLe4KV9AJ67pR6afaMB9P1DhdsJvmnvsHcmKa3MdYd/I69
MQr857oHPMtQn3Fi37u1kakDfXLaRHJQTVqf2WA7OHN7bHdC/93zTSdQmQrzcgg+
LgvxE0hLHhvxZKzlcSOHjmZpBPiGQbVNFALr1QIDAQABAoIBAGV/6uShdDf3IZw6
tlWWM/RuIpXBZ1zYYj4CI0XSMQ11BTPXc8D5bf0jok8+d+Ts3v+dkdD+pYWu5nIl
rzhLKFhvm1ht7mjJ49ZHtwK2BEgHLcJthR8X0f5H44YfHtW9/xxS7363injuEhYF
yuCPHJxoM6TpveXmT2Dm5bBzAW83F82sr9wXFXyAw61F4xabWf56PIYbtavHkt1o
EAmolhxSiRwnUGQcyvx0Sa+C4V3hRN+BZAX17wgnT5/mDLcoHzH1j071vtbZVpFD
czddPV+nRx7EQQpJd/44mxCUwmNp5sKJtVcX/ndJfW+dzqtKwkyjg6ZS9dHtThvp
QRSlO6ECgYEA/eaCl7KGvpcHtblXubuJbdsUD7N0AW2nqJwNf3ehY9BfAHk6Xm2M
/fnWLA/EAitTYlgFToa/qGB9ial8We358ul0yreKChSkhBxbdH69gHgScmMgfPjH
aHVhAePmIn0CQB5AO2Xj03azdsRn/v+SI55UDEQ3S629xIv053UxRL0CgYEA8IX1
FjbZAbAlbr4K51pRBJC2som/D2b0etv9DnxDztXjmtEaOlaC6nsR17zQmFHsVIBM
ekjaJvuRuZPhcW0gwFGZLDsyHhlBOjuky36zszKDguCDCaD9A4REbxwVnASCvsyH
aIqBkzr+DOuIr3e8tLzObq+0z1Dwjx0od8fMUPkCgYBCUFtZfaJd0xqLZx43f3jU
fXzO4QLygI5ipmeMHFXFuR2nBQKuuRQzHXbHyVJbcq9zpyOzr9QNCS6gruiwoExB
GqKLc8aU/XE+pB1q3tNl43aF88f/fAaxDL9KfBiWd2oIDx6dpO4NRBp5cbDr1Bp6
PRccoRCELpu64wcTEPPOTQKBgCUIy0sHWPSclbbuhilHS9BDJA5rjUKm3KAKPXW8
hohTgL820S4IYhIOrxmj1g6OFrCQLLZrf0OfWrnTXlQjtHZIWihoWPgvdU6tHlvC
/5JpBbziKusRocOn2w2sqlsiiqssPPFI2li8LZ/5qEs0SZcetz5tyY5ebRvsJm4D
Ep+pAoGBAKTv197Bq3IXqqEPhk9Wd9vh2yOzrHyktNMbDlbg5zmA4/FXoyGtPExD
lNoAh7Ymas3/cg8IGj7lkxdKrXwOO4gT5CKRktKHi7QGukdV/b280UsQQN86djZ2
+60eAC7aTviTxXddFd5DZPXVmIor0LWxxKH6yr72T/tebRLiEUWr
-----END RSA PRIVATE KEY-----
"""
