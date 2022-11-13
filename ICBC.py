# -*- coding:utf-8 -*- 
# 
# 
# 

import datetime
import json
import os
import re
import time
import time as tm
from concurrent.futures import ThreadPoolExecutor

import requests
from scrapy.selector import Selector
from tqdm import tqdm

from FXPositionDict import FXPositionDict


class ICBC:
    CurrencyNameList = ['英镑', '欧元', '美元', '日元', '港币', '加拿大元', '澳大利亚元']
    CurrencyCodeList = ['GBP', 'EUR', 'USD', 'JPY', 'HKD', 'CAD', 'AUD']

    SleepTime = -1
    EndRow = 64

    def __init__(self):
        self.SleepTime = -1

    def setSleepTime(self, sleeptime):
        if sleeptime != '':
            self.SleepTime = sleeptime
            print("已按照默认设置刷新(120s)\n")
        else:
            self.SleepTime = -1

    def QuotationFlow(self, QuotationList):
        while True:
            a = self.getQuotation()
            QuotationList += a

            print(self.SleepTime)
            time.sleep(self.SleepTime)

    def getQuotation(self):
        error_times = 0
        try:
            r = requests.get('https://papi.icbc.com.cn/icbc/iepa/oproxy/rest/nsexchanges/latest')
            r.encoding = "utf-8"
        except:
            print("Internet Error, waiting 2s.\n")
            error_times += 1
            tm.sleep(2)
            while error_times <= 3:
                r = requests.get('https://papi.icbc.com.cn/icbc/iepa/oproxy/rest/nsexchanges/latest')
            else:
                print("Retry 3 times, break!")
                exit()

        html = r.text
        text = json.loads(html)

        QuotationList = []

        for row in text['data']:
            try:
                if 'currencyType' in row and 'currencyCHName' in row and 'currencyENName' in row and 'reference' in row \
                        and 'foreignBuy' in row and 'foreignSell' in row and 'cashBuy' in row and 'cashSell' in row \
                        and 'publishDate' in row and 'publishTime' in row:


                    # QuotationDict = {'BankName', 'CurrencyName', 'TimeStamp', 'SE_Bid', 'SE_Ask', 'BN_Bid', 'BN_Ask'}
                    QuotationDictTmp = FXPositionDict()
                    QuotationDictTmp.BankName = 'ICBC'
                    QuotationDictTmp.CurrencyCode = row['currencyENName']
                    QuotationDictTmp.TimeStamp = datetime.datetime.strptime(
                        row['publishDate'] + '_' + row['publishTime'], "%Y-%m-%d_%H:%M:%S")
                    QuotationDictTmp.SE_Bid = row['foreignBuy']
                    QuotationDictTmp.SE_Ask = row['foreignSell']
                    QuotationDictTmp.BN_Bid = row['cashBuy']
                    QuotationDictTmp.BN_Ask = row['cashSell']
                    QuotationDictTmp.CurrencyUnit = 100

                    if QuotationDictTmp.CurrencyCode in self.CurrencyCodeList:
                        QuotationList.append(QuotationDictTmp)
                else:
                    print('table fault')
                    exit()
            except IndexError:
                break
        print('ICBC Spider RownNum_' + str(len(text['data'])) + ' is endness.')
        return QuotationList
