<!-- Source: https://hyperliquid.gitbook.io/hyperliquid-docs/support/faq/manual-borrows -->

> For the complete documentation index, see [llms.txt](https://hyperliquid.gitbook.io/hyperliquid-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](manual-borrows.md).

# Manual borrows

### What are manual borrows?

Manual borrows allow you to borrow quote assets (USDC and USDT) against supplied collateral (HYPE and BTC).&#x20;

Manual borrowing is supported for Manual/Standard and Unified Account users. For portfolio margin (PM) accounts, borrowing is automated and the manual borrow action is disabled.

### How do manual borrows work?

#### Supported assets

| **Asset**   | **Use**                            | **LTV** |
| ----------- | ---------------------------------- | ------- |
| HYPE        | Supply as collateral               | 65%     |
| BTC         | Supply as collateral               | 50%     |
| USDC / USDT | Borrow, or supply to earn interest | N/A     |

Supplied HYPE and BTC act as collateral and do not earn interest. Supplied USDC and USDT earn interest but do not contribute to manual borrow capacity. Borrowed USDC and USDT pay interest.&#x20;

#### Loan-to-value (LTV) and borrowing

Each collateral asset has an LTV that determines how much you can borrow. `Borrowable amount = supplied amount × oracle price × LTV` If multiple collateral assets are supplied, their contributions are added together.&#x20;

Example, assuming USDC is worth $1:

| **Parameter**              | **Value**                |
| -------------------------- | ------------------------ |
| Collateral supplied        | 100 HYPE at $40          |
| LTV                        | 65%                      |
| Borrow capacity            | 100 × $40 × 65% = $2,600 |
| Outstanding borrow         | 2,000 USDC               |
| Additional borrowable USDC | 600 USDC                 |

#### APY calculations

Borrow APY is higher than supply APY because utilization is not 100%, i.e., interest paid by the set of borrowers need to be distributed proportionally to a larger set of suppliers, and the protocol retains 10% of borrowed interest as a buffer for future liquidations.&#x20;

### Understanding information related to manual borrows

#### Your Health Factor

Health Factor measures the account's LTV-weighted collateral value relative to its outstanding borrows. `Health Factor = supplied collateral value weighted by LTV / borrowed value × 100%`

In the example above, Health Factor is $2,600 / $2,000 × 100% = 130%.

At or below 100%, the account cannot borrow more. A Health Factor below 100% does not itself trigger liquidation.&#x20;

#### Interest and caps

Interest accrues continuously and is indexed hourly. Borrow APY depends on utilization. Refer to how interest works [here](../../trading/portfolio-margin.md#ltv-and-borrowing).

Borrows are subject to available liquidity and account and global caps. As such, a borrow may be limited even when the account has sufficient collateral. Refer to the current [supply and borrow limits](../../trading/portfolio-margin.md).

#### Liquidations

Partial borrow liquidation is triggered when the borrowed value exceeds the supplied collateral value weighted by the liquidation thresholds. For HYPE and BTC: `Liquidation threshold = (1 + LTV) / 2`

| **Collateral** | **LTV** | **Partial liquidation threshold** |
| -------------- | ------- | --------------------------------- |
| HYPE           | 65%     | 82.5%                             |
| BTC            | 50%     | 75%                               |

All supplied collateral and outstanding borrows are included. Collateral price declines, additional borrows, collateral withdrawals, and accrued interest can increase liquidation risk.

#### Liquidation price

Displays the estimated oracle price at the partial liquidation threshold. For a single collateral asset: `Liquidation price = borrowed value / (supplied amount × liquidation threshold)`

Example using 100 HYPE collateral and 2,000 USDC borrowed, assuming USDC remains at $1 and excluding additional interest:

| **Parameter**                 | **HYPE oracle price**           |
| ----------------------------- | ------------------------------- |
| Health Factor = 100%          | $2,000 / (100 × 65%) ≈ $30.77   |
| Partial liquidation threshold | $2,000 / (100 × 82.5%) ≈ $24.24 |

With multiple collateral assets, each estimate includes the other collateral's contribution at its liquidation threshold, holding all other asset prices fixed. The estimates do not assume that all collateral prices decline together.

Liquidation price changes with prices, balances, and interest. On-chain rounding may differ from the displayed estimate. PM accounts use a separate calculation. Refer to the [liquidation](../../trading/portfolio-margin.md#liquidations) Docs for more details.

#### Why is liquidation price shown as N/A?

N/A is displayed when no positive downside liquidation price is available. This can occur when:

* The asset is not supplied as collateral, or there are no outstanding borrows.
* Other collateral covers the debt even if this asset's price falls to zero, with other prices unchanged.
* The calculated liquidation price is above the current oracle price, meaning the account has already passed the threshold.

N/A does not indicate that the account is safe from liquidation risk. Users should also monitor outstanding borrows, supplied collateral, and Health Factor.
