#!F:\Python\Python39\python.exe
import re
import traceback
import requests
from log import getLogger
import xml.etree.ElementTree as ET


logger =getLogger('huawei', 'F:\\xampp\\htdocs\\IMS\\dbFunction\\ONEGBPS\\logs\\huawei')
endpoint = "http://huaweincefanoss.intranet.slt.com.lk:30102/wsdl";

proxies = {
    "http": None,
    "https": None,
}


class Huaweicreate:
    def huaweiVlan(self, indata, inval, inval2):
        try:
            xmlfile = open('F:\\xampp\\htdocs\\IMS\\dbFunction\\NMSCon\\files\\huawei\\' + self, 'r')
            data = xmlfile.read()

            for key in indata:
                value = indata[key]

                data = data.replace(key, value)
                # print(key, value)

            # print(data)
            logger.info(data)
            response = requests.request("POST", endpoint,
                                        data=data, proxies=proxies)

            logger.info("Start : =========================================================================")
            logger.info("Input Data : "+str(indata))
            logger.info("command xml : "+str(self))
            logger.info(response.request.body)
            logger.info("Response : =================================")
            logger.info(response.text)

            data = {}
            root = ET.fromstring(response.content)

            ResultCode=re.findall("<os:errCode>(.*?)</os:errCode>", str(response.content))
            ResultDesc=re.findall("<os:errDesc>(.*?)</os:errDesc>", str(response.content))

            userlable = re.findall("<USERLABEL>(.*?)</USERLABEL>", str(response.content))
            print(userlable.index('Entree'))
            vlan = re.findall("<VLANID>(.*?)</VLANID>", str(response.content))
            print(vlan[userlable.index('Entree')])

            if inval == 'VOBB':
                data[inval] = vlan[userlable.index(inval)]
            if inval == 'IPTV':
                data['IPTV_VLAN'] = vlan[userlable.index(inval)]
            if inval == 'ADSL_VLAN':
                data[inval] = vlan[userlable.index('Entree')]
            if inval2 == 'ADSL_SVLAN':
                data[inval2] = vlan[userlable.index('SVLAN')]
            if inval2 == 'IPTV_SVLAN':
                data[inval2] = vlan[userlable.index(inval2)]

            # print(data)
            if (ResultCode[0] == '0'):
                logger.info(data)
                logger.info("End   : =========================================================================")
                return data
            else:
                logger.info(str(ResultCode[0]) + '#' + str(ResultDesc[0]))
                logger.info("End   : =========================================================================")
                return ResultCode[0] + '#' + ResultDesc[0]
            # print(data)


        except Exception as e:
            print("Exception : %s" % traceback.format_exc())
            logger.error(e)
            logger.info("End   : =========================================================================")

    def huaweiCreate(self, indata):

        try:
            xmlfile = open('F:\\xampp\\htdocs\\IMS\\dbFunction\\NMSCon\\files\\huawei\\' + self, 'r')
            data = xmlfile.read()

            for key in indata:
                value = indata[key]

                data = data.replace(key, value)
                # print(key, value)

            # print(data)
            response = requests.request("POST", endpoint,
                                        data=data, proxies=proxies)

            logger.info("Start : =========================================================================")
            logger.info("Input Data : "+str(indata))
            logger.info("command xml : "+str(self))
            logger.info(response.request.body)
            logger.info("Response : =================================")
            logger.info(response.text)


            ResultCode=re.findall("<os:errCode>(.*?)</os:errCode>", str(response.content))
            ResultDesc=re.findall("<os:errDesc>(.*?)</os:errDesc>", str(response.content))

            # print(ResultCode)
            # print(ResultDesc)
            logger.info(str(ResultCode[0]) + '#' + str(ResultDesc[0]))
            logger.info("End   : =========================================================================")
            return ResultCode[0] + '#' + ResultDesc[0]

        except Exception as e:
            print("Exception : %s" % traceback.format_exc())
            logger.error(e)
            logger.info("End   : =========================================================================")


class Huaweidelete:
    def huaweiDelete(self):
        # FAB DELETE / VOICE DELETE
        try:
            xmlfile = open('F:\\xampp\\htdocs\\IMS\\dbFunction\\NMSCon\\files\\huawei\\FTTH_HW_ONUDEL.xml', 'r')
            data = xmlfile.read()

            for key in self:
                value = self[key]

                data = data.replace(key, value)
                # print(key, value)

            print(data)
            response = requests.request("POST", endpoint,
                                        data=data, proxies=proxies)

            logger.info("Start : =========================================================================")
            logger.info("Input Data : "+str(self))
            logger.info("command xml : FTTH_HW_ONUDEL.xml")
            logger.info(response.request.body)
            logger.info("Response : =================================")
            logger.info(response.text)


            ResultCode=re.findall("<os:errCode>(.*?)</os:errCode>", str(response.content))
            ResultDesc=re.findall("<os:errDesc>(.*?)</os:errDesc>", str(response.content))

            # print(ResultDesc)
            logger.info(str(ResultCode[0]) + '#' + str(ResultDesc[0]))
            logger.info("End   : =========================================================================")
            return ResultCode[0] + '#' + ResultDesc[0]

        except Exception as e:
            print("Exception : %s" % traceback.format_exc())
            logger.error(e)
            logger.info("End   : =========================================================================")



