# -*- coding:utf-8 -*- 
# 
# 
# 

import datetime
import re
import time
import time as tm

import requests
from scrapy.selector import Selector

from FXPositionDict import FXPositionDict


class BCOH:
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

    def QuotationFlow(self):
        while True:
            ##a = self.getQuotation()

            QuotationList = self.getQuotation()
            print(len(QuotationList))
            print(self.SleepTime)
            time.sleep(self.SleepTime)
            break

    def getQuotation(self):
        error_times = 0
        try:
            r = requests.get('https://bankcomm.com/BankCommSite/zonghang/cn/whpj/foreignExchangeSearch_Cn.jsp')
            r.encoding = "utf-8"
        except:
            print("Internet Error, waiting 2s.\n")
            error_times += 1
            tm.sleep(2)
            while error_times <= 3:
                r = requests.get('https://bankcomm.com/BankCommSite/zonghang/cn/whpj/foreignExchangeSearch_Cn.jsp')
            else:
                print("Retry 3 times, break!")
                exit()
        html = r.text

        QuotationList = []

        for row in range(1, self.EndRow):
            try:
                print('000')
                if row == 1 and Selector(text=html).xpath('//tr[%i]/th[1]/text()' % (row)).extract()[0] != '币种' and \
                        Selector(text=html).xpath('//tr[%i]/th[2]/text()' % (row)).extract()[0] != '单位' and \
                        Selector(text=html).xpath('//tr[%i]/th[3]/text()' % (row)).extract()[0] != '现汇买入价' and \
                        Selector(text=html).xpath('//tr[%i]/th[4]/text()' % (row)).extract()[0] != '现汇卖出价' and \
                        Selector(text=html).xpath('//tr[%i]/th[5]/text()' % (row)).extract()[0] != '现钞卖出价':
                    print('111')
                    print('table fault')
                    exit()
                elif Selector(text=html).xpath('//tr[%i]/td[1]/text()' % (row)).extract()[0] in self.CurrencyNameList:
                    print('222')
                    CurrencyName = Selector(text=html).xpath('//tr[%i]/td[1]/text()' % (row)).extract()[0]
                    SE_Bid = Selector(text=html).xpath('//tr[%i]/td[2]/text()' % (row)).extract()[0]
                    BN_Bid = Selector(text=html).xpath('//tr[%i]/td[3]/text()' % (row)).extract()[0]
                    SE_Ask = Selector(text=html).xpath('//tr[%i]/td[4]/text()' % (row)).extract()[0]
                    BN_Ask = Selector(text=html).xpath('//tr[%i]/td[5]/text()' % (row)).extract()[0]
                    TimeStamp = datetime.datetime.strptime(
                        Selector(text=html).xpath('//tr[%i]/td[7]/text()' % (row)).extract()[0], "%Y.%m.%d %H:%M:%S")

                    # QuotationDict = {'BankName', 'CurrencyName', 'TimeStamp', 'SE_Bid', 'SE_Ask', 'BN_Bid', 'BN_Ask'}
                    QuotationDictTmp = FXPositionDict()
                    QuotationDictTmp.BankName = 'BCHO'
                    QuotationDictTmp.CurrencyCode = self.CurrencyCodeList[self.CurrencyNameList.index(CurrencyName)]
                    QuotationDictTmp.TimeStamp = TimeStamp
                    QuotationDictTmp.SE_Bid = SE_Bid
                    QuotationDictTmp.SE_Ask = SE_Ask
                    QuotationDictTmp.BN_Bid = BN_Bid
                    QuotationDictTmp.BN_Ask = BN_Ask
                    QuotationDictTmp.CurrencyUnit = 100

                    QuotationList.append(QuotationDictTmp)
                else:
                    print('333')
                    CurrencyName = Selector(text=html).xpath('//tr[%i]/td[1]/text()' % (row)).extract()[0]

            except IndexError:
                print(IndexError.__dict__)
                print('BCHO Spider RownNum_' + str(row) + ' is endness.')
                break
        return QuotationList
