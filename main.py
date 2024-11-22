#!F:\Python\Python39\python.exe
import re
import sys
import json
from huawei import Huaweicreate, Huaweidelete
from nokia import Nokiacreate,Nokiadelete
from zte import Ztecreate, Ztedelete

if __name__ == '__main__':
    data = json.loads(re.sub('\'', '\"', sys.argv[4]))
    # ZTE NMS
    if sys.argv[1] == 'ZTE':
        # DELETE
        if sys.argv[2] == 'FAB':
            if sys.argv[3] == 'FTTH_DEL_ONU':
                # print(data)
                result = Ztedelete.zteDelete(data)
                print(result)

        # FAB CREATE
        if sys.argv[2] == 'FAB':
            if sys.argv[3] == 'FTTH_ZTE_ADDONU':
                # print(data)
                if data['ZTE_ONUTYPE'] == "1_GBPS":
                    data['ZTE_ONUTYPE'] = 'ZTE-F2866S'

                if data['ZTE_ONUTYPE'] == 'FTTH':
                    data['ZTE_ONUTYPE'] = 'ZTE-F660'

                result = Ztecreate.zteCreate('FTTH_ZTEADD_ONU.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_ZTE_BID_PROFILE':

                if data['FTTH_INTERNET_PKG'] == "1_GBPS":
                    data['FTTH_INTERNET_PKG'] = '1G'

                if data['FTTH_INTERNET_PKG'] == 'FTTH':
                    data['FTTH_INTERNET_PKG'] = '100M'

                if data['FTTH_ZTE_PROFILE'] == 'DOUBLEPLAY_VOICE_IPTV':
                    result = Ztecreate.zteCreate('FTTH_ZTEX_BIDPIPTV.xml', data)
                    print(result)

                elif data['FTTH_ZTE_PROFILE'] == 'TRIPLEPLAY_MULTIIPTV':
                    result = Ztecreate.zteCreate('FTTH_ZTEX_MIPTV.xml', data)
                    print(result)

                else:
                    result = Ztecreate.zteCreate('FTTH_ZTEX_BIDP.xml', data)
                    print(result)

        # VOICE CREATE
        if sys.argv[2] == 'VOICE':
            if sys.argv[3] == 'FTTH_ZTE_ISERPOT':
                resultvlan = Ztecreate.zteVlan('lst_vlan.xml', data, 'VOBB', '')
                print(resultvlan)
                if "VOBB" not in resultvlan:
                    data.update({'VOBB': '0'})
                data.update(resultvlan)

                result = Ztecreate.zteCreate('FTTH_VSER_PORT.xml', data)
                print(result)

        # BB CREATE
        if sys.argv[2] == 'BB':
            if sys.argv[3] == 'FTTH_ZTE_ISERPOT':
                resultvlan = Ztecreate.zteVlan('lst_vlan.xml', data, 'EVLAN', 'SVLAN')
                print(resultvlan)
                if "EVLAN" not in resultvlan:
                    data.update({'EVLAN': '0'})
                if "SVLAN" not in resultvlan:
                    data.update({'SVLAN': '0'})
                data.update(resultvlan)

                result = Ztecreate.zteCreate('FTH_ISER_POT.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_INT_USRADD':
                result = Ztecreate.zteCreate('FTTH_INT_USRADD.xml', data)
                print(result)

        # IPTV CREATE
        if sys.argv[2] == 'IPTV':
            if sys.argv[3] == 'FTTH_ZTE_ISERPOT':
                resultvlan = Ztecreate.zteVlan('lst_vlan.xml', data, 'IPTV', 'IPTV_SVLAN')
                print(resultvlan)
                if "IPTV" not in resultvlan:
                    data.update({'IPTV': ''})
                if "IPTV_SVLAN" not in resultvlan:
                    data.update({'IPTV_SVLAN': ''})
                data.update(resultvlan)

                result = Ztecreate.zteCreate('FTTH_PSER_PORT.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_ZTE_IPTVSERA':
                result = Ztecreate.zteCreate('FTTH_ZTE_IPTVSERA.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_ZTE_IPTVSERB':
                result = Ztecreate.zteCreate('FTTH_ZTE_IPTVSERB.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_ZTE_IPTVSERC':
                result = Ztecreate.zteCreate('FTTH_ZTE_IPTVSERC.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_ZTE_IPTVSERD':
                result = Ztecreate.zteCreate('FTTH_ZTE_IPTVSERD.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_ZTE_IPTV2':
                result = Ztecreate.zteCreate('FTTH_ZTE_IPTV2.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_ZTE_IPTV3':
                result = Ztecreate.zteCreate('FTTH_ZTE_IPTV3.xml', data)
                print(result)
    # HUAWEI NMS
    elif sys.argv[1] == 'HUAWEI':
        # DELETE
        if sys.argv[2] == 'FAB':
            if sys.argv[3] == 'FTTH_HW_ONUDEL':
                result = Huaweidelete.huaweiDelete(data)
                print(result)

        # FAB CREATE
        if sys.argv[2] == 'FAB':
            if sys.argv[3] == 'FTTH_HUW_ADDONT':
                result = Huaweicreate.huaweiCreate('FTTH_HUW_ADDONT.xml', data)
                print(result)

        # VOICE CREATE
        if sys.argv[2] == 'VOICE':
            if sys.argv[3] == 'FTH_CREATE_SER_PORT_VOICE':
                resultvlan = Huaweicreate.huaweiVlan('HUAWEI_LIST_VLAN.xml', data,  'VOBB', '')
                print(resultvlan)
                if "VOBB" not in resultvlan:
                    data.update({'VOBB': '0'})
                data.update(resultvlan)

                result = Huaweicreate.huaweiCreate('HX_FTH_V_SER_POT_CRE.xml', data)
                print(result)

        # BB CREATE
        if sys.argv[2] == 'BB':
            if sys.argv[3] == 'FTH_CREATE_SER_PORT_BB':
                resultvlan = Huaweicreate.huaweiVlan('HUAWEI_LIST_VLAN.xml', data,  'ADSL_VLAN', 'ADSL_SVLAN')
                print(resultvlan)
                if "ADSL_VLAN" not in resultvlan:
                    data.update({'ADSL_VLAN': '0'})
                if "ADSL_SVLAN" not in resultvlan:
                    data.update({'ADSL_SVLAN': '0'})
                data.update(resultvlan)

                result = Huaweicreate.huaweiCreate('HX_FTH_V_SER_POT_CRE.xml', data)
                print(result)

        # IPTV CREATE
        if sys.argv[2] == 'IPTV':
            if sys.argv[3] == 'FTH_CREATE_SER_PORT_BB':
                resultvlan = Huaweicreate.huaweiVlan('HUAWEI_LIST_VLAN.xml', data,  'IPTV', 'IPTV_SVLAN')
                print(resultvlan)
                if "IPTV_VLAN" not in resultvlan:
                    data.update({'IPTV_VLAN': '0'})
                if "IPTV_SVLAN" not in resultvlan:
                    data.update({'IPTV_SVLAN': '0'})
                data.update(resultvlan)

                result = Huaweicreate.huaweiCreate('HX_FTH_IPTV_SER_POT_CRE.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_HUW_JOINT_NTV':
                result = Huaweicreate.huaweiCreate('FTTH_HUW_JOINT_NTV.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_HUW_MOD_NTV':
                result = Huaweicreate.huaweiCreate('FTTH_HUW_MOD_NTV.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_IPTV_ADD_21':
                result = Huaweicreate.huaweiCreate('FTTH_IPTV_ADD_21.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_IPTV_ADD_22':
                result = Huaweicreate.huaweiCreate('FTTH_IPTV_ADD_22.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_IPTV_ADD_23':
                result = Huaweicreate.huaweiCreate('FTTH_IPTV_ADD_23.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_IPTV_ADD_31':
                result = Huaweicreate.huaweiCreate('FTTH_IPTV_ADD_31.xml', data)
                print(result)

            if sys.argv[3] == 'FTTH_IPTV_ADD_32':
                result = Huaweicreate.huaweiCreate('FTTH_IPTV_ADD_32.xml', data)
                print(result)

    # NOKIA NMS
    elif sys.argv[1] == 'NOKIA':
        # DELETE
        if sys.argv[2] == 'FAB':
            if sys.argv[3] == 'DEL_ONT_NOKIA':
                result = Nokiadelete.nokiaDelete('DEL_ONT_NOKIA.xml', data)
                print(result)

        # FAB CREATE
        if sys.argv[2] == 'FAB':
            if sys.argv[3] == 'ADD_ONT_NOKIA':
                result = Nokiacreate.nokiaCreate('ADD_ONT_NOKIA.xml', data)
                print(result)

        # BB CREATE
        if sys.argv[2] == 'BB':
            if sys.argv[3] == 'ADD_NK_INTERNET':
                result = Nokiacreate.nokiaCreate('ADD_NK_INTERNET.xml', data)
                print(result)

        # IPTV CREATE
        if sys.argv[2] == 'IPTV':
            if sys.argv[3] == 'ADD_NK_IPTV':
                result = Nokiacreate.nokiaCreate('ADD_NK_IPTV.xml', data)
                print(result)

    else:
        print('Invalid MSAN')
