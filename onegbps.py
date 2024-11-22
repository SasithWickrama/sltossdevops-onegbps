import multiprocessing
import random
import sys
import time
import db
import subprocess

import zte
from huawei import Huaweicreate, Huaweidelete
from nokia import Nokiacreate, Nokiadelete
from zte import Ztecreate, Ztedelete
from log import getLogger


def specific_string(length):
    sample_string = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890'  # define the specific string
    # define the condition for random string
    return ''.join((random.choice(sample_string)) for x in range(length))


def multiprocessing_func(x, pe):
    #logger = getLogger(pe + '_prov', 'logs/' + pe)
    logger = getLogger(pe + '_prov', 'F:\\xampp\\htdocs\\IMS\\dbFunction\\ONEGBPS\\logs\\' + pe)

    refid = specific_string(10)

    try:
        conn = db.DbConnection.dbconnOssRpt(self="")
        c = conn.cursor()
        sql = "select MSAN_TYPE,DNAME,ONT_SN,ZTE_PORT,HUAWEI_PORT,NOKIA_PORT,V_PORT,REGID,BB_CIRCUIT,IPTV_COUNT,SPEED," \
              "ZTE_PROFILE,REC_ID from ONEG_OLDCCT_DETAILS where  PE_NO = :PE_NO and CCT_STATUS=:CCT_STATUS"\
              " and ONT_SN is not null and REGID is not null   " \
              "AND MOD(DBMS_ROWID.ROWID_ROW_NUMBER(ONEG_OLDCCT_DETAILS.ROWID), 10) = " + str(x)
        c.execute(sql, [pe, '0'])

        for row in c:

            MSAN_TYPE, DNAME, ONT_SN, ZTE_PORT, HUAWEI_PORT, NOKIA_PORT, V_PORT, REGID, BB_CIRCUIT, IPTV_COUNT, SPEED, ZTE_PROFILE, REC_ID = row
            print(MSAN_TYPE, ONT_SN, ZTE_PORT, IPTV_COUNT)

            sql = "select distinct ZTE_PORT,HUAWEI_PORT,NOKIA_PORT,V_PORT,REGID,DNAME,SPEED,ZTE_PROFILE,VOICE_NO" \
                  ",VOICE_NO2,VTYPE1,VTYPE2 from ONEG_NEWCCT_DETAILS " \
                  "where PE_NO= :PE_NO  and ONT_SN= :ONT_SN and REGID= :REGID and CCT_STATUS=:CCT_STATUS"
            with conn.cursor() as cursor:
                cursor.execute(sql, [pe, ONT_SN, REGID,'0'])
                credata = cursor.fetchone()


            ref = refid + '_' + REGID

            datadel = {}
            data = {}

            datadel['ADSL_ZTE_DNAME'] = DNAME
            datadel['FTTH_ONT_SN'] = ONT_SN
            datadel['FTTH_ZTE_PID'] = ZTE_PORT
            datadel['REF_ID'] = str(ref)
            datadel['PENO'] = str(pe)

            data['ADSL_ZTE_DNAME'] = str(credata[5])
            data['FTTH_ZTE_PID'] = credata[0]
            data['FTTH_ONT_SN'] = ONT_SN
            data['FTTH_HUW_VP'] = str(credata[3])
            data['ZTE_NMS_REGID'] = '94'+str(credata[4])[1:10]
            data['FTTH_ZTE_PROFILE'] = str(credata[7])
            data['REF_ID'] = str(ref)
            data['PENO'] = str(pe)
            data['ADSL_ZTE_USERNAME'] = BB_CIRCUIT


            if MSAN_TYPE == 'ZTE':
                #if credata[6] == "1_GBPS":
                #data['ZTE_ONUTYPE'] = 'ZTE-F2866S'
                #data['FTTH_INTERNET_PKG'] = '1G'

                # if credata[6] == 'FTTH':
                data['ZTE_ONUTYPE'] = 'ZTE-F660'
                data['FTTH_INTERNET_PKG'] = '100M'

                logger.info(ref+"  " + "Start : =========================================================================")
                logger.info(ref+"  " + str(data))

                #DELETE
                result = Ztedelete.zteDelete(datadel)
                if result.split('#')[0] == '0': # IF CON 1
                    #CREATE
                    try:
                        sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=1, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                        with conn.cursor() as cursor:
                            cursor.execute(sql, [result.split('#')[1], REGID, pe])
                            conn.commit()

                        sql2 = "update ONEG_OLDCCT_DETAILS set CCT_STATUS=1, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                        with conn.cursor() as cursor2:
                            cursor2.execute(sql2, [result.split('#')[1], REGID, pe])
                            conn.commit()
                    except conn.Error as error:
                        #print('DB Error:' + str(error))
                        logger.error(ref+"  DB Error: " + str(error))


                    #GET VLAN
                    resultvlan = Ztecreate.zteVlan('lst_vlan.xml', data, 'VOBB', '')
                    logger.info(ref+"  " + "command xml : lst_vlan.xml")
                    logger.info(ref+"  " + str(resultvlan))
                    data.update(resultvlan)

                    if BB_CIRCUIT != '':
                        resultvlanbb = Ztecreate.zteVlan('lst_vlan.xml', data, 'Entree', 'SVLAN')
                        logger.info(ref+"  " + "command xml : lst_vlan.xml")
                        logger.info(ref+"  " + str(resultvlanbb))
                        data.update(resultvlanbb)

                    if IPTV_COUNT != '0':
                        resultvlanpeo = Ztecreate.zteVlan('lst_vlan.xml', data, 'IPTV_SVLAN', 'IPTV')
                        logger.info(ref+"  " + "command xml : lst_vlan.xml")
                        logger.info(ref+"  " + str(resultvlanpeo))
                        data.update(resultvlanpeo)

                    # FAB
                    resultfab = Ztecreate.zteCreate('FTTH_ZTEADD_ONU.xml', data)
                    logger.info(ref+"  " + "command xml : FTTH_ZTEADD_ONU.xml")
                    logger.info(ref+"  " + resultfab)

                    if resultfab.split('#')[0] == '0':#IF FAB RESULT
                        try:
                            sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=2, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                            with conn.cursor() as cursor:
                                cursor.execute(sql, [resultfab.split('#')[1], REGID, pe])
                                conn.commit()
                        except conn.Error as error:
                            print('DB Error:' + str(error))

                        if credata[7] == 'DOUBLEPLAY_VOICE_IPTV':
                            command = 'FTTH_ZTEX_BIDPIPTV.xml'
                        elif credata[7] == 'TRIPLEPLAY_MULTIIPTV':
                            command = 'FTTH_ZTEX_MIPTV.xml'
                        else:
                            command = 'FTTH_ZTEX_BIDP.xml'

                        resultprof = Ztecreate.zteCreate(command, data)
                        logger.info(ref+"  " + "command xml : "+ command)
                        logger.info(ref+"  " + resultprof)

                        if resultprof.split('#')[0] == '0':#IF PROFILE RESULT
                            try:
                                sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=3, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                with conn.cursor() as cursor:
                                    cursor.execute(sql, [resultprof.split('#')[1], REGID, pe])
                                    conn.commit()
                            except conn.Error as error:
                                #print('DB Error:' + str(error))
                                logger.error(ref+"  DB Error: " + str(error))

                            # VOICE
                            resultv = Ztecreate.zteCreate('FTTH_VSER_PORT.xml', data)
                            logger.info(ref+"  " + "command xml : FTTH_VSER_PORT.xml")
                            logger.info(ref+"  " + resultv)

                            if resultv.split('#')[0] == '0':#IF VOICE RESULT

                                try:
                                    sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=4, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                    with conn.cursor() as cursor:
                                        cursor.execute(sql, [resultv.split('#')[1], REGID, pe])
                                        conn.commit()
                                except conn.Error as error:
                                    #print('DB Error:' + str(error))
                                    logger.error(ref+"  DB Error: " + str(error))

                                #BB
                                if BB_CIRCUIT != '':
                                    resultbb = Ztecreate.zteCreate('FTH_ISER_POT.xml', data)
                                    logger.info(ref+"  " + "command xml : FTH_ISER_POT.xml")
                                    logger.info(ref+"  " + resultbb)

                                    if resultbb.split('#')[0] == '0':#IF BB RESULT

                                        try:
                                            sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=5, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                            with conn.cursor() as cursor:
                                                cursor.execute(sql, [resultbb.split('#')[1], REGID, pe])
                                                conn.commit()
                                        except conn.Error as error:
                                            #print('DB Error:' + str(error))
                                            logger.error(ref+"  DB Error: " + str(error))

                                        resultusr = Ztecreate.zteCreate('FTTH_INT_USRADD.xml', data)
                                        logger.info(ref+"  " + "command xml : FTTH_INT_USRADD.xml")
                                        logger.info(ref+"  " + resultusr)

                                        if resultusr.split('#')[0] == '0':#IF USR ADD RESULT

                                            try:
                                                sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=6, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                with conn.cursor() as cursor:
                                                    cursor.execute(sql, [result.split('#')[1], REGID, pe])
                                                    conn.commit()
                                            except conn.Error as error:
                                                #print('DB Error:' + str(error))
                                                logger.error(ref+"  DB Error: " + str(error))

                                        else:#IF USR ADD RESULT
                                            try:
                                                sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                with conn.cursor() as cursor:
                                                    cursor.execute(sql, [resultusr.split('#')[1], REGID, pe])
                                                    conn.commit()
                                            except conn.Error as error:
                                                #print('DB Error:' + str(error))
                                                logger.error(ref+"  DB Error: " + str(error))


                                    else:#IF BB RESULT
                                        try:
                                            sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                            with conn.cursor() as cursor:
                                                cursor.execute(sql, [resultbb.split('#')[1], REGID, pe])
                                                conn.commit()
                                        except conn.Error as error:
                                            #print('DB Error:' + str(error))
                                            logger.error(ref+"  DB Error: " + str(error))
                                #IPTV
                                if  IPTV_COUNT != '':
                                    resultiptv = Ztecreate.zteCreate('FTTH_PSER_PORT.xml', data)
                                    logger.info(ref+"  " + "command xml : FTTH_PSER_PORT.xml")
                                    logger.info(ref+"  " + resultiptv)

                                    if resultiptv.split('#')[0] == '0':#IF IPTV 1 RESULT
                                        try:
                                            sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=7, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                            with conn.cursor() as cursor:
                                                cursor.execute(sql, [resultiptv.split('#')[1], REGID, pe])
                                                conn.commit()
                                        except conn.Error as error:
                                            print('DB Error:' + str(error))

                                        resultA = Ztecreate.zteCreate('FTTH_ZTE_IPTVSERA.xml', data)
                                        logger.info(ref+"  " + "command xml : FTTH_ZTE_IPTVSERA.xml")
                                        logger.info(ref+"  " + resultA)

                                        if resultA.split('#')[0] == '0':#IF IPTV A RESULT
                                            try:
                                                sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=8, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                with conn.cursor() as cursor:
                                                    cursor.execute(sql, [resultA.split('#')[1], REGID, pe])
                                                    conn.commit()
                                            except conn.Error as error:
                                                #print('DB Error:' + str(error))
                                                logger.error(ref+"  DB Error: " + str(error))


                                            resultB = Ztecreate.zteCreate('FTTH_ZTE_IPTVSERB.xml', data)
                                            logger.info(ref+"  " + "command xml : FTTH_ZTE_IPTVSERB.xml")
                                            logger.info(ref+"  " + resultB)

                                            if resultB.split('#')[0] == '0':#IF IPTV B RESULT
                                                try:
                                                    sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=9, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                    with conn.cursor() as cursor:
                                                        cursor.execute(sql, [resultB.split('#')[1], REGID, pe])
                                                        conn.commit()
                                                except conn.Error as error:
                                                    #print('DB Error:' + str(error))
                                                    logger.error(ref+"  DB Error: " + str(error))

                                                resultC = Ztecreate.zteCreate('FTTH_ZTE_IPTVSERC.xml', data)
                                                logger.info(ref+"  " + "command xml : FTTH_ZTE_IPTVSERC.xml")
                                                logger.info(ref+"  " + resultC)

                                                if resultC.split('#')[0] == '0':#IF IPTV C RESULT
                                                    try:
                                                        sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=10, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                        with conn.cursor() as cursor:
                                                            cursor.execute(sql,
                                                                           [resultC.split('#')[1], REGID, pe])
                                                            conn.commit()
                                                    except conn.Error as error:
                                                        #print('DB Error:' + str(error))
                                                        logger.error(ref+"  DB Error: " + str(error))

                                                    resultD = Ztecreate.zteCreate('FTTH_ZTE_IPTVSERD.xml', data)
                                                    logger.info(ref+"  " + "command xml : FTTH_ZTE_IPTVSERD.xml")
                                                    logger.info(ref+"  " + resultD)

                                                    if resultD.split('#')[0] == '0':#IF IPTV D RESULT
                                                        try:
                                                            sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=11, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                            with conn.cursor() as cursor:
                                                                cursor.execute(sql,
                                                                               [resultD.split('#')[1], REGID,
                                                                                pe])
                                                                conn.commit()
                                                        except conn.Error as error:
                                                            #print('DB Error:' + str(error))
                                                            logger.error(ref+"  DB Error: " + str(error))

                                                        if IPTV_COUNT == 2:
                                                            result2 = Ztecreate.zteCreate('FTTH_ZTE_IPTV2.xml',
                                                                                          data)
                                                            logger.info(ref+"  " + "command xml : FTTH_ZTE_IPTV2.xml")
                                                            logger.info(ref+"  " + result2)

                                                            if result2.split('#')[0] == '0':#IF IPTV 2 RESULT
                                                                try:
                                                                    sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=12, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                                    with conn.cursor() as cursor:
                                                                        cursor.execute(sql,
                                                                                       [result.split('#')[1],
                                                                                        REGID, pe])
                                                                        conn.commit()
                                                                except conn.Error as error:
                                                                    #print('DB Error:' + str(error))
                                                                    logger.error(ref+"  DB Error: " + str(error))

                                                            else:#IF IPTV 2 RESULT
                                                                try:
                                                                    sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                                    with conn.cursor() as cursor:
                                                                        cursor.execute(sql,
                                                                                       [result2.split('#')[1],
                                                                                        REGID, pe])
                                                                        conn.commit()
                                                                except conn.Error as error:
                                                                    #print('DB Error:' + str(error))
                                                                    logger.error(ref+"  DB Error: " + str(error))

                                                        if IPTV_COUNT == 3:
                                                            result2 = Ztecreate.zteCreate('FTTH_ZTE_IPTV2.xml',
                                                                                          data)
                                                            logger.info(ref+"  " + "command xml : FTTH_ZTE_IPTV2.xml")
                                                            logger.info(ref+"  " + result2)

                                                            if result2.split('#')[0] == '0':#IF IPTV 2 RESULT
                                                                try:
                                                                    sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=12, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                                    with conn.cursor() as cursor:
                                                                        cursor.execute(sql,
                                                                                       [result2.split('#')[1],
                                                                                        REGID, pe])
                                                                        conn.commit()
                                                                except conn.Error as error:
                                                                    print('DB Error:' + str(error))

                                                            else:#IF IPTV 2 RESULT
                                                                try:
                                                                    sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                                    with conn.cursor() as cursor:
                                                                        cursor.execute(sql,
                                                                                       [result2.split('#')[1],
                                                                                        REGID, pe])
                                                                        conn.commit()
                                                                except conn.Error as error:
                                                                    print('DB Error:' + str(error))

                                                            result3 = Ztecreate.zteCreate('FTTH_ZTE_IPTV3.xml',
                                                                                          data)
                                                            logger.info(ref+"  " + "command xml : FTTH_ZTE_IPTV3.xml")
                                                            logger.info(ref+"  " + result3)

                                                            if result3.split('#')[0] == '0':#IF IPTV 3 RESULT
                                                                try:
                                                                    sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=13, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                                    with conn.cursor() as cursor:
                                                                        cursor.execute(sql,
                                                                                       [result3.split('#')[1],
                                                                                        REGID, pe])
                                                                        conn.commit()
                                                                except conn.Error as error:
                                                                    print('DB Error:' + str(error))

                                                            else:#IF IPTV 3 RESULT
                                                                try:
                                                                    sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                                    with conn.cursor() as cursor:
                                                                        cursor.execute(sql,
                                                                                       [result3.split('#')[1],
                                                                                        REGID, pe])
                                                                        conn.commit()
                                                                except conn.Error as error:
                                                                    print('DB Error:' + str(error))



                                                    else:#IF IPTV D RESULT
                                                        try:
                                                            sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                            with conn.cursor() as cursor:
                                                                cursor.execute(sql, [resultD.split('#')[1], REGID, pe])
                                                                conn.commit()
                                                        except conn.Error as error:
                                                            #print('DB Error:' + str(error)
                                                            logger.error(ref+"  DB Error: " + str(error))


                                                else:#IF IPTV C RESULT
                                                    try:
                                                        sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                        with conn.cursor() as cursor:
                                                            cursor.execute(sql, [resultC.split('#')[1], REGID, pe])
                                                            conn.commit()
                                                    except conn.Error as error:
                                                        #print('DB Error:' + str(error)
                                                        logger.error(ref+"  DB Error: " + str(error))


                                            else:#IF IPTV B RESULT
                                                try:
                                                    sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                    with conn.cursor() as cursor:
                                                        cursor.execute(sql, [resultB.split('#')[1], REGID, pe])
                                                        conn.commit()
                                                except conn.Error as error:
                                                    #print('DB Error:' + str(error)
                                                    logger.error(ref+"  DB Error: " + str(error))



                                        else:#IF IPTV A RESULT
                                            try:
                                                sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                with conn.cursor() as cursor:
                                                    cursor.execute(sql, [resultA.split('#')[1], REGID, pe])
                                                    conn.commit()
                                            except conn.Error as error:
                                                #print('DB Error:' + str(error)
                                                logger.error(ref+"  DB Error: " + str(error))


                                    else:#IF IPTV 1 RESULT
                                        try:
                                            sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                            with conn.cursor() as cursor:
                                                cursor.execute(sql, [resultiptv.split('#')[1], REGID, pe])
                                                conn.commit()
                                        except conn.Error as error:
                                            #print('DB Error:' + str(error)
                                            logger.error(ref+"  DB Error: " + str(error))


                                #IMS UDR DELETE

                                imsresult = subprocess.run(['java', '-jar', 'F:\\xampp\\htdocs\\IMS\\dbFunction\\SLTIMSgui.jar', 'DELATS', '2','tpno#'+str(credata[4])[1:10],'source#'+str(credata[4])[1:2]], capture_output=True)
                                logger.info(ref+"  " + "command xml : IMS DELATS ")
                                logger.info(ref+"  " + imsresult.stdout.decode())

                                if imsresult.stdout.decode().split('#')[0] == '0':#IF IMS DELETE
                                    try:
                                        sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=14, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                        with conn.cursor() as cursor:
                                            cursor.execute(sql,
                                                           [imsresult.stdout.decode().split('#')[1],
                                                            REGID, pe])
                                            conn.commit()
                                    except conn.Error as error:
                                        print('DB Error:' + str(error))

                                    udrhssresult = subprocess.run(['java', '-jar', 'F:\\xampp\\htdocs\\IMS\\dbFunction\\SLTUdrGui.jar', 'UDR_DEL_HSS', '1','tpno#'+str(credata[4])[1:10]], capture_output=True)
                                    logger.info(ref+"  " + "command xml : UDR DELHSS ")
                                    logger.info(ref+"  " + udrhssresult.stdout.decode())

                                    if udrhssresult.stdout.decode().split('#')[0] == '0':#IF UDR HSS DELETE
                                        try:
                                            sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=15, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                            with conn.cursor() as cursor:
                                                cursor.execute(sql,
                                                               [udrhssresult.stdout.decode().split('#')[1],
                                                                REGID, pe])
                                                conn.commit()
                                        except conn.Error as error:
                                            print('DB Error:' + str(error))


                                        udrensresult = subprocess.run(['java', '-jar', 'F:\\xampp\\htdocs\\IMS\\dbFunction\\SLTUdrGui.jar', 'DELENS', '1','tpno#'+str(credata[4])[1:10]], capture_output=True)
                                        logger.info(ref+"  " + "command xml : UDR DELENS ")
                                        logger.info(ref+"  " + udrensresult.stdout.decode())

                                        if udrensresult.stdout.decode().split('#')[0] == '0':#IF UDR ENS DELETE
                                            try:
                                                sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=16, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                with conn.cursor() as cursor:
                                                    cursor.execute(sql,
                                                                   [udrensresult.stdout.decode().split('#')[1],
                                                                    REGID, pe])
                                                    conn.commit()
                                            except conn.Error as error:
                                                print('DB Error:' + str(error))


                                            #IMS UDR CREATE
                                            resultudrhss = subprocess.run(['java', '-jar', 'F:\\xampp\\htdocs\\IMS\\dbFunction\\SLTUdrGui.jar', 'UDR_ADDFTTH_HSS', '6','tpno#'+str(credata[4])[1:10],'MSAN_TYPE#ZTE','ONT_PORT#'+str(credata[10]),'FTTH_ZTE_PID#'+str(credata[0]),'FTTH_HUW_VP#'+str(credata[3]),'ADSL_ZTE_DNAME#'+str(credata[5])], capture_output=True)
                                            logger.info(ref+"  " + "command xml : UDR ADDHSS ")
                                            logger.info(ref+"  " + resultudrhss.stdout.decode())

                                            if resultudrhss.stdout.decode().split('#')[0] == '0':#IF UDR HSS CREATE
                                                try:
                                                    sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=17, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                    with conn.cursor() as cursor:
                                                        cursor.execute(sql,
                                                                       [resultudrhss.stdout.decode().split('#')[1],
                                                                        REGID, pe])
                                                        conn.commit()
                                                except conn.Error as error:
                                                    print('DB Error:' + str(error))

                                                resultudrens = subprocess.run(['java', '-jar', 'F:\\xampp\\htdocs\\IMS\\dbFunction\\SLTUdrGui.jar', 'ADDENS', '1','tpno#'+str(credata[4])[1:10]], capture_output=True)
                                                logger.info(ref+"  " + "command xml : UDR ADDENS ")
                                                logger.info(ref+"  " + resultudrens.stdout.decode())

                                                if resultudrens.stdout.decode().split('#')[0] == '0':#IF UDR ENS CREATE
                                                    try:
                                                        sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=18, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                        with conn.cursor() as cursor:
                                                            cursor.execute(sql,
                                                                           [resultudrens.stdout.decode().split('#')[1],
                                                                            REGID, pe])
                                                            conn.commit()
                                                    except conn.Error as error:
                                                        print('DB Error:' + str(error))

                                                    resultimsats = subprocess.run(['java', '-jar', 'F:\\xampp\\htdocs\\IMS\\dbFunction\\SLTIMSgui.jar', 'ADDATS', '2','tpno#'+str(credata[4])[1:10],'source#'+str(credata[4])[1:2]], capture_output=True)
                                                    logger.info(ref+"  " + "command xml : IMS ADDATS ")
                                                    logger.info(ref+"  " + resultimsats.stdout.decode())

                                                    if resultimsats.stdout.decode().split('#')[0] == '0':#IF IMS CREATE
                                                        try:
                                                            sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=19, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                            with conn.cursor() as cursor:
                                                                cursor.execute(sql,
                                                                               [resultimsats.stdout.decode().split('#')[1],
                                                                                REGID, pe])
                                                                conn.commit()
                                                        except conn.Error as error:
                                                            print('DB Error:' + str(error))
                                                    else:#IF IMS CREATE
                                                        try:
                                                            sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                            with conn.cursor() as cursor:
                                                                cursor.execute(sql, [resultimsats.stdout.decode().split('#')[1], REGID, pe])
                                                                conn.commit()
                                                        except conn.Error as error:
                                                            #print('DB Error:' + str(error))
                                                            logger.error(ref+"  DB Error: " + str(error))

                                                else:#IF UDR ENS CREATE
                                                    try:
                                                        sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                        with conn.cursor() as cursor:
                                                            cursor.execute(sql, [resultudrens.stdout.decode().split('#')[1], REGID, pe])
                                                            conn.commit()
                                                    except conn.Error as error:
                                                        #print('DB Error:' + str(error))
                                                        logger.error(ref+"  DB Error: " + str(error))

                                            else:#IF UDR HSS CREATE
                                                try:
                                                    sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                    with conn.cursor() as cursor:
                                                        cursor.execute(sql, [resultudrhss.stdout.decode().split('#')[1], REGID, pe])
                                                        conn.commit()
                                                except conn.Error as error:
                                                    #print('DB Error:' + str(error))
                                                    logger.error(ref+"  DB Error: " + str(error))

                                        else:#IF UDR ENS DELETE
                                            try:
                                                sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                                with conn.cursor() as cursor:
                                                    cursor.execute(sql, [udrensresult.stdout.decode().split('#')[1], REGID, pe])
                                                    conn.commit()
                                            except conn.Error as error:
                                                #print('DB Error:' + str(error))
                                                logger.error(ref+"  DB Error: " + str(error))

                                    else:#IF UDR HSS DELETE
                                        try:
                                            sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                            with conn.cursor() as cursor:
                                                cursor.execute(sql, [udrhssresult.stdout.decode().split('#')[1], REGID, pe])
                                                conn.commit()
                                        except conn.Error as error:
                                            #print('DB Error:' + str(error))
                                            logger.error(ref+"  DB Error: " + str(error))

                                else:#IF IMS DELETE
                                    try:
                                        sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                        with conn.cursor() as cursor:
                                            cursor.execute(sql, [imsresult.stdout.decode().split('#')[1], REGID, pe])
                                            conn.commit()
                                    except conn.Error as error:
                                        #print('DB Error:' + str(error))
                                        logger.error(ref+"  DB Error: " + str(error))

                            else:#IF VOICE RESULT
                                    try:
                                        sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                        with conn.cursor() as cursor:
                                            cursor.execute(sql, [resultv.split('#')[1], REGID, pe])
                                            conn.commit()
                                    except conn.Error as error:
                                        #print('DB Error:' + str(error))
                                        logger.error(ref+"  DB Error: " + str(error))


                        else:#IF PROFILE RESULT
                            try:
                                sql = "update ONEG_NEWCCT_DETAILS set  CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                                with conn.cursor() as cursor:
                                    cursor.execute(sql, [resultprof.split('#')[1], REGID, pe])
                                    conn.commit()
                            except conn.Error as error:
                                #print('DB Error:' + str(error))
                                logger.error(ref+"  DB Error: " + str(error))


                    else:#IF FAB RESULT
                        try:
                            sql = "update ONEG_NEWCCT_DETAILS set CCT_STATUS=1, CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                            with conn.cursor() as cursor:
                                cursor.execute(sql, [resultfab.split('#')[1], REGID, pe])
                                conn.commit()
                        except conn.Error as error:
                            #print('DB Error:' + str(error))
                            logger.error(ref+"  DB Error: " + str(error))

                else:# IF CON 1
                    logger.info(ref+"  " + str(result.split('#')[1]))
                    try:
                        sql = "update ONEG_OLDCCT_DETAILS set CCT_MESSAGE= :CCT_MESSAGE where  REGID= :REGID and PE_NO= :PE_NO"
                        with conn.cursor() as cursor:
                            cursor.execute(sql, [result.split('#')[1], REGID, pe])
                            conn.commit()
                    except conn.Error as error:
                        #print('DB Error:' + str(error))
                        logger.error(ref+"  DB Error: " + str(error))

    except conn.Error as error:
        print('Error occurred:' + str(error))
        logger.error(" " + str(error))

    try:
        conn = db.DbConnection.dbconnOssRpt(self="")
        sql = "update ONEG_PE_DETAILS set PE_STATUS= :PE_STATUS where   PE_NO= :PE_NO"
        with conn.cursor() as cursor:
            cursor.execute(sql, ['8', pe])
            conn.commit()
    except conn.Error as error:
        #print('DB Error:' + str(error))
        logger.error(ref+"  DB Error: " + str(error))

if __name__ == '__main__':
    pe = sys.argv[1]
    # PE2022031995404
    starttime = time.time()
    processes = []
    for i in range(0, 10):
        p = multiprocessing.Process(target=multiprocessing_func, args=(i, pe))
        processes.append(p)
        p.start()
    # multiprocessing_func(i)
    for process in processes:
        process.join()
