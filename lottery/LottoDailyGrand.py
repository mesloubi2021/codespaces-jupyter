#!/usr/bin/env python
# coding: utf-8

# ## Daily Grand 规律总结
# 
# - Sum mean 125 std 30 (Best between 95 ~ 155)
# 
# - Top 10 Sum **[124, 118, 146, 102, 121, 122, 133]** hit almost 15% of total count 
# 
# - Draw Top picks **[14, 43, 17, 4, 38]**
# 
# - 2022 Bonus Top picks **[2, 4, 6, 7, 1, 5, 3]**
# 
# - 3个奇数 2个偶数 或者 2个奇数 3个偶数的组合最多
# 
# - 新号码 至少2~3个号码 出现在最近6次抽奖中 (大概23个号码)

# In[1]:


import sys
sys.path.append('./lib')
import numpy
import pandas as pd
from lotto import Lotto
from utils import *
import optparse
import warnings
warnings.filterwarnings('ignore')

# pd.options.display.max_columns = None
# pd.options.display.max_rows = None

parser = optparse.OptionParser()

parser.add_option('-r', '--runs',
    action="store", dest="runs",
    help="Number of runs for each test", default="100")

parser.add_option('-n', '--num',
    action="store", dest="num",
    help="Number of backtest to go back to in the history", default="10")

parser.add_option('-g', '--gen',
    action="store_true", dest="gen",
    help="Generate data analysis based on raw data")

options, args = parser.parse_args()

runs = int(options.runs)
numOfTest = int(options.num)


# In[2]:


lotto = Lotto('Daily Grand')


# In[3]:

if  options.gen:
    print('Generate data analysis based on raw data')
    df = pd.read_csv("./data/DailyGrand/DailyGrand.raw.csv", parse_dates=['Date'])
    df = lotto.build_sum_div_bucket(df)
    df = lotto.get_prev_draws_analytics(df)
    df.to_csv("./data/DailyGrand/DailyGrand.analytics.csv", index=False)
    exit()


# In[4]:


# print("Generate sum, bucket, divide analytics")
# 

# print("Generate the relations between previous draws and current draws")
# 


# In[5]:


df = pd.read_csv("./data/DailyGrand/DailyGrand.analytics.csv", parse_dates=['Date'])


# In[6]:


# df['SumNoBonus'].plot.hist(bins=100, alpha=0.5)


# In[7]:


# show_column_rank(df[df['Date']>'2022-01-01'], "GrandNum").head()


# In[55]:


tests = [
    {
        "name": "TestSum",
        "des": "Test Sum",
        "assert": lotto.test_sum,
        "rule": "rank",
        "column": "SumNoBonus",
        "rank": show_column_rank(df, "SumNoBonus"),
        "weight": 1
    },
    {
        "name": "TestPrev3",
        "desc": "Test with Previous 3 Draws",
        "assert": lotto.test_count_in_prev_draws(3),
        "rule": "rank",
        "column": "Prev3",
        "rank": show_column_rank(df, "Prev3"),
        "weight": 1
    },
    {
        "name": "TestPrev6",
        "desc": "Test with Previous 6 Draws",
        "assert": lotto.test_count_in_prev_draws(6),
        "rule": "rank",
        "column": "Prev6",
        "rank": show_column_rank(df, "Prev6"),
        "weight": 1
    },
    {
        "name": "TestOnesDigit",
        "desc": "Test Ones Digit",
        "assert": lotto.test_ones_digit,
        "rule": "rank",
        "column": "OnesDigit",
        "rank": show_column_rank(df, "OnesDigit"),
        "weight": 1
    },
    {
        "name": "TestTensDigit",
        "desc": "Test Tens Digit",
        "assert": lotto.test_tens_digit,
        "rule": "rank",
        "column": "TensDigit",
        "rank": show_column_rank(df, "TensDigit"),
        "weight": 1
    },
    {
        "name": "TestBigSmall",
        "desc": "Test Big Small Nums",
        "assert": lotto.test_big_small,
        "rule": "rank",
        "column": "BigSmall",
        "rank": show_column_rank(df, "BigSmall"),
        "weight": 1
    },
    {
        "name": "TestPrime",
        "desc": "Test Prime Numbers",
        "assert": lotto.test_prime,
        "rule": "rank",
        "column": "Prime",
        "rank": show_column_rank(df, "Prime"),
        "weight": 1
    },
    {
        "name": "TestMinPrimeSum",
        "desc": "Test Sum of Min Prime Numbers",
        "assert": lotto.test_min_prime_sum,
        "rule": "rank",
        "column": "MinPrimeSum",
        "rank": show_column_rank(df, "MinPrimeSum"),
        "weight": 1
    },
    {
        "name": "TestAC",
        "desc": "Test AC Value",
        "assert": lotto.test_ac_value,
        "rule": "rank",
        "column": "AC",
        "rank": show_column_rank(df, "AC"),
        "weight": 1
    },
    {
        "name": "TestDivide2",
        "desc": "Test Divide by 2",
        "assert": lotto.test_divide(2),
        "rule": "rank",
        "column": "Divide2",
        "rank": show_column_rank(df, "Divide2"),
        "weight": 1
    },
    {
        "name": "TestDivide3",
        "desc": "Test Divide by 3",
        "assert": lotto.test_divide(3),
        "rule": "rank",
        "column": "Divide3",
        "rank": show_column_rank(df, "Divide3"),
        "weight": 1
    },
    {
        "name": "TestDivide5",
        "desc": "Test Divide by 5",
        "assert": lotto.test_divide(5),
        "rule": "rank",
        "column": "Divide5",
        "rank": show_column_rank(df, "Divide5"),
        "weight": 1
    },
]


# In[9]:


# def valid_generated_nums(numList, df, tests):
#     msg = ''
#     for t in tests:
#         assertValue = t["assert"](numList, df)[0]
#         if t["rule"] == "range":
#             if assertValue in t[t["rule"]]:
#                 continue
#             else:
#                 msg = f'Failed with {t["name"]} assert value {assertValue}'
#                 return False
#         if t["rule"] == "notInList":
#             if assertValue not in t[t["rule"]]:
#                 continue
#             else:
#                 msg = f'Failed with {t["name"]} assert value {assertValue}'
#                 return False
#         if t["rule"] == "rank":
#             df_t = t[t["rule"]].head(t["max"])
#             ar_t = df_t[t["column"]].to_list()
#             if assertValue in ar_t:
#                 # msg = f'{t["name"]} test {t["assert"]} rank {ar_t.index(t["assert"])}'
#                 continue
#             else:
#                 msg = f'Failed with {t["name"]} assert value {assertValue}'
#                 return False
            
#     return True


# In[10]:


# counter = 0
# for i in range(10):
#     numList = lotto.generate_lotto_nums()
#     result = valid_generated_nums(numList, df, tests)
#     if result:
#         counter+=1
#         print(counter, numList)


# In[11]:


# def analyze_generated_nums(numList, df, tests):
#     l = [0] * len(tests)
#     msg = ''

#     for i, t in enumerate(tests):
#         assertValue = t["assert"](numList, df)[0]
#         if t["rule"] == "range":
#             if assertValue in t[t["rule"]]:
#                 l[i] = t["mean"] - assertValue % t["mean"]
#             else:
#                 msg = f'Failed with {t["name"]} assert value {assertValue}'
#                 return [0] * len(tests), msg
#         if t["rule"] == "notInList":
#             if assertValue not in t[t["rule"]]:
#                l[i] = 1
#             else:
#                 msg = f'Failed with {t["name"]} assert value {assertValue}'
#                 return [0] * len(tests), msg
#         if t["rule"] == "rank":
#             df_t = t[t["rule"]].head(t["max"])
#             ar_t = df_t[t["column"]].to_list()
#             if assertValue in ar_t:
#                 l[i] = t["max"] - ar_t.index(assertValue)
#                 # msg = f'{t["name"]} test {t["assert"]} rank {ar_t.index(t["assert"])}'
#                 continue
#             else:
#                 msg = f'Failed with {t["name"]} assert value {assertValue}'
#                 return [0] * len(tests), msg

#     return l, msg

# def normalized_col(df, columns):
#     for c in columns:
#         df[c] = (df[c] - df[c].min())/(df[c].max()-df[c].min())
        
#     return df


# In[12]:


# data = []
# for i in range(1000):
#     numList = lotto.generate_lotto_nums()
#     result = analyze_generated_nums(numList, df, tests)[0]
#     data.append(numList + result)

# df_p = pd.DataFrame(data, columns=['Draw1','Draw2','Draw3','Draw4','Draw5','TestSum','TestPrev','TestOE', 'TestBucket'])
# df_p = normalized_col(df_p, ['TestSum','TestPrev','TestOE', 'TestBucket'])
# df_p['Score'] = df_p[['TestSum','TestPrev','TestOE', 'TestBucket']].sum(axis=1)
# df_p.sort_values('Score', ascending=False)


# In[13]:


# for i in range(100):
#     backtest_lotto(lotto, df, tests,
#                    runs=100 * 20,
#                    numOfTest=1
#                   )


# In[ ]:


backtest_lotto(lotto, df, tests, runs=runs, numOfTest=numOfTest)


# In[15]:


# df.to_csv('./data/DailyGrand/DailyGrand.analytics.csv', index=False)

