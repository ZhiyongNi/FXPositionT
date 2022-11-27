import pandas as pd
import math


class Process_LP_USD:
    rule = pd.read_excel("eurandusd.xlsx")
    df = rule.iloc[:8, -1]
    rule = rule.iloc[:8, :4]
    rule["current"] = df  # 使用两个用来保留索引
    rule["orignal_current"] = rule["current"]
    rule = rule.set_index("账户行名称")

    # 先把余额不足的填满
    low_limit_bank = ["德意志法兰克福", "中行法兰克福", "花旗爱尔兰", "招行香港", "工行路桥境内外币支付账户",
                      "工行路桥一般清算账户", "中行路桥一般清算账户", "交行台州"]
    adjust_low_limit = {}  # 对于非数变量使用字典
    for bank in low_limit_bank:  # 每个for循环是可以定义一个新的变量的
        if rule.loc[bank, "current"] - rule.loc[bank, "余额下限"] < 0:
            adjust_low_limit[bank] = abs(rule.loc[bank, "current"] - rule.loc[bank, "余额下限"])

    # 找出有账户盈余超出的银行
    up_limit_bank = ["德意志法兰克福", "中行法兰克福", "花旗爱尔兰", "工行路桥境内外币支付账户", "中行路桥一般清算账户",
                     "交行台州"]
    adjust_up_limit = {}
    for bank in up_limit_bank:
        if rule.loc[bank, "current"] - rule.loc[bank, "余额上限"] > 0:
            adjust_up_limit[bank] = abs(rule.loc[bank, "current"] - rule.loc[bank, "余额上限"])

    adjust_up_limit_df = pd.DataFrame(list(adjust_up_limit.values()), index=adjust_up_limit.keys(),
                                      columns=["超出部分"]).sort_values("超出部分", ascending=False)
    adjust_low_limit_df = pd.DataFrame(list(adjust_low_limit.values()), index=adjust_low_limit.keys(),
                                       columns=["不足部分"]).sort_values("不足部分", ascending=False)
    # 将要转移的单独列出，而后排序分配

    # 资金转给不足的银行
    df2 = pd.DataFrame([], columns=['from', 'to', 'value'])

    for recieve_bank in adjust_low_limit_df.index:  # 用字典可以实现字符串的选取，方便直接选取中文,这里用来给不足的银行填补
        adjust_up_limit_df["累计超出"] = adjust_up_limit_df["超出部分"].cumsum()  # 分别计算共超出多少以及共不足多少
        lack_amount = adjust_low_limit_df.loc[recieve_bank, "不足部分"]

        # 判断需要几家银行才能对不足部分进行补充
        fill_over_bank = list(adjust_up_limit_df[adjust_up_limit_df["累计超出"] < lack_amount].index)
        not_fill_over_bank = list(adjust_up_limit_df[adjust_up_limit_df["累计超出"] > lack_amount].iloc[:1].index)
        fill_bank = fill_over_bank + not_fill_over_bank
        if len(fill_over_bank) != 0:
            for give_bank in fill_over_bank:
                give_moeny = adjust_up_limit_df.loc[give_bank, "超出部分"]
                lack_amount = lack_amount - give_moeny
                adjust_up_limit_df.loc[give_bank, "超出部分"] = 0
                rule.loc[give_bank, "current"] = 0
                df3 = pd.DataFrame([[give_bank, recieve_bank, give_moeny]], columns=['from', 'to', 'value'])
                df2 = df2.append(df3, ignore_index=True)

        for give_bank in fill_bank:
            adjust_up_limit_df.loc[give_bank, "超出部分"] = adjust_up_limit_df.loc[give_bank, "超出部分"] - lack_amount
            rule.loc[give_bank, "current"] = rule.loc[give_bank, "current"] - lack_amount
            df3 = pd.DataFrame([[give_bank, recieve_bank, lack_amount]], columns=['from', 'to', 'value'])
            df2 = df2.append(df3, ignore_index=True)

        adjust_low_limit_df.loc[recieve_bank, "不足部分"] = 0
        rule.loc[recieve_bank, "current"] = rule.loc[recieve_bank, "余额下限"]

    recieve_bank = "交行台州"
    recieve_bank2 = "招行香港"
    recieve_bank3 = "工行路桥一般清算账户"
    for give_bank in adjust_up_limit_df.index:
        give_money = adjust_up_limit_df.loc[give_bank, "超出部分"]
        if (give_money + rule.loc[recieve_bank, "current"] <= rule.iloc[7, 2]):
            rule.loc[give_bank, "current"] = rule.loc[give_bank, "current"] - give_money
            rule.loc[recieve_bank, "current"] = rule.loc[recieve_bank, "current"] + give_money
            adjust_up_limit_df.loc[give_bank, "超出部分"] = 0  # 将之清零
            df3 = pd.DataFrame([[give_bank, recieve_bank, give_money]], columns=['from', 'to', 'value'])
            df2 = df2.append(df3, ignore_index=True)
        else:
            if (rule.loc[recieve_bank, "current"] != rule.iloc[7, 2]):
                rule.loc[give_bank, "current"] -= (rule.iloc[7, 2] - rule.loc[recieve_bank, "current"])
                give_money -= (rule.iloc[7, 2] - rule.loc[recieve_bank, "current"])
                adjust_up_limit_df.loc[give_bank, "超出部分"] -= (rule.iloc[7, 2] - rule.loc[recieve_bank, "current"])
                df3 = pd.DataFrame([[give_bank, recieve_bank, rule.iloc[7, 2] - rule.loc[recieve_bank, "current"]]],
                                   columns=['from', 'to', 'value'])
                df2 = df2.append(df3, ignore_index=True)
                rule.loc[recieve_bank, "current"] = rule.iloc[7, 2]
            if (give_bank in ['德意志法兰克福', '中行法兰克福', '花旗爱尔兰', '工行路桥境内外币支付账户']):
                rule.loc[give_bank, "current"] = rule.loc[give_bank, "current"] - give_money
                rule.loc[recieve_bank2, "current"] = rule.loc[recieve_bank2, "current"] + give_money
                adjust_up_limit_df.loc[give_bank, "超出部分"] = 0  # 将之清零
                df3 = pd.DataFrame([[give_bank, recieve_bank2, give_money]], columns=['from', 'to', 'value'])
                df2 = df2.append(df3, ignore_index=True)
            else:
                rule.loc[give_bank, "current"] = rule.loc[give_bank, "current"] - give_money
                rule.loc[recieve_bank3, "current"] = rule.loc[recieve_bank3, "current"] + give_money
                adjust_up_limit_df.loc[give_bank, "超出部分"] = 0  # 将之清零
                df3 = pd.DataFrame([[give_bank, recieve_bank3, give_money]], columns=['from', 'to', 'value'])
                df2 = df2.append(df3, ignore_index=True)

    df2['true_trans'] = df2['value'].apply(lambda x: math.floor(x / (5 * (10 ** 5))) * (5 * (10 ** 5)))  # 默认取下整
    # del df2['value']
    outputpath = 'banks.csv'
    df2.to_csv(outputpath, index=True, header=True, encoding='utf-8-sig')
