# -*- coding:utf-8 -*-

from CCPRestSDK import REST

# 说明：主账号，登陆云通讯网站后，可在"控制台-应用"中看到开发者主账号ACCOUNT SID
_accountSid = '8a216da86c282c6a016c6126db3820db'

# 说明：主账号Token，登陆云通讯网站后，可在控制台-应用中看到开发者主账号AUTH TOKEN
_accountToken = '3b497397a7614721af8848e90d293ac4'

# 请使用管理控制台首页的APPID或自己创建应用的APPID
_appId = '8a216da86c282c6a016c6126db9220e2'

# 说明：请求地址，生产环境配置成app.cloopen.com
_serverIP = 'app.cloopen.com'

# 说明：请求端口 ，生产环境为8883
_serverPort = "8883"

# 说明：REST API版本号保持不变
_softVersion = '2013-12-26'


# 云通讯官方提供的发送短信代码实例
# # 发送模板短信
# # @param to 手机号码
# # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
# # @param $tempId 模板Id
#
# class CCP(object):
#     """自己封装的发送短信的辅助类"""
#
#     def __init__(self):
#         # 初始化REST SDK
#         self.rest = REST(_serverIP, _serverIP, _softVersion)
#         self.rest.setAccount(_accountSid, _accountToken)
#         self.rest.setAppId(_appId)
#
#     def send_template_sms(self, to, datas, tempID):
#         result = self.send_template_sms(to, datas, tempID)
#         for k, v in result.iteritems():
#             if k == 'templateSMS':
#                 for k, s in v.iteritems():
#                     print('%s:%s' % (k, s))
#                 else:
#                     print('%s:%s' % (k, v))


class CCP(object):
    """发送短信的辅助类"""

    def __new__(cls, *args, **kwargs):
        # 判断是否存在类属性_instance，_instance是类CCP的唯一对象，即单例
        # 判断CCP类有没有已经建好的对象，如果没有，创建一个对象，并且保存
        if not hasattr(CCP, "_instance"):
        # if cls._instance is None:
            cls._instance = super(CCP, cls).__new__(cls, *args, **kwargs)
            cls._instance.rest = REST(_serverIP, _serverPort, _softVersion)
            cls._instance.rest.setAccount(_accountSid, _accountToken)
            cls._instance.rest.setAppId(_appId)
        return cls._instance

    def send_template_sms(self, to, datas, temp_id):
        """发送模板短信"""
        # @param to 手机号码
        # @param datas 内容数据 格式为数组 例如：{'12','34'}，如不需替换请填 ''
        # @param temp_id 模板Id
        result = self.rest.sendTemplateSMS(to, datas, temp_id)
        print(result)
        # 如果云通讯发送短信成功，返回的字典数据result中statuCode字段的值为"000000"

        if result.get("statusCode") == "000000":
            # 返回0 表示发送短信成功
            return 0
        else:
            # 返回-1 表示发送失败
            return -1


if __name__ == '__main__':
    ccp = CCP()
    # 注意： 测试的短信模板编号为1[以后申请了企业账号以后可以有更多的模板]
    # 参数1: 客户端手机号码,测试时只能发给测试号码
    # 参数2: 短信模块中的数据
    #        短信验证码
    #        短信验证码有效期提示
    # 参数3: 短信模板的id,开发测试时,只能使用1
    result = ccp.send_template_sms('18666951518', ['1234', 5], 1)
    print(result)
