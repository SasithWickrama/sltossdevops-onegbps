#!F:\Python\Python39\python.exe
import re
import traceback
import requests
from log import getLogger
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth


logger =getLogger('huawei', 'F:\\xampp\\htdocs\\IMS\\dbFunction\\ONEGBPS\\logs\\huawei')
endpoint = "http://10.68.136.52:8080/soap/services/ApcRemotePort/9.6";

proxies = {
    "http": None,
    "https": None,
}


class Nokiacreate:
    def nokiaCreate(self, indata):

        try:
            xmlfile = open('F:\\xampp\\htdocs\\IMS\\dbFunction\\NMSCon\\files\\nokia\\' + self, 'r')
            data = xmlfile.read()

            for key in indata:
                value = indata[key]

                data = data.replace(key, value)
                # print(key, value)

            # print(data)
            response = requests.request("POST", endpoint,
                                        data=data, proxies=proxies, auth=HTTPBasicAuth('nbiuser', 'nbiuser'))

            logger.info("Start : =========================================================================")
            logger.info("Input Data : "+str(indata))
            logger.info("command xml : "+str(self))
            logger.info(response.request.body)
            logger.info("Response : =================================")
            logger.info(response.text)


            ResultCode=re.findall("<ResultIndicator>(.*?)</ResultIndicator>", str(response.content))

            if len(ResultCode) > 0:
                logger.info('0#' + str(ResultCode[0]))
                logger.info("End   : =========================================================================")
                return '0#' + str(ResultCode[0])
            else:
                ResultCode = re.findall("<message>(.*?)</message>", str(response.content))
                logger.info('1#' + str(ResultCode[0]))
                logger.info("End   : =========================================================================")
                return '1#' + str(ResultCode[0])

        except Exception as e:
            print("Exception : %s" % traceback.format_exc())
            logger.error(e)
            logger.info("End   : =========================================================================")


class Nokiadelete:
    def nokiaDelete(self, indata):
        # FAB DELETE / VOICE DELETE
        try:
            xmlfile = open('F:\\xampp\\htdocs\\IMS\\dbFunction\\NMSCon\\files\\nokia\\' + self, 'r')
            data = xmlfile.read()

            for key in indata:
                value = indata[key]

                data = data.replace(key, value)
                # print(key, value)

            print(data)
            response = requests.request("POST", endpoint,
                                        data=data, proxies=proxies, auth=HTTPBasicAuth('nbiuser', 'nbiuser'))

            logger.info("Start : =========================================================================")
            logger.info("Input Data : "+str(indata))
            logger.info("command xml : "+str(self))
            logger.info(response.request.body)
            logger.info("Response : =================================")
            logger.info(response.text)


            ResultCode=re.findall("<ResultIndicator>(.*?)</ResultIndicator>", str(response.content))
            if len(ResultCode) > 0:
                logger.info('0#' + str(ResultCode[0]))
                logger.info("End   : =========================================================================")
                return '0#' + str(ResultCode[0])
            else:
                ResultCode = re.findall("<message>(.*?)</message>", str(response.content))
                logger.info('1#' + str(ResultCode[0]))
                logger.info("End   : =========================================================================")
                return '1#' + str(ResultCode[0])

        except Exception as e:
            print("Exception : %s" % traceback.format_exc())
            logger.error(e)
            logger.info("End   : =========================================================================")
