import requests
import json
import base64
import time
import datetime
import ddddocr
import ssl
import math

# 你的原始设置
cookie = "route=de1353bd2eecd92e44c51ddb2c26661d; EMAP_LANG=zh; GS_SESSIONID=0b091302e0e31c2f5433de4abef36edc; _WEU=CDA2krgoCLIO9j6fVy10XPvKz*CwPMoneGr2WNrRTX_roTklcuONDB4tBvg1PkEApBfJoXRSlo_C9Yiva0KSBCf4D_AYS*_0AOIgCsTT5PDnUecRy1E235I464V*oPBZPevfdy8a0cHgVaEz1y7adFe2uVFn02DfUfsupBjdrJxj5DNJv7P7iTqKuV0AlnEwAzgguqfisisbOdn0T801Yoq3Ih6_Eu0lcWD9k9YjUzg03HcMNb4GEEPi9gKPhmaQDG7DMzf*OmSlI6P*MCmIPMvpHl0ZUe58JgWis2TWwgKmGR1rrGXTCLzeHkI424bFWPmlSNu_KOc.; amp.locale=zh_CN; JSESSIONID=WHclK-5nChaZT4ga6wxXlMnA5bEJ_a4DK1NumID1PqhEeilIq0aw!11941531"
target_time = datetime.datetime(2024, 11, 13, 18, 59, 59)
test = 0

list_url = 'https://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/hdyy/queryActivityList.do'
code_url = 'https://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/hdyy/vcode.do'
app_url = 'https://ehall.seu.edu.cn/gsapp/sys/jzxxtjapp/hdyy/yySave.do'
ocr = ddddocr.DdddOcr()
header = {
    'Cookie': cookie,
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36 Edg/130.0.0.0',
}
data = {
    '_': str(int(time.time() * 1000)),
}
wid = ''

class TLSAdapter(requests.adapters.HTTPAdapter):
    def init_poolmanager(self, *args, **kwargs):
        ctx = ssl.create_default_context()
        ctx.check_hostname = False  # 关闭主机名检查
        ctx.set_ciphers("DEFAULT@SECLEVEL=1")
        ctx.options |= 0x4  # OP_LEGACY_SERVER_CONNECT
        kwargs["ssl_context"] = ctx
        return super(TLSAdapter, self).init_poolmanager(*args, **kwargs)

def get_json(s, parm=None):
    response = s.post(list_url, data=data, params=parm, verify=False)
    txt = response.content.decode('utf-8', 'ignore')
    return json.loads(txt)

def get_list(s):
    jt = get_json(s)
    lec_list = jt['datas']
    len1 = jt['total'] - len(lec_list)
    page_size = 10
    for i in range(math.ceil(len1/page_size)):
        params = {
            'pageIndex': i+2,
            'pageSize': page_size,
        }
        lec_list.extend(get_json(s,params)['datas'])
    for i, l in enumerate(lec_list):
        print("%2d  %s"%(i+1, l['JZMC']))
    n = int(input("select the number:")) - 1
    return lec_list[n]['WID']

def reserve(s):
    response = s.get(code_url, params=data, verify=False)
    txt = response.content.decode('utf-8', 'ignore')
    base64_str = json.loads(txt)['result']
    base64_str = base64_str[(base64_str.index("base64,") + 7):]
    image = base64.b64decode(base64_str)
    vcode = ocr.classification(image)
    params = {
        'HD_WID': wid,
        'vcode': vcode,
    }
    dataJson = {
        'paramJson': json.dumps(params)
    }
    r = s.post(app_url, data=dataJson, verify=False)
    txt = r.content.decode('utf-8', 'ignore')
    print(txt)
    res = json.loads(txt)
    return res['code'] == 200

def my_task(s):
    global wid
    for i in range(5):
        if reserve(s):
            print("successful!")
            break
        else:
            time.sleep(0.3)

if __name__ == "__main__":
    with requests.Session() as s:
        s.mount("https://", TLSAdapter())
        s.headers.update(header)

        wid = get_list(s)
        if not test:
            now = datetime.datetime.now()
            time_to_wait = (target_time - now).total_seconds()
            print(f"等待 {time_to_wait} 秒后执行任务...")
            time.sleep(time_to_wait)
        my_task(s)
