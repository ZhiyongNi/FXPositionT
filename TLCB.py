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


class TLCB:
    CurrencyNameList = ['826', '978', '840', '392', '344']
    CurrencyCodeList = ['GBP', 'EUR', 'USD', 'JPY', 'HKD']

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
            a = self.getFXPosition()
            QuotationList += a

            print(self.SleepTime)
            time.sleep(self.SleepTime)

    def getFXPosition(self):
        error_times = 0
        try:
            r = requests.post('https://ebank.zjtlcb.com/perbank/PB0000_currencyRate.do',
                              data={'trxCode': 'PB0000', 'tranFlag': '1', 'format': 'JSON', 'srcChannel': 'WEB'})
            r.encoding = "utf-8"
        except:
            print("Internet Error, waiting 2s.\n")
            error_times += 1
            tm.sleep(2)
            while error_times <= 3:
                r = requests.post('https://ebank.zjtlcb.com/perbank/PB0000_currencyRate.do',
                                  data={'trxCode': 'PB0000', 'tranFlag': '1', 'format': 'JSON', 'srcChannel': 'WEB'})
            else:
                print("Retry 3 times, break!")
                exit()

        with open('query.json', encoding='utf-8') as file_obj:
            contents = file_obj.read()

        html = contents.rstrip()
        text = json.loads(html)

        FXPositionList = []

        for row in text['rows']:
            try:
                print(row)

                if 'reserveId' in row and 'tradeAccount' in row and 'accountName' in row and 'dataDate' in row \
                        and 'organ' in row and 'currency' in row and 'accountBalance' in row and 'yesterdayAccountBalance' in row \
                        and 'accountType' in row and 'accountRemarks' in row and 'status' in row and 'removeId' in row:

                    FXPositionDictTmp = FXPositionDict()
                    FXPositionDictTmp.reserveId = row['reserveId']
                    FXPositionDictTmp.tradeAccount = row['tradeAccount']
                    FXPositionDictTmp.accountName = row['accountName']
                    FXPositionDictTmp.dataDate = row['dataDate']
                    #FXPositionDictTmp.TimeStamp = datetime.datetime.strptime(
                     #   row['valDate'] + '_' + row['valTime'], "%Y-%m-%d_%H:%M:%S")
                    #FXPositionDictTmp.SE_Bid = row['buyPrice']
                    #FXPositionDictTmp.SE_Ask = row['selPrice']
                    #FXPositionDictTmp.BN_Bid = row['cashBuyPrice']
                    #FXPositionDictTmp.BN_Ask = row['cashSellPrice']
                    #FXPositionDictTmp.CurrencyUnit = 100

                    FXPositionList.append(FXPositionDictTmp)
                else:
                    print('table fault')
                    exit()

            except IndexError:

                break
        print('TLCB Spider RownNum_' + str(len(text['cd']['exchangeRateList'])) + ' is endness.')
        return FXPositionList
