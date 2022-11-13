# -*- coding:utf-8 -*- 
# 
# 
# 

import datetime
import json
import time
import time as tm

import requests

from FXPositionDict import FXPositionDict


class ABCI:
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
            r = requests.get('https://ewealth.abchina.com/app/data/api/DataService/ExchangeRateV2')
            r.encoding = "utf-8"
        except:
            print("Internet Error, waiting 2s.\n")
            error_times += 1
            tm.sleep(2)
            while error_times <= 3:
                r = requests.get('https://ewealth.abchina.com/app/data/api/DataService/ExchangeRateV2')
            else:
                print("Retry 3 times, break!")
                exit()
        html = r.text
        text = json.loads(html)
        QuotationList = []

        for row in text['Data']['Table']:

            try:
                if 'BenchMarkPrice' in row and 'BuyingPrice' in row and 'SellPrice' in row and 'CashBuyingPrice' in row \
                        and 'PublishTime' in row and 'Id' in row and 'CurrId' in row and 'CurrName' in row:
                    # QuotationDict = {'BankName', 'CurrencyName', 'TimeStamp', 'SE_Bid', 'SE_Ask', 'BN_Bid', 'BN_Ask'}
                    QuotationDictTmp = FXPositionDict()
                    QuotationDictTmp.BankName = 'ABCI'
                    QuotationDictTmp.CurrencyCode = row['CurrName'][-4:-1]
                    QuotationDictTmp.TimeStamp = datetime.datetime.strptime(row['PublishTime'].split('+')[0],
                                                                            "%Y-%m-%dT%H:%M:%S")
                    QuotationDictTmp.SE_Bid = row['BuyingPrice']
                    QuotationDictTmp.SE_Ask = row['SellPrice']
                    QuotationDictTmp.BN_Bid = row['CashBuyingPrice']
                    QuotationDictTmp.BN_Ask = row['SellPrice']
                    QuotationDictTmp.CurrencyUnit = 100

                    if QuotationDictTmp.CurrencyCode in self.CurrencyCodeList:
                        QuotationList.append(QuotationDictTmp)
                else:
                    print('table fault')
                    exit()
            except IndexError:
                break
        print('ABCI Spider RownNum_' + str(len(text['Data']['Table'])) + ' is endness.')
        return QuotationList
