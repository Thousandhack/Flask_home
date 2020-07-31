from qiniu import Auth, put_file, etag, put_data
import qiniu.config

# 需要填写你的Access Key 和 Secret Key
access_key = 'Access_key'
secret_key = 'Secret_Key'


def storage(file_data):
    """
    上传文件到七牛
    :param file_data:要上传的文件数据
    :return:
    """
    # 构建鉴权对象
    q = Auth(access_key, secret_key)

    # 要上传的空间
    buckert_name = 'Buckert_name'

    # 生成上传Token,可以指定过期时间等
    token = q.upload_token(buckert_name, None, 3600)

    # 要上传的本地路径
    # localfile = './sync/bbb.jpg'

    ret, info = put_data(token, None, file_data)  # None表示让七牛自动生成文件名
    if info.status_code == 200:
        # 表示上传成功


    print(ret)  # 返回一个结果对象
    print(info)  # info['key']  为文件名
