#!/usr/bin/env python
# coding:utf-8
# name: cursor.py

import mysql.connector

from FXPositionDict import FXPositionDict


class QuotationDB:
    QuotationList = []

    def DBConnect(self):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                passwd='TLCB2021',
                database='FXQuotationSpider',
                charset='utf8'
            )
            return conn
        except Exception:
            raise Exception("数据库连接失败")

    @staticmethod
    def findall():
        conndb = QuotationDB().connect()
        cursor = conndb.cursor()
        print(cursor)
        cursor.execute("SELECT * FROM FXQuotation;")
        result = cursor.fetchone()

        print(result)

    # 打印所有行数据
    # print(self.conn.is_connected())
    # print(cursor.rowcount)

    # cursor.close()
    # conn.close()

    @staticmethod
    def addQuotationtoDB(QuotationList):
        Conn = QuotationDB().DBConnect()
        cursor = Conn.cursor()

        ##if cursor.execute(sql, tuple(data.values())):
        ##print('users')

        for QuotationDictCell in QuotationList:
            QuotationDictTmpD = QuotationDictCell.__dict__
            # 这里你知道table和data，其中data是一个字典，写插入数据库的代码
            #print(QuotationDictTmpD)
            table = 'FXQuotation'
            # 获取到一个以键且为逗号分隔的字符串，返回一个字符串
            keys = ','.join(QuotationDictTmpD.keys())
            values = ','.join(['%s'] * len(QuotationDictTmpD))
            sql = 'INSERT INTO {table}({keys}) VALUES({values})'.format(table=table, keys=keys, values=values)
            # 这里的第二个参数传入的要是一个元组
            cursor.execute(sql, tuple(QuotationDictTmpD.values()))
            Conn.commit()

            ##print(QuotationDict(qwe).BankName)

        cursor.close()
        Conn.close()
        return ''
