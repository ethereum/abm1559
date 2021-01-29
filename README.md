Agent-based simulation environment for EIP 1559.

## Starting up

You can simply run the following commands in a terminal. If you prefer, use a virtual environment to install packages in a local folder.

```shell
git clone https://github.com/barnabemonnot/abm1559.git
cd abm1559

###
# Optional: use a virtual environment
python3 -m venv env
source env/bin/activate
###

pip install -r requirements.txt
jupyter lab
```

## Notebooks

### [Introduction to EIP 1559](/notebooks/eip1559.html)

We present a brief introduction to the rationale behind EIP 1559 as well as simulate the dynamics of the mechanism, including the basefee.

### [Stationary behaviour of EIP 1559](/notebooks/stationary1559.html)

A good benchmark case to test fee market proposals is stationary demand. In this notebook, we simulate random waves of new users who have value and costs all drawn from the same distribution. Users decide whether to transact or not based on their values and costs. We show that in this environment, the basefee always settles to a stationary level that depends on the congestion of the chain, i.e., how large the demand is.

### [Strategic users in EIP 1559](/notebooks/strategicUser.html)

Before reaching stationarity, or when demand varies rapidly, the market endures transitionary periods where either too many users or too few decide to transact. When there are too few, the basefee naturally decreases. But when there are too many, users have an incentive to increase their premiums during this transitionary period, until sufficiently many users are discouraged by the basefee level, at which point being strategic is no longer helpful. We investigate this dynamics and briefly compare the efficiency in both strategic and non-strategic cases.

### [The floating escalator: Combining 1559 and the escalator](/notebooks/floatingEscalator.html)

As shown by the previous notebook, strategic users in 1559 sometimes have the incentive to enter tip auctions when demand increases rapidly. The escalator is a proposal to automate in protocol the "transaction resubmission" pattern where a strategic user increases their bid over time until inclusion. Combined with 1559 to obtain a good default starting bid, the escalator could help users with various time preferences optimise their resubmission during demand shifts. In this introductory notebook, we present the behaviour of various user strategies and discuss their efficiency.

### [The stable road to EIP 1559: Transitioning out of first-price auctions](/notebooks/transition1559.html)

1559 will be introduced by a soft transition out of the legacy behaviour, with legacy transactions cast into 1559 format by setting their parameters from the declared gas price. This notebook investigates first the behaviour of legacy users in an environment where price references are provided by distributional oracles. We observe the inefficiencies of the legacy, first-price auction-based systems: sticky prices leading to overpayment and "bubbles" driven by high-value users. Meanwhile the introduction of the basefee and basefee-following users (explored in previous notebooks) "cools" the market, reducing the gap between transaction fees and true market-clearing price.
