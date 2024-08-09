import numpy as np
import pandas as pd
import math
import random
from sympy import isprime
from functools import reduce

# The Lotto class doesn't count Bonus ball
class Lotto:
    noOfDraws = 5
    maxPrevDraws = 6
    maxNum = 49
    bins = [10,20,30,40,50]
    
    
    def __init__(self, name):
        self.name = name
        
        if name == "Daily Grand":
            self.noOfDraws = 5
            self.maxPrevDraws = 6
            self.maxNum = 49
        elif name == "649":
            self.noOfDraws = 6
            self.maxPrevDraws = 6
            self.maxNum = 49
        elif name == "Max Lotto":
            self.noOfDraws = 7
            self.maxPrevDraws = 6
            self.maxNum = 50
        else:
            raise Exception("Invalid Lotto type only support [Max Lotto, 649, Daily Grand]")
            
    
    def build_sum_div_bucket(self, df):
        df['SumNoBonus'] = df[[f"Draw{i}" for i in range(1, self.noOfDraws + 1)]].sum(axis=1)
        df['Sum'] = df['SumNoBonus'] + df['GrandNum']

        df["TensDigit"] = 0
        for i in range(1, self.noOfDraws + 1):
            df["TensDigit"] += 10 ** (df[f"Draw{i}"] / 10).apply(np.floor)
            
        df["OnesDigit"] = 0
        for i in range(1, self.noOfDraws + 1):
            df["OnesDigit"] += df[f"Draw{i}"] % 10
        
        self.build_divide(df, 2)
        self.build_divide(df, 3)
        self.build_divide(df, 5)
        self.build_big_small(df)
        self.build_prime(df)
        self.build_min_prime_sum(df)
        self.build_ac_value(df)

        return df
    
    
    def build_divide(self, df, by=2):
        df[f"Divide{by}"] = 0
        for i in range(1, self.noOfDraws + 1):
            df[f"Divide{by}"] += 10 ** (df["Draw"+str(i)] % by)
          
        
    # 以 25为中位数，大于25为大数， 小于25为小数
    def build_big_small(self, df):
        df["BigSmall"] = 0
        for i in range(1, self.noOfDraws + 1):
            df["BigSmall"] += 10 ** (df[f"Draw{i}"] * 2 / (self.maxNum + 1)).apply(np.floor)
            
    
    # 查看数列里有多少质数
    def build_prime(self, df):
        df["Prime"] = 0
        for i in range(1, self.noOfDraws + 1):
            df["Prime"] += 10 ** df[f"Draw{i}"].apply(lambda x: 1 if isprime(x) else 0)
         
        
    # 对数列里每个数的素数因子求和
    def build_min_prime_sum(self, df):
        df["MinPrimeSum"] = 0
        for index, row in df.iterrows():
            l = []
            for i in range(1, 6):
                l += factors(row[f"Draw{i}"])
            l = [*set(l)]
            df.at[index, "MinPrimeSum"] = sum(l)
            
            
    # 查看ac value 可以得到数列的离散程度
    def build_ac_value(self, df):
        df["AC"] = df[[f"Draw{i}" for i in range(1, self.noOfDraws + 1)]].apply(lambda x: get_ac_value(x.values), axis=1)

            
    # The Dataframe must follow columns names such as []
    def get_prev_draws_analytics(self, df):
        for n in range(1, self.maxPrevDraws+1):
            df['Prev'+str(n)] = 0

        for n in range(1, self.maxPrevDraws+1):
            df['NumCount'+str(n)] = 0

        draws_list = [f'Draw{i}' for i in range(1, self.noOfDraws + 1)]

#         for n in range(1, self.noOfDraws+1):
#             draws_list.append('Draw'+str(n))

        for i in range(len(df)):
            for k in range(1, self.maxPrevDraws+1):
                if i < len(df) - k:
                    dp_t = pd.melt(df.iloc[i+1:i+k+1], id_vars='Date', value_vars=draws_list, value_name='Draw')
                    ar_t = dp_t['Draw'].unique()
                    df.loc[i,'NumCount'+str(k)] = len(ar_t)
                    for j in range(1, self.noOfDraws+1):
                        if df.loc[i, 'Draw'+str(j)] in ar_t:
                            df.loc[i, 'Prev' + str(k)] += 1

        return df


    def generate_lotto_nums(self, counts=None):
        l = random.sample(range(1, self.maxNum + 1), self.noOfDraws, counts=counts)
        
        # if there is duplicates in the list, generate the list again
        if len(l) != len(set(l)):
            return self.generate_lotto_nums(counts)
        
        l.sort()
        return l


    def test_count_in_prev_draws(self, noOfPrevDraws):
        draws_list = [f'Draw{i}' for i in range(1, self.noOfDraws+1)]
        
        def count_in_prev_draws(numList, df):
            counter = 0

            dp_t = pd.melt(df.iloc[0: noOfPrevDraws], id_vars='Date', value_vars=draws_list, value_name='Draw')
            ar_t = dp_t['Draw'].unique()

            for n in numList:
                if n in ar_t:
                    counter += 1

            ar_t.sort()
            return counter, ar_t
        
        return count_in_prev_draws
    
    
    def test_ones_digit(self, numList, _):
        r = 0
        for n in numList:
            r += n % 10
        return r, _
    
    
    def test_tens_digit(self, numList, _):
        r = 0
        for n in numList:
            r += 10 ** math.floor(n / 10)
        return r, _


    def test_divide(self, by):
        def divide_by(numList, _):
            r = 0
            for i in numList:
                r += 10 ** (i % by)
            return r, _
        
        return divide_by
        
            
    def test_sum(self, numList, _):
        return sum(numList), _
    
    
    def test_big_small(self, numList, _):
        r = 0
        for n in numList:
            r += 10 ** math.floor(n * 2 / (self.maxNum + 1))
        return r, _
    
    
    def test_prime(self, numList, _):
        r = 0
        for n in numList:
            r += 10 ** (1 if isprime(n) else 0)
        return r, _
    
    
    def test_min_prime_sum(self, numList, _):
        r = 0
        l = []
        for n in numList:
            l += factors(n)
        l = [*set(l)]
        r = sum(l)
        return r, _
    
    
    def test_ac_value(self, numList, _):
        return get_ac_value(numList), _
    

###########################################################
# Test Template
###########################################################
# tests = [
#     {
#         "name": "Test Sum",
#         "assert": lotto.test_sum,
#         "rule": "range",
#         "range": range(125- int(30*1.25), 125+int(30*1.25)),
#         "mean": 125,
#         "std": 30
#     },
#     {
#         "name": "Test with Previous 6 Draws",
#         "assert": lotto.test_count_in_prev_draws,
#         "rule": "range",
#         "range": range(1, 5),
#         "mean": 3,
#         "std": 30
#     },
#     {
#         "name": "Test Odd Even",
#         "assert": lotto.test_odd_even,
#         "rule": "notInList",
#         "notInList": [50, 5]
#     },
#     {
#         "name": "Test Buck 10 ~ 50",
#         "assert": lotto.test_bucket,
#         "rule": "rank",
#         "column": "Combine10-50",
#         "rank": df.groupby(['Combine10-50'])['Combine10-50'].count().reset_index(name='Count').sort_values(['Count'], ascending=False),
#         "max": 50
#     },
# ]

# Find min prime numbers of a given number
def factors(n):    
    f = list(set(reduce(list.__add__, 
                ([i, n//i] for i in range(1, int(n**0.5) + 1) if n % i == 0))))
    f.sort()
    f = f[1:-1]
    
    if len(f):
        l = []
        for i in f:
            l += factors(i)
        return list(set(l))
    else:
        return [n]
    
    
# Get AC value of a list to indicate how scale the numbers are    
def get_ac_value(nums):
    s = set()
    for i in range(len(nums)):
        a = nums[i]
        for j in range(len(nums) - i -1):
            b = nums[j+i+1]
            s.add(b-a)
    return len(s) - (len(nums) - 1)
        