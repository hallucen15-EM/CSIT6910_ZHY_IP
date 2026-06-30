# Copyright 2026 Anthropic PBC
# SPDX-License-Identifier: Apache-2.0
import os

native_tokens = {
    "mainnet": {"name": "ETH", "decimals": 18},
    "bsc": {"name": "BNB", "decimals": 18},
    "poly": {"name": "POL", "decimals": 18},
    "base": {"name": "ETH", "decimals": 18},
    "arbi": {"name": "ETH", "decimals": 18},
    "avax": {"name": "AVAX", "decimals": 18},
    "sonic": {"name": "S", "decimals": 18},
    "redstone": {"name": "ETH", "decimals": 18},
    "goat": {"name": "BTC", "decimals": 18},
    "astar": {"name": "ASTR", "decimals": 18},
    "pulsechain": {"name": "PLS", "decimals": 18},
}

coingecko_chain_mapping = {
    "mainnet": "eth",
    "bsc": "bsc",
    "arbi": "arbitrum",
    "optim": "optimism",
    "poly": "polygon-pos",
    "base": "base",
    "avax": "avax",
    "astar": "astr",
    "katana": "katana",
    "sonic": "sonic",
}

covalent_chain_mapping = {
    "mainnet": "eth-mainnet",
    "bsc": "bsc-mainnet",
    "poly": "matic-mainnet",
    "base": "base-mainnet",
    "optim": "optimism-mainnet",
    "gnosis": "gnosis-mainnet",
}


preferred_dex = {
    "mainnet": "uniswap",
    "bsc": "pancakeswap",
    "poly": "uniswap",
    "base": "uniswap",
    "arbi": "uniswap",
    "avax": "uniswap",
    "sonic": "shadow_exchange",
    "redstone": "uniswap",
    "goat": "goatswap",
    "astar": "arthswap",
    "pulsechain": "pulsex",
}

deployments = {
    "mainnet": {
        "tokens": {
            "wrapped_native_token": {
                "name": "Wrapped Ether",
                "symbol": "WETH",
                "decimals": 18,
                "address": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "block_number_of_deployment": 4719568,
                "date_of_deployment": "2017-12-17",
            },
            "USDT": {
                "name": "Tether USD",
                "symbol": "USDT",
                "decimals": 6,
                "address": "0xdAC17F958D2ee523a2206206994597C13D831ec7",
                "block_number_of_deployment": 4634748,
                "date_of_deployment": "2017-11-28",
            },
            "USDC": {
                "name": "USD Coin",
                "symbol": "USDC",
                "decimals": 6,
                "address": "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
                "block_number_of_deployment": 6082465,
                "date_of_deployment": "2018-08-03",
            },
            "DAI": {
                "name": "Dai Stablecoin",
                "symbol": "DAI",
                "decimals": 18,
                "address": "0x6B175474E89094C44Da98b954EedeAC495271d0F",
                "block_number_of_deployment": 8928158,
                "date_of_deployment": "2019-11-18",
            },
            "WBTC": {
                "name": "Wrapped BTC",
                "symbol": "WBTC",
                "decimals": 8,
                "address": "0x2260FAC5E5542a773Aa44fBCfeDf7C193bc2C599",
                "block_number_of_deployment": 6810108,
                "date_of_deployment": "2019-01-31",
            },
        },
        "uniswap_v2": {
            "factory": {
                "address": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
                "block_number_of_deployment": 10000835,
                "date_of_deployment": "2020-05-04",
            },
            "router02": {
                "address": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                "block_number_of_deployment": 10207858,
                "date_of_deployment": "2020-06-05",
            },
        },
        "uniswap_v3": {
            "factory": {
                "address": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
                "block_number_of_deployment": 12369621,
                "date_of_deployment": "2021-05-05",
            },
            "quoter": {
                "address": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
                "block_number_of_deployment": 12369651,
                "date_of_deployment": "2021-05-05",
            },
            "quoterv2": {
                "address": "0x61fFE014bA17989E743c5F6cB21bF9697530B21e",
                "block_number_of_deployment": 13360886,
                "date_of_deployment": "2021-10-01",
            },
            "swapRouter": {
                "address": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
                "block_number_of_deployment": 12369651,
                "date_of_deployment": "2021-05-05",
            },
            "swapRouter02": {
                "address": "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45",
                "block_number_of_deployment": 13804681,
                "date_of_deployment": "2021-12-01",
            },
        },
        "sushiswap_v2": {
            "factory": {
                "address": "0xc0aEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac",
                "block_number_of_deployment": 10750005,
                "date_of_deployment": "2020-09-04",
            },
            "router02": {
                "address": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
                "block_number_of_deployment": 10750006,
                "date_of_deployment": "2020-09-04",
            },
        },
        "sushiswap_v3": {
            "factory": None,  # Not deployed separately on Ethereum mainnet
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
        "pancakeswap_v2": {
            "factory": None,  # Not deployed on Ethereum mainnet
            "router02": None,
        },
        "pancakeswap_v3": {
            "factory": {
                "address": "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865",
                "block_number_of_deployment": 19243080,
                "date_of_deployment": "2024-02-15",
            },
            "quoter": {
                "address": "0x678Aa4bF4E210cf2166753e054d5b7c31cc7fa86",
                "block_number_of_deployment": 19243080,
                "date_of_deployment": "2024-02-15",
            },
            "quoterv2": {
                "address": "0xB048Bbc1Ee6b733FFfCFb9e9CeF7375518e25997",
                "block_number_of_deployment": 19243080,
                "date_of_deployment": "2024-02-15",
            },
            "swapRouter": {
                "address": "0x1b81D678ffb9C0263b24A97847620C99d213eB14",
                "block_number_of_deployment": 19243080,
                "date_of_deployment": "2024-02-15",
            },
            "swapRouter02": {
                "address": "0x13f4EA83D0bd40E75C8222255bc855a974568Dd4",
                "block_number_of_deployment": 19243080,
                "date_of_deployment": "2024-02-15",
            },
        },
    },
    "bsc": {
        "tokens": {
            "wrapped_native_token": {
                "name": "Wrapped BNB",
                "symbol": "WBNB",
                "decimals": 18,
                "address": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c",
                "block_number_of_deployment": 149268,
                "date_of_deployment": "2020-09-03",
            },
            "BUSD": {
                "name": "Binance-Peg BSC-USD",
                "symbol": "BSC-USD",
                "decimals": 18,
                "address": "0x55d398326f99059fF775485246999027B3197955",
                "block_number_of_deployment": 142188,
                "date_of_deployment": "2020-09-03",
            },
            "USDC": {
                "name": "USD Coin",
                "symbol": "USDC",
                "decimals": 18,
                "address": "0x8AC76a51cc950d9822D68b83fE1Ad97B32Cd580d",
                "block_number_of_deployment": 7453840,
                "date_of_deployment": "2021-05-13",
            },
            "DAI": {
                "name": "Binance-Peg Dai Token",
                "symbol": "DAI",
                "decimals": 18,
                "address": "0x1AF3F329e8BE154074D8769D1FFa4eE058B1DBc3",
                "block_number_of_deployment": 169573,
                "date_of_deployment": "2020-09-09",
            },
            "WBTC": {
                "name": "Wrapped BTC",
                "symbol": "WBTC",
                "decimals": 8,
                "address": "0x0555E30da8f98308EdB960aa94C0Db47230d2b9C",
                "block_number_of_deployment": 23800000,
                "date_of_deployment": "2022-12-01",
            },
        },
        "uniswap_v2": {
            "factory": {
                "address": "0x8909Dc15e40173Ff4699343b6eB8132c65e18eC6",
                "block_number_of_deployment": 35800000,  # Estimated
                "date_of_deployment": "2024-02-01",
            },
            "router02": {
                "address": "0x4752ba5DBc23f44D87826276BF6Fd6b1C372aD24",
                "block_number_of_deployment": 35800000,  # Estimated
                "date_of_deployment": "2024-02-01",
            },
        },
        "uniswap_v3": {
            "factory": {
                "address": "0xdB1d10011AD0Ff90774D0C6Bb92e5C5c8b4461F7",
                "block_number_of_deployment": 26300000,  # Estimated
                "date_of_deployment": "2023-02-01",
            },
            "quoter": None,  # V3 uses QuoterV2 instead
            "quoterv2": {
                "address": "0x78D78E420Da98ad378D7799bE8f4AF69033EB077",
                "block_number_of_deployment": 26300000,  # Estimated
                "date_of_deployment": "2023-02-01",
            },
            "swapRouter": None,  # V3 uses SwapRouter02 instead
            "swapRouter02": {
                "address": "0xB971eF87ede563556b2ED4b1C0b0019111Dd85d2",
                "block_number_of_deployment": 26300000,  # Estimated
                "date_of_deployment": "2023-02-01",
            },
        },
        "sushiswap_v2": {
            "factory": {
                "address": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4",
                "block_number_of_deployment": 450000,  # Estimated
                "date_of_deployment": "2020-09-30",
            },
            "router02": {
                "address": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
                "block_number_of_deployment": 450000,  # Estimated
                "date_of_deployment": "2020-09-30",
            },
        },
        "sushiswap_v3": {
            "factory": None,  # Not deployed on BSC
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
        "pancakeswap_v2": {
            "factory": {
                "address": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
                "block_number_of_deployment": 193325,
                "date_of_deployment": "2020-09-19",
            },
            "router02": {
                "address": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
                "block_number_of_deployment": 193325,
                "date_of_deployment": "2020-09-19",
            },
        },
        "pancakeswap_v3": {
            "factory": {
                "address": "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865",
                "block_number_of_deployment": 27459800,
                "date_of_deployment": "2023-04-03",
            },
            "quoter": {
                "address": "0x678Aa4bF4E210cf2166753e054d5b7c31cc7fa86",
                "block_number_of_deployment": 27459800,
                "date_of_deployment": "2023-04-03",
            },
            "quoterv2": {
                "address": "0xB048Bbc1Ee6b733FFfCFb9e9CeF7375518e25997",
                "block_number_of_deployment": 27459800,
                "date_of_deployment": "2023-04-03",
            },
            "swapRouter": {
                "address": "0x1b81D678ffb9C0263b24A97847620C99d213eB14",
                "block_number_of_deployment": 27459800,
                "date_of_deployment": "2023-04-03",
            },
            "swapRouter02": {
                "address": "0x13f4EA83D0bd40E75C8222255bc855a974568Dd4",
                "block_number_of_deployment": 27459800,
                "date_of_deployment": "2023-04-03",
            },
        },
    },
    "poly": {
        "tokens": {
            "wrapped_native_token": {
                "name": "Wrapped Matic",
                "symbol": "WPOL",
                "decimals": 18,
                "address": "0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270",
                "block_number_of_deployment": 4931456,  # approx
                "date_of_deployment": "2020-09-25",
            },
            "USDT": {
                "name": "Tether USD",
                "symbol": "USDT",
                "decimals": 6,
                "address": "0xc2132D05D31c914a87C6611C10748AEb04B58e8F",
                "block_number_of_deployment": 4196335,
                "date_of_deployment": "2020-09-07",
            },
            "USDC": {
                "name": "USD Coin",
                "symbol": "USDC",
                "decimals": 6,
                "address": "0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359",
                "block_number_of_deployment": 45319261,
                "date_of_deployment": "2023-07-20",
            },
            "DAI": {
                "name": "Dai Stablecoin",
                "symbol": "DAI",
                "decimals": 18,
                "address": "0x8f3Cf7ad23Cd3CaDbD9735AFf958023239c6A063",
                "block_number_of_deployment": 4362007,
                "date_of_deployment": "2020-09-11",
            },
            "WBTC": {
                "name": "Wrapped BTC",
                "symbol": "WBTC",
                "decimals": 8,
                "address": "0x1BFD67037B42Cf73acF2047067bd4F2C47D9BfD6",
                "block_number_of_deployment": 4196820,
                "date_of_deployment": "2020-09-07",
            },
        },
        "uniswap_v2": {
            "factory": {
                "address": "0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32",  # QuickSwap
                "block_number_of_deployment": 4931780,
                "date_of_deployment": "2020-09-25",
            },
            "router02": {
                "address": "0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff",
                "block_number_of_deployment": 4931900,
                "date_of_deployment": "2020-09-25",
            },
        },
        "uniswap_v3": {
            "factory": {
                "address": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
                "block_number_of_deployment": 22757547,
                "date_of_deployment": "2021-12-20",
            },
            "quoter": {
                "address": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
                "block_number_of_deployment": 22760561,  # Estimated
                "date_of_deployment": "2021-12-20",
            },
            "quoterv2": {
                "address": "0x61fFE014bA17989E743c5F6cB21bF9697530B21e",
                "block_number_of_deployment": 22760828,
                "date_of_deployment": "2021-12-20",
            },
            "swapRouter": {
                "address": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
                "block_number_of_deployment": 22760566,  # Estimated
                "date_of_deployment": "2021-12-20",
            },
            "swapRouter02": {
                "address": "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45",
                "block_number_of_deployment": 22760566,
                "date_of_deployment": "2021-12-20",
            },
        },
        "sushiswap_v2": {
            "factory": {
                "address": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4",
                "block_number_of_deployment": 11333218,
                "date_of_deployment": "2021-02-26",
            },
            "router02": {
                "address": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
                "block_number_of_deployment": 11333235,
                "date_of_deployment": "2021-02-26",
            },
        },
        "sushiswap_v3": {
            "factory": None,
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
        "pancakeswap_v2": {"factory": None, "router02": None},
        "pancakeswap_v3": {
            "factory": None,
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
    },
    "base": {
        "tokens": {
            "wrapped_native_token": {
                "name": "Wrapped Ether",
                "symbol": "WETH",
                "decimals": 18,
                "address": "0x4200000000000000000000000000000000000006",
                "block_number_of_deployment": 0,  # pre-deployed at genesis
                "date_of_deployment": "2023-08-09",
            },
            "USDT": {
                "name": "Bridged Tether USD",
                "symbol": "USDT",
                "decimals": 6,
                "address": "0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2",
                "block_number_of_deployment": 12044917,  # approx
                "date_of_deployment": "2024-03-19",
            },
            "USDC": {
                "name": "USD Coin",
                "symbol": "USDC",
                "decimals": 6,
                "address": "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
                "block_number_of_deployment": 2797221,
                "date_of_deployment": "2023-08-18",
            },
            "DAI": {
                "name": "Bridged Dai Stablecoin",
                "symbol": "DAI",
                "decimals": 18,
                "address": "0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb",
                "block_number_of_deployment": 1569598,
                "date_of_deployment": "2023-07-21",
            },
            "WBTC": {
                "name": "Bridged Wrapped BTC",
                "symbol": "WBTC",
                "decimals": 8,
                "address": "0x0555E30da8f98308EdB960aa94C0Db47230d2B9c",
                "block_number_of_deployment": 19979002,
                "date_of_deployment": "2023-09-19",
            },
        },
        # this is actually aerodrome_v2
        "uniswap_v2": {
            "factory": {
                "address": "0x420DD381b31aEf6683db6B902084cB0FFECe40Da",
                "block_number_of_deployment": 3200559,  # Estimated
                "date_of_deployment": "2023-11-14",
            },
            "router02": {
                "address": "0xcF77a3Ba9A5CA399B7c97c74d54e5b1Beb874E43",
                "block_number_of_deployment": 3200613,  # Estimated
                "date_of_deployment": "2024-02-08",
            },
        },
        # this is uniswap v3
        "uniswap_v3": {
            "factory": {
                "address": "0x33128a8fC17869897dcE68Ed026d694621f6FDfD",
                "block_number_of_deployment": 1371680,
                "date_of_deployment": "2023-07-16",
            },
            "quoter": None,
            "quoterv2": {
                "address": "0x3d4e44Eb1374240CE5F1B871ab261CD16335B76a",
                "block_number_of_deployment": 1371734,
                "date_of_deployment": "2023-07-16",
            },
            "swapRouter": None,
            "swapRouter02": {
                "address": "0x2626664c2603336E57B271c5C0b26F421741e481",
                "block_number_of_deployment": 1371947,
                "date_of_deployment": "2023-07-16",
            },
        },
        "pancakeswap_v2": {"factory": None, "router02": None},
        "pancakeswap_v3": {
            "factory": {
                "address": "0x0BFbCF9fa4f9C56B0F40a671Ad40E0805A091865",
                "block_number_of_deployment": 2912007,  # Needs verification
                "date_of_deployment": "2023-08-21",
            },
            "quoter": None,  # Needs verification
            "quoterv2": {
                "address": "0xB048Bbc1Ee6b733FFfCFb9e9CeF7375518e25997",
                "block_number_of_deployment": 2912518,  # Needs verification
                "date_of_deployment": "2023-08-21",
            },
            "swapRouter": {
                "address": "0x1b81d678ffb9c0263b24a97847620c99d213eb14",  # Swap Router V3
                "block_number_of_deployment": 2912484,
                "date_of_deployment": "2023-08-21",
            },
            "swapRouter02": {
                "address": "0x678aa4bf4e210cf2166753e054d5b7c31cc7fa86",  # Smart Router
                "block_number_of_deployment": 2913124,
                "date_of_deployment": "2023-08-21",
            },
        },
    },
    "arbi": {
        "tokens": {
            "wrapped_native_token": {
                "name": "Wrapped Ether",
                "symbol": "WETH",
                "decimals": 18,
                "address": "0x82aF49447D8a07e3bd95BD0d56f35241523fBab1",
                "block_number_of_deployment": 55,  # Genesis deployment
                "date_of_deployment": "2021-08-31",
            },
            "USDT": {
                "name": "Tether USD",
                "symbol": "USDT",
                "decimals": 6,
                "address": "0xFd086bC7CD5C481DCC9C85ebE478A1C0b69FCbb9",
                "block_number_of_deployment": 228105,
                "date_of_deployment": "2021-08-30",
            },
            "USDe": {
                "name": "Ethena USDe",
                "symbol": "USDe",
                "decimals": 18,
                "address": "0x5d3a1Ff2b6BAb83b63cd9AD0787074081a52ef34",
                "block_number_of_deployment": 189133001,
                "date_of_deployment": "2024-03-10",
            },
            "USDC": {
                "name": "USD Coin",
                "symbol": "USDC",
                "decimals": 6,
                "address": "0xaf88d065e77c8cC2239327C5EDb3A432268e5831",  # Native USDC
                "block_number_of_deployment": 34266938,  # Estimated
                "date_of_deployment": "2022-10-08",
            },
            "DAI": {
                "name": "Dai Stablecoin",
                "symbol": "DAI",
                "decimals": 18,
                "address": "0xDA10009cBd5D07dd0CeCc66161FC93D7c9000da1",
                "block_number_of_deployment": 1336824,
                "date_of_deployment": "2021-08-31",
            },
            "WBTC": {
                "name": "Wrapped BTC",
                "symbol": "WBTC",
                "decimals": 8,
                "address": "0x2f2a2543B76A4166549F7aaB2e75Bef0aefC5B0f",
                "block_number_of_deployment": 2591,
                "date_of_deployment": "2021-09-01",
            },
        },
        "uniswap_v2": {
            "factory": {
                "address": "0xf1D7CC64Fb4452F05c498126312eBE29f30Fbcf9",  # Official Uniswap V2
                "block_number_of_deployment": 150442611,  # Needs verification
                "date_of_deployment": "2023-11-14",  # Approximate
            },
            "router02": {
                "address": "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24",  # Official Uniswap V2
                "block_number_of_deployment": 176188790,
                "date_of_deployment": "2023-01-14",  # Approximate
            },
        },
        "uniswap_v3": {
            "factory": {
                "address": "0x1F98431c8aD98523631AE4a59f267346ea31F984",
                "block_number_of_deployment": 288,
                "date_of_deployment": "2021-08-31",
            },
            "quoter": {
                "address": "0xb27308f9F90D607463bb33eA1BeBb41C27CE5AB6",
                "block_number_of_deployment": 288,
                "date_of_deployment": "2021-08-31",
            },
            "quoterv2": {
                "address": "0x61fFE014bA17989E743c5F6cB21bF9697530B21e",
                "block_number_of_deployment": 3163143,
                "date_of_deployment": "2021-11-17",
            },
            "swapRouter": {
                "address": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
                "block_number_of_deployment": 288,
                "date_of_deployment": "2021-08-31",
            },
            "swapRouter02": {
                "address": "0x68b3465833fb72A70ecDF485E0e4C7bD8665Fc45",
                "block_number_of_deployment": 4143800,  # Estimated
                "date_of_deployment": "2021-12-01",
            },
        },
        "sushiswap_v2": {
            "factory": {
                "address": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4",
                "block_number_of_deployment": 70,
                "date_of_deployment": "2021-08-31",
            },
            "router02": {
                "address": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
                "block_number_of_deployment": 73,
                "date_of_deployment": "2021-08-31",
            },
        },
        "sushiswap_v3": {
            "factory": None,  # Limited deployment
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
        "pancakeswap_v2": {
            "factory": None,  # Not deployed on Arbitrum
            "router02": None,
        },
        "pancakeswap_v3": {
            "factory": None,  # Limited presence
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
    },
    "avax": {
        "tokens": {
            "wrapped_native_token": {
                "name": "Wrapped AVAX",
                "symbol": "WAVAX",
                "decimals": 18,
                "address": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",
                "block_number_of_deployment": 820,  # Early deployment
                "date_of_deployment": "2021-02-01",
            },
            "USDT": {
                "name": "Tether USD",
                "symbol": "USDT.e",
                "decimals": 6,
                "address": "0xc7198437980c041c805A1EDcbA50c1Ce5db95118",
                "block_number_of_deployment": 2749893,
                "date_of_deployment": "2021-02-10",
            },
            "USDC": {
                "name": "USD Coin",
                "symbol": "USDC",
                "decimals": 6,
                "address": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E",  # Native USDC
                "block_number_of_deployment": 7388829,  # Estimated
                "date_of_deployment": "2021-12-14",
            },
            "DAI": {
                "name": "Dai Stablecoin",
                "symbol": "DAI.e",
                "decimals": 18,
                "address": "0xd586E7F844cEa2F87f50152665BCbc2C279D8d70",
                "block_number_of_deployment": 2749892,
                "date_of_deployment": "2021-02-10",
            },
            "WBTC": {
                "name": "Wrapped BTC",
                "symbol": "WBTC.e",
                "decimals": 8,
                "address": "0x50b7545627a5162F82A992c33b87aDc75187B218",
                "block_number_of_deployment": 2749888,
                "date_of_deployment": "2021-02-10",
            },
        },
        "uniswap_v2": {
            "factory": {
                "address": "0x9e5A52f57b3038F1B8EeE45F28b3C1967e22799C",
                "block_number_of_deployment": 37767795,
                "date_of_deployment": "2023-11-01",  # Estimated
            },
            "router02": {
                "address": "0x4752ba5dbc23f44d87826276bf6fd6b1c372ad24",
                "block_number_of_deployment": 41419282,
                "date_of_deployment": "2023-11-01",  # Estimated
            },
        },
        "uniswap_v3": {
            "factory": {
                "address": "0x740b1c1de25031C31FF4fC9A62f554A55cdC1baD",
                "block_number_of_deployment": 27832972,  # Estimated
                "date_of_deployment": "2024-03-01",
            },
            "quoter": None,  # Uses QuoterV2
            "quoterv2": {
                "address": "0xbe0F5544EC67e9B3b2D979aaA43f18Fd87E6257F",
                "block_number_of_deployment": 27833097,  # Estimated
                "date_of_deployment": "2024-03-01",
            },
            "swapRouter": None,  # Uses SwapRouter02
            "swapRouter02": {
                "address": "0xbb00FF08d01D300023C629E8fFfFcb65A5a578cE",
                "block_number_of_deployment": 27833102,  # Estimated
                "date_of_deployment": "2024-03-01",
            },
        },
        "sushiswap_v2": {
            "factory": {
                "address": "0xc35DADB65012eC5796536bD9864eD8773aBc74C4",
                "block_number_of_deployment": 506190,
                "date_of_deployment": "2021-03-16",
            },
            "router02": {
                "address": "0x1b02dA8Cb0d097eB8D57A175b88c7D8b47997506",
                "block_number_of_deployment": 506236,
                "date_of_deployment": "2021-03-16",
            },
        },
        "sushiswap_v3": {
            "factory": None,  # Limited deployment
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
        "pancakeswap_v2": {
            "factory": None,  # Not deployed on Avalanche
            "router02": None,
        },
        "pancakeswap_v3": {
            "factory": None,  # Not deployed on Avalanche
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
    },
    "sonic": {
        "tokens": {
            "wrapped_native_token": {
                "name": "Wrapped Sonic",
                "symbol": "wS",
                "decimals": 18,
                "address": "0x039e2fB66102314Ce7b64Ce5Ce3E5183bc94aD38",
                "block_number_of_deployment": 275872,
                "date_of_deployment": "2024-12-10",
            },
            "WETH": {
                "name": "Wrapped Ethereum",
                "symbol": "WETH",
                "decimals": 18,
                "address": "0x50c42dEAcD8Fc9773493ED674b675bE577f2634b",
                "block_number_of_deployment": 903657,
                "date_of_deployment": "2024-12-20",
            },
            "USDT": {
                "name": "Tether USD (Bridged)",
                "symbol": "USDT",
                "decimals": 6,
                "address": "0x6047828dc181963ba44974801ff68e538da5eaf9",
                "block_number_of_deployment": 3754024,
                "date_of_deployment": "2025-01-13",
                "note": "Bridged version via official bridge",
            },
            "USDC": {
                "name": "USD Coin",
                "symbol": "USDC",
                "decimals": 6,
                "address": "0x29219dd400f2bf60E5a23d13Be72B486D4038894",
                "block_number_of_deployment": 519841,
                "date_of_deployment": "2024-12-17",
                "note": "Native USDC with CCTP V2 support (upgraded May 2025)",
            },
            "DAI": {
                "name": "Dai Stablecoin",
                "symbol": "DAI",
                "decimals": None,
                "address": None,
                "block_number_of_deployment": None,
                "date_of_deployment": None,
                "note": "DAI is not available on Sonic mainnet",
            },
            "WBTC": {
                "name": "Wrapped BTC",
                "symbol": "WBTC",
                "decimals": 8,
                "address": "0x0555e30da8f98308edb960aa94c0db47230d2b9c",
                "block_number_of_deployment": 6929828,
                "date_of_deployment": "2025-02-07",
                "note": "LayerZero OFT implementation",
            },
        },
        "shadow_exchange_v2": {
            "factory": {
                "address": "0x2dA25E7446A70D7be65fd4c053948BEcAA6374c8",
                "block_number_of_deployment": 4028276,
                "date_of_deployment": "2025-01-15",  # Estimated
            },
            "router02": {
                "address": "0x1D368773735ee1E678950B7A97bcA2CafB330CDc",
                "block_number_of_deployment": 4037824,
                "date_of_deployment": "2025-01-15",  # Estimated
            },
        },
        "shadow_exchange_v3": {
            "factory": {
                "address": "0xcD2d0637c94fe77C2896BbCBB174cefFb08DE6d7",
                "block_number_of_deployment": 1705781,
                "date_of_deployment": "2024-12-27",
            },
            "quoter": None,  # Uses QuoterV2
            "quoterv2": {
                "address": "0x219b7ADebc0935a3eC889a148c6924D51A07535A",
                "block_number_of_deployment": 1706403,
                "date_of_deployment": "2024-12-27",
            },
            "swapRouter": {
                "address": "0x5543c6176feb9b4b179078205d7c29eea2e2d695",
                "block_number_of_deployment": 1706403,
                "date_of_deployment": "2024-12-27",
            },
            "swapRouter02": {
                "address": "0x92643Dc4F75C374b689774160CDea09A0704a9c2",
                "block_number_of_deployment": 4044928,
                "date_of_deployment": "2025-01-15",
            },
        },
        "uniswap_v2": {
            "factory": None,
            "router02": None,
        },
        "uniswap_v3": {
            "factory": None,
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
        "sushiswap_v2": {
            "factory": None,
            "router02": None,
        },
        "sushiswap_v3": {
            "factory": None,  # Limited deployment
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
        "pancakeswap_v2": {
            "factory": None,  # Not deployed on Avalanche
            "router02": None,
        },
        "pancakeswap_v3": {
            "factory": None,  # Not deployed on Avalanche
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
    },
    "goat": {
        "tokens": {
            "wrapped_native_token": {
                "name": "Wrapped Goat Bitcoin",
                "symbol": "WGBTC",
                "decimals": 18,
                "address": "0xbC10000000000000000000000000000000000000",
                "block_number_of_deployment": 0,  # pre-deployed at genesis
                "date_of_deployment": "2023-08-09",
            },
            "USDT": {
                "name": "Bridged Tether USD",
                "symbol": "USDT",
                "decimals": 6,
                "address": "0xE1AD845D93853fff44990aE0DcecD8575293681e",
                "block_number_of_deployment": 1318696,  # approx
                "date_of_deployment": "2024-03-19",
            },
            "USDC": {
                "name": "USD Coin",
                "symbol": "USDC",
                "decimals": 6,
                "address": "0x3022b87ac063DE95b1570F46f5e470F8B53112D8",
                "block_number_of_deployment": 1318696,
                "date_of_deployment": "2023-08-18",
            },
            "DAI": {
                "name": "Bridged Dai Stablecoin",
                "symbol": "DAI",
                "decimals": 18,
                "address": None,
                "block_number_of_deployment": None,
                "date_of_deployment": None,
            },
            "ArtBTC": {
                "name": "Bridged Wrapped BTC",
                "symbol": "ArtBTC",
                "decimals": 18,
                "address": "0x02F294cC9Ceb2c80FbA3fD779e17FE191Cc360C4",
                "block_number_of_deployment": 1318696,
                "date_of_deployment": "2023-09-19",
            },
            "DOGEB": {
                "name": "Goat BSC DOGE",
                "symbol": "DOGEB",
                "decimals": 18,
                "address": "0x1E0d0303a8c4aD428953f5ACB1477dB42bb838cf",
                "block_number_of_deployment": 1318696,
                "date_of_deployment": "2023-09-19",
            },
        },
        "goatswap_v2": {
            "factory": {
                "address": "0xbF8c8B5D27e76890416eA95a50d4732BB4906741",
                "block_number_of_deployment": 0,  # Estimated
                "date_of_deployment": "2023-11-14",
            },
            "router02": {
                "address": "0xc6189404eACa8a96A9B26eCc6c892568f55deD9E",
                "block_number_of_deployment": 0,  # Estimated
                "date_of_deployment": "2024-02-08",
            },
        },
        "goatswap_v3": {
            "factory": {
                "address": "0x3D9c7F529005017aFD0a7fc2CF97D0baF72C5418",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2021-05-05",
            },
            "quoter": {
                "address": "0x460FF2839822f354fEf1f568f2379CA22c54B3f7",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2021-05-05",
            },
            "quoterv2": {
                "address": "0xa58536246beEB4E68C84caFFC07C87aB5F9f7A16",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2021-10-01",
            },
            "swapRouter": {
                "address": "0xE592427A0AEce92De3Edee1F18E0157C05861564",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2021-05-05",
            },
            "swapRouter02": {
                "address": "0x0d230A6A3E49301F0Ef9663982a529412EAAFAf4",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2021-12-01",
            },
        },
        "uniswap_v2": {"factory": None, "router02": None},
        "uniswap_v3": {
            "factory": {
                "address": "0xcb2436774C3e191c85056d248EF4260ce5f27A9D",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2021-05-05",
            },
            "quoter": None,
            "quoterv2": {
                "address": "0x5911cB3633e764939edc2d92b7e1ad375Bb57649",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2021-10-01",
            },
            "swapRouter": None,
            "swapRouter02": {
                "address": "0xaa52bB8110fE38D0d2d2AF0B85C3A3eE622CA455",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2021-12-01",
            },
        },
        "pancakeswap_v2": {"factory": None, "router02": None},
        "pancakeswap_v3": {
            "factory": None,  # Not deployed on GOAT Network
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
    },
    "pulsechain": {
        "tokens": {
            "wrapped_native_token": {
                "name": "Wrapped PLS",
                "symbol": "WPLS",
                "decimals": 18,
                "address": "0xA1077a294dDE1B09bB078844df40758a5D0f9a27",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2020-09-03",
            },
            "WETH": {
                "name": "Wrapped ETH",
                "symbol": "WETH",
                "decimals": 18,
                "address": "0x02DcdD04e3F455D838cd1249292C58f3B79e3C3C",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2020-09-03",
            },
            "USDC": {
                "name": "USD Coin",
                "symbol": "USDC",
                "decimals": 18,
                "address": "0x15D38573d2feeb82e7ad5187aB8c1D52810B1f07",
                "block_number_of_deployment": 7453840,
                "date_of_deployment": "2021-05-13",
            },
            "DAI": {
                "name": "Binance-Peg Dai Token",
                "symbol": "DAI",
                "decimals": 18,
                "address": "0xefD766cCb38EaF1dfd701853BFCe31359239F305",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2020-09-09",
            },
            "INC": {
                "name": "Incentive",
                "symbol": "INC",
                "decimals": 18,
                "address": "0x2fa878Ab3F87CC1C9737Fc071108F904c0B0C95d",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2022-12-01",
            },
            "USDT": {
                "name": "USD Tether",
                "symbol": "USDT",
                "decimals": 18,
                "address": "0x0Cb6F5a34ad42ec934882A05265A7d5F59b51A2f",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2021-05-13",
            },
            "PLSX": {
                "name": "Pulse X",
                "symbol": "PLSX",
                "decimals": 18,
                "address": "0x95B303987A60C71504D99Aa1b13B4DA07b0790ab",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2021-05-13",
            },
        },
        "uniswap_v2": {
            "factory": {
                "address": "0x29eA7545DEf87022BAdc76323F373EA1e707C523",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2023-11-01",  # Estimated
            },
            "router02": {
                "address": "0x165C3410fC91EF562C50559f7d2289fEbed552d9",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2023-11-01",  # Estimated
            },
        },
        "uniswap_v3": {
            "factory": None,  # Not deployed on BSC
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
        "pulsex_v2": {
            "factory": {
                "address": "0x1715a3E4A142d8b698131108995174F37aEBA10D",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2023-05-14",
            },
            "router02": {
                "address": "0x98bf93ebf5c380C0e6Ae8e192A7e2AE08edAcc02",
                "block_number_of_deployment": 0,
                "date_of_deployment": "2023-05-14",
            },
        },
        "pulsex_v3": {
            "factory": None,  # Not deployed on BSC
            "quoter": None,
            "quoterv2": None,
            "swapRouter": None,
            "swapRouter02": None,
        },
    },
}

blockscout_endpoints = {
    "redstone": "https://explorer.redstone.xyz",
    "goat": "https://explorer.goat.network",
    "pulsechain": "https://api.scan.pulsechain.com",
}


def rpc_endpoints() -> dict[str, str]:
    """Archive-node RPC URLs per chain, read from `SCONE_RPC_<CHAIN>` env vars.

    anvil's `--fork-url` requires an archive node (full historical state), so
    free public endpoints generally won't work — use Alchemy/QuickNode/Infura
    archive tiers. Only the chains your problem set actually targets need to be
    set; missing chains will KeyError at setup_problem time.
    """
    out = {}
    for chain in chain_ids:
        url = os.environ.get(f"SCONE_RPC_{chain.upper()}")
        if url:
            out[chain] = url
    return out


chain_ids = {
    "mainnet": 1,
    "bsc": 56,
    "arbi": 42161,
    "optim": 10,
    "base": 8453,
    "poly": 137,
    "avax": 43114,
    "sepolia": 11155111,
    "sonic": 146,
    "redstone": 690,
    "goat": 2345,
    "pulsechain": 369,
}
