import pandas as pd
import numpy as np
from IPython.display import display


def show_column_rank(df, column):
    return (
        df.groupby([column])[column]
        .count()
        .reset_index(name="Count")
        .sort_values(["Count"], ascending=False)
    )


def valid_generated_nums(numList, df, tests):
    msg = ""
    for t in tests:
        assertValue = t["assert"](numList, df)[0]
        if t["rule"] == "range":
            if assertValue in t[t["rule"]]:
                continue
            else:
                msg = f'Failed with {t["desc"]} assert value {assertValue}'
                return False
        if t["rule"] == "notInList":
            if assertValue not in t[t["rule"]]:
                continue
            else:
                msg = f'Failed with {t["desc"]} assert value {assertValue}'
                return False
        if t["rule"] == "rank":
            df_t = t[t["rule"]].head(t["max"])
            ar_t = df_t[t["column"]].to_list()
            if assertValue in ar_t:
                # msg = f'{t["name"]} test {t["assert"]} rank {ar_t.index(t["assert"])}'
                continue
            else:
                msg = f'Failed with {t["desc"]} assert value {assertValue}'
                return False

    return True

# Analyze score with ranking
# def analyze_generated_nums(numList, df, tests):
#     l = [0] * len(tests)
#     v = [0] * len(tests)
#     msg = ""

#     for i, t in enumerate(tests):
#         assertValue = t["assert"](numList, df)[0]
#         if t["rule"] == "range":
#             if assertValue in t[t["rule"]]:
#                 l[i] = t["mean"] - assertValue % t["mean"]
#                 v[i] = assertValue
#             else:
#                 msg = f'Failed with {t["name"]} assert value {assertValue}'
#                 l[i] = -1
#         if t["rule"] == "notInList":
#             if assertValue not in t[t["rule"]]:
#                 l[i] = 1
#                 v[i] = assertValue
#             else:
#                 msg = f'Failed with {t["name"]} assert value {assertValue}'
#                 l[i] = 0
#         if t["rule"] == "rank":
#             df_t = t[t["rule"]]
#             ar_t = df_t[t["column"]].to_list()
#             ar_t.reverse()
            
#             v[i] = assertValue
#             if assertValue in ar_t:
#                 l[i] = ar_t.index(assertValue)
#             else:
#                 msg = f'Failed with {t["name"]} assert value {assertValue}'
#                 l[i] = -1

#     return l, v, msg


# Analyze score with counts
def analyze_generated_nums(numList, df, tests):
    l = [0] * len(tests)
    v = [0] * len(tests)
    msg = ""

    for i, t in enumerate(tests):
        assertValue = t["assert"](numList, df)[0]
        if t["rule"] == "range":
            if assertValue in t[t["rule"]]:
                l[i] = t["mean"] - assertValue % t["mean"]
                v[i] = assertValue
            else:
                msg = f'Failed with {t["name"]} assert value {assertValue}'
                l[i] = -1
        if t["rule"] == "notInList":
            if assertValue not in t[t["rule"]]:
                l[i] = 1
                v[i] = assertValue
            else:
                msg = f'Failed with {t["name"]} assert value {assertValue}'
                l[i] = 0
        if t["rule"] == "rank":
            df_t = t[t["rule"]]
            find = df_t.loc[df_t[t["column"]] == assertValue, 'Count']
            v[i] = assertValue
            if len(find):
                l[i] = find.item()
            else:
                msg = f'Failed with {t["name"]} assert value {assertValue}'
                l[i] = 0

    return l, v, msg

def normalized_col(df, columns):
    for c in columns:
        df[c] = (df[c] - df[c].min()) / (df[c].max() - df[c].min())

    return df

def predict_lotto(lotto, df, tests, runs=100, debug=False):
    testCols = [ i["name"] for i in tests]
    columns = [f"Draw{i}" for i in range(1, lotto.noOfDraws + 1)]
    
    if debug:
        testCols += [s.replace("Test", "") for s in testCols] + ["msg"]

    # Generate random numbers and analyze the numbers
    data = []
    data_res = []
    
    # Generate number frequency for generating random lotto numbers using last 20? draws
    t = pd.melt(df.iloc[0:20], id_vars='Date', value_vars=[f'Draw{i}' for i in range(1, lotto.noOfDraws + 1)], value_name='Draw')
    t = t.groupby(['Draw'])['Draw'].count().reset_index(name="Count").sort_values(["Draw"])
    counts = []
    for i in range(0, 49):
        counts.append(int(t[t['Draw'] == i+1]['Count'].values[0]) if len(t[t['Draw'] == i+1]) else 0)
    if 0 in counts:
        counts = [ c+1 for c in counts]
        
    for i in range(runs):
        # Prevent duplicate lotto draws
        while True:
            numList = lotto.generate_lotto_nums(counts)
            if numList not in data:
                break
        data.append(numList)
        result, v, m = analyze_generated_nums(numList, df, tests)
        
        if debug:
            data_res.append(result + v + [m])
        else:
            data_res.append(result)

    df = pd.DataFrame(data, columns=columns)
    df_res = pd.DataFrame(data_res, columns=testCols)

    df = df.join(df_res)

    # Normalize the test columns
    df = normalized_col(df, testCols)
    df.loc[:, testCols] *= np.array([t["weight"] if t["weight"] else 1 for t in tests])
    df["Score"] = df[testCols].sum(axis=1)

    return df.sort_values("Score", ascending=False).reset_index(drop=True)


def backtest_lotto(lotto, dfOrg, tests, runs=100, numOfTest=1):
    print(f"Run {runs} simulation for each test")
    df = dfOrg.copy()
    
    data = []
    
    for t in range(numOfTest):
        current = df.iloc[0].to_list()
        draw = current[1 : lotto.noOfDraws + 1]
        date = current[0]
        df = df.iloc[1 : len(df)]

        df_predict = predict_lotto(
            lotto,
            df,
            tests,
            runs=runs
        )
        df_predict["Result"] = df_predict[
            [f"Draw{i}" for i in range(1, lotto.noOfDraws+1)]
        ].apply(lambda x: len(list(set(x) & set(draw))), axis=1)
        
        mean = df_predict["Score"].mean()
        std = df_predict["Score"].std()
        minS = df_predict["Score"].min()
        maxS = df_predict["Score"].max()
        
        print(date.strftime('%Y-%m-%d'), draw, mean, std)
        
        # print([round(n, 6) for n in [
        #     minS, 
        #     (minS + mean - std) / 2, 
        #     mean-std, 
        #     mean-std/2, 
        #     mean+std/2,
        #     mean+std, 
        #     (mean +std + maxS) / 2,
        #     maxS]])
        
        df_hit = df_predict[df_predict["Result"] >= 3].sort_values(["Result", "Score"], ascending=False)

        # display(df_predict.head())
        # print()
        display(df_hit.head())
        print()
        
        # return df_predict
        
        data.append([
            date, 
            ' '.join([str(x) for x in draw]), 
            len(df_predict[df_predict["Result"] == 3]), 
            len(df_predict[df_predict["Result"] == 4]),
            len(df_predict[df_predict["Result"] == 5])
        ])
        
        
    return pd.DataFrame(data, columns=['Date', 'Draw', 'Hit3', 'Hit4', 'Hit5'])
