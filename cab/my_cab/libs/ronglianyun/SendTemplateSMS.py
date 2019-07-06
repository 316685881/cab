# coding=utf8

from .sms_skd import CCPRestSDK

# 主帐号
accountSid = '8aaf07086b6526f8016b7ae2cf7e10ba'

# 主帐号Token
accountToken = 'e6e0e0b24e22482d8be36f949b05bf99'

# 应用Id
appId = '8aaf07086b6526f8016b7ae2cfd110c0'

# 请求地址，格式如下，不需要写http://
serverIP = 'app.cloopen.com'

# 请求端口 
serverPort = '8883'

# REST版本号
softVersion = '2013-12-26'


class CCP(object):
    # 单例模式
    instance = None

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cpp = super(CCP, cls).__new__(cls)
            # 初始化REST SDK
            cpp.rest = CCPRestSDK.REST(serverIP, serverPort, softVersion)
            cpp.rest.setAccount(accountSid, accountToken)
            cpp.rest.setAppId(appId)
            cls.instance = cpp
        return cls.instance

    # 发送模板短信
    # @param to 手机号码
    # @param data 内容数据 格式为数组 例如：['12', '34']，如不需替换请填 ''
    # @param $tempId 模板Id
    def send_template_sms(self, to, data, temp_id):
        result = self.rest.sendTemplateSMS(to, data, temp_id)

        # if result.get('statusCode') == '000000':
        #     print('发送短信成功')
        # else:
        #     print('发送短信失败')


        # for k, v in result.iteritems():
        #
        #     if k == 'templateSMS':
        #         for k, s in v.iteritems():
        #             print('%s:%s' % (k, s))
        #     else:
        #         print('%s:%s' % (k, v))

        return result


# if __name__ == '__main__':
#     obj = CCP()
#     obj.send_template_sms('18665387514', ['222', '333'], 1)


    

    
   

