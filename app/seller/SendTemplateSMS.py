#coding=gbk

#coding=utf-8

#-*- coding: UTF-8 -*-  

from .CCPRestSDK import REST
import configparser

#���ʺ�
accountSid= '8a216da866f71d0401670ac6a0cc0711'

#���ʺ�Token
accountToken= '0a2e160709e2403aad815f834e204d32'

#Ӧ��Id
appId='8a216da866f71d0401670ac6a1150717'

#�����ַ����ʽ���£�����Ҫдhttp://
serverIP='app.cloopen.com'

#����˿� 
serverPort='8883'

#REST�汾��
softVersion='2013-12-26'

  # ����ģ�����
  # @param to �ֻ�����
  # @param datas �������� ��ʽΪ���� ���磺{'12','34'}���粻���滻���� ''
  # @param $tempId ģ��Id

def sendTemplateSMS(to,datas,tempId):

    
    #��ʼ��REST SDK
    rest = REST(serverIP,serverPort,softVersion)
    rest.setAccount(accountSid,accountToken)
    rest.setAppId(appId)
    
    result = rest.sendTemplateSMS(to,datas,tempId)
    return result["statusCode"]
    
   
# sendTemplateSMS(18826138192,['123456','5'],1)