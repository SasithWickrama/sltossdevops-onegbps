import cx_Oracle



class DbConnection:

    def dbconnOssRpt(self):
        try:
            hostname = '172.25.1.172'
            port = '1521'
            service = 'clty'
            user = 'OSSRPT'
            password = 'ossrpt123'

            #cx_Oracle.init_oracle_client(lib_dir=r"D:\oracle\instantclient_19_6")
            dsn_tns = cx_Oracle.makedsn(hostname, port, service_name=service)
            conn = cx_Oracle.connect(user=user, password=password, dsn=dsn_tns)
            return conn
        except Exception as e:
            print("Exception : %s" % e)
            return e
