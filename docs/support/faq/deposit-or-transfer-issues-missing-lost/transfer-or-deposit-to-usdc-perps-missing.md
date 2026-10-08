<!-- Source: https://hyperliquid.gitbook.io/hyperliquid-docs/support/faq/deposit-or-transfer-issues-missing-lost/transfer-or-deposit-to-usdc-perps-missing -->

> For the complete documentation index, see [llms.txt](https://hyperliquid.gitbook.io/hyperliquid-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](transfer-or-deposit-to-usdc-perps-missing.md).

# Transfer or deposit to USDC (Perps) missing

Description: You transferred USDC from your Spot to Perps balance or deposited USDC via Arbitrum and can’t figure out where it went or why you are not able to use the USDC in your Perps balance.

Situation 1: Transferred 1,000 from USDC (Spot) to USDC (Perps). When I checked, I see <1,000 USDC in my Available Balance. Where did it go?

Situation 2: Deposited 1,000 USDC from Arbitrum, and the deposit was successful. When I checked, I see <1,000 USDC in my Available Balance. Where did it go?

### Reasoning

* If you have open positions on cross margin with negative unrealized P\&L, your deposits and Spot to Perp transfers will go toward collateral for those open positions. Please refer to the Docs to understand how margining works: <../../../trading/margining.md#unrealized-pnl-and-transfer-margin-requirements>
