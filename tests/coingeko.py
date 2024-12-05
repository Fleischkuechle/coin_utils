import requests
import json

api_coins = {
    "BTC": "bitcoin",
    "BCH": "bitcoin-cash",
    "DGB": "digibyte",
    "DASH": "dash",
    "QTUM": "qtum",
    "DOGE": "dogecoin",
    "KMD": "komodo",
    "ETH": "ethereum",
    "BAT": "basic-attention-token",
    "USDC": "usd-coin",
    "LTC": "litecoin",
    "VRSC": "verus-coin",
    "OMG": "omisego",
    "RVN": "ravencoin",
    "RFOX": "redfox-labs",
    "ZILLA": "chainzilla",
}


def get_prices_in_usd(coins_dict):

    url = "https://api.coingecko.com/api/v3/simple/price"
    coin_string = ",".join(list(coins_dict.values()))
    params = dict(ids=coin_string, vs_currencies="usd")
    r = requests.get(url=url, params=params)
    prices = r.json()

    return prices


# getting usd prices from coingecko
gecko_prices = get_prices_in_usd(api_coins)

# changing coin names to tickers for consistency with makerbot api
gecko_prices_with_tickers = {}
for coin_name in gecko_prices.keys():
    for key in api_coins.keys():
        if api_coins[key] == coin_name:
            gecko_prices_with_tickers[key] = gecko_prices[coin_name]

# calculating ratios with pair format similar to makerbot
gecko_ratios = {}
for ticker_a in gecko_prices_with_tickers:
    for ticker_b in gecko_prices_with_tickers:
        if ticker_a != ticker_b:
            gecko_ratios[ticker_a + "/" + ticker_b] = (
                gecko_prices_with_tickers[ticker_a]["usd"]
                / gecko_prices_with_tickers[ticker_b]["usd"]
            )

# getting ratio prices from makerbot
makerbot_ratios_original = requests.get(
    "http://95.217.44.58:81/api/v1/getallprice"
).json()

# converting for easier comparison
makerbot_ratios = {}
for ticker in makerbot_ratios_original:
    for ticker_ratio in ticker:
        for ratio in ticker[ticker_ratio]:
            for k, v in ratio.items():
                makerbot_ratios[k] = v

# compare gecko ratio with makerbot ratio
for gecko_ticker in gecko_ratios:
    if gecko_ticker in makerbot_ratios:
        percentage_difference = (
            (gecko_ratios[gecko_ticker] - float(makerbot_ratios[gecko_ticker]))
            / gecko_ratios[gecko_ticker]
            * 100
        )
        if abs(percentage_difference) > 1:
            print(
                gecko_ticker
                + " ratio diff is more than 1%. Diff is: "
                + str(percentage_difference)
            )
        else:
            print(gecko_ticker + " ratio is almost the same")
