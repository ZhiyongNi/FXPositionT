# -*- coding:utf-8 -*- 
# 
# 
# 

import datetime
import json
import os
import time
import time as tm
import xml
from xml.dom.minidom import parseString

import requests
from scrapy.selector import Selector

from FXPositionDict import FXPositionDict


class CCBH:
    CurrencyNameList = ['826', '978', '840', '392', '344', '124', '036']
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
            r = requests.get('http://www1.ccb.com/cn/home/news/jshckpj_new.xml')
            r.encoding = "utf-8"
        except:
            print("Internet Error, waiting 2s.\n")
            error_times += 1
            tm.sleep(2)
            while error_times <= 3:
                r = requests.get('http://www1.ccb.com/cn/home/news/jshckpj_new.xml')
            else:
                print("Retry 3 times, break!")
                exit()
        html = r.text
        xml_dom = parseString(html)

        QuotationList = []

        for row in xml_dom.getElementsByTagName("ReferencePriceSettlement"):
            try:
                if len(row.getElementsByTagName('Ofrd_Ccy_CcyCd')) and len(
                        row.getElementsByTagName('Ofr_Ccy_CcyCd')) and len(
                    row.getElementsByTagName('BidRateOfCash')) and len(
                    row.getElementsByTagName('OfrRateOfCash')) and len(
                    row.getElementsByTagName('BidRateOfCcy')) and len(
                    row.getElementsByTagName('OfrRateOfCcy')) and len(
                    row.getElementsByTagName('HBBnk_Bss_Buy_Prc')) and len(
                    row.getElementsByTagName('HBBnk_Bss_Sell_Prc')) and len(
                    row.getElementsByTagName('Mdl_ExRt_Prc')) and len(row.getElementsByTagName('LstPr_Dt')) and len(
                    row.getElementsByTagName('LstPr_Tm')) and len(
                    row.getElementsByTagName('ExRt_StCd')):

                    # QuotationDict = {'BankName', 'CurrencyName', 'TimeStamp', 'SE_Bid', 'SE_Ask', 'BN_Bid', 'BN_Ask'}
                    QuotationDictTmp = FXPositionDict()
                    QuotationDictTmp.BankName = 'CCBH'
                    QuotationDictTmp.CurrencyCode = row.getElementsByTagName('Ofrd_Ccy_CcyCd')[0].childNodes[
                        0].nodeValue
                    QuotationDictTmp.TimeStamp = datetime.datetime.strptime(
                        row.getElementsByTagName('LstPr_Dt')[0].childNodes[0].nodeValue + '_' +
                        row.getElementsByTagName('LstPr_Tm')[0].childNodes[0].nodeValue, "%Y%m%d_%H%M%S")
                    QuotationDictTmp.SE_Bid = row.getElementsByTagName('BidRateOfCcy')[0].childNodes[0].nodeValue
                    QuotationDictTmp.SE_Ask = row.getElementsByTagName('OfrRateOfCcy')[0].childNodes[0].nodeValue
                    QuotationDictTmp.BN_Bid = row.getElementsByTagName('BidRateOfCash')[0].childNodes[0].nodeValue
                    QuotationDictTmp.BN_Ask = row.getElementsByTagName('OfrRateOfCash')[0].childNodes[0].nodeValue
                    QuotationDictTmp.CurrencyUnit = 1

                    if QuotationDictTmp.CurrencyCode in self.CurrencyNameList:
                        QuotationDictTmp.CurrencyCode = self.CurrencyCodeList[
                            self.CurrencyNameList.index(QuotationDictTmp.CurrencyCode)]
                        QuotationList.append(QuotationDictTmp)
                else:
                    print('table fault')
                    exit()

            except IndexError:

                break
        print('CCBH Spider RownNum_' + str(
            len(xml_dom.getElementsByTagName("ReferencePriceSettlement"))) + ' is endness.')
        return QuotationList
