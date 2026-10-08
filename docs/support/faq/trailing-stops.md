<!-- Source: https://hyperliquid.gitbook.io/hyperliquid-docs/support/faq/trailing-stops -->

> For the complete documentation index, see [llms.txt](https://hyperliquid.gitbook.io/hyperliquid-docs/llms.txt). Markdown versions of documentation pages are available by appending `.md` to page URLs; this page is available as [Markdown](trailing-stops.md).

# Trailing stops

### What is a trailing stop?

A trailing stop is typically used to reduce or close an existing position. Its trigger price follows the mark price as it moves in favor of the position. When the mark price reverses by the retracement you set, it triggers a market order to close the selected size.

### How does a trailing stop work?

A short trailing stop tracks the highest mark price reached since activation and triggers when the mark price falls from it by the set retracement. This closes a long or opens a short. A long trailing stop tracks the lowest mark price and triggers when the mark price rises from it by the set retracement. This closes a short or opens a long in the second.

* Activation price: Optional. Tracking begins when the mark price reaches this level or immediately if no activation price is set.
* Watermark: The highest mark price reached for a short trailing stop, or the lowest for a buy trailing stop, recorded since activation.
* Retracement: The reversal from the watermark required to trigger the order, set as a fixed price distance or a percentage.
* Trigger price: The price at which the order submits a market order for the selected size. It moves only when a new watermark is recorded, and stays unchanged during a reversal.

<table data-header-hidden><thead><tr><th width="189"></th><th></th><th></th><th></th></tr></thead><tbody><tr><td><strong>Order side</strong></td><td><strong>Watermark</strong></td><td><strong>Trigger</strong> <strong>price</strong> <strong>(distance)</strong></td><td><strong>Trigger price (percentage)</strong></td></tr><tr><td>Short (close long, open short)</td><td>Highest mark price</td><td>Watermark − distance</td><td>Watermark × (1 − rate)</td></tr><tr><td>Long (close short, open long)</td><td>Lowest mark price</td><td>Watermark + distance</td><td>Watermark × (1 + rate)</td></tr></tbody></table>

#### Example 1: Closing a long with a fixed distance

You have a long position, and the mark price is at 100. You place a trailing stop with a retracement of 10 and no activation price, intending to close the long once the market stops rising. The order begins tracking immediately from the current mark price. It follows the highest mark price reached, and triggers a market sell when the mark price falls from that high by 10.

<figure><img src="https://223971011-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2Fjea34cXPWRf1o1Lan56O%2Fuploads%2FkOHmqteIBfBugCzRKWRX%2Fclosing-long%20(3).png?alt=media&amp;token=be3cd3cc-1249-497d-bb81-1b7fdc307d3b" alt=""><figcaption></figcaption></figure>

| **Mark price** | **Highest mark** | **Trigger price** | **What happens**                            |
| -------------- | ---------------- | ----------------- | ------------------------------------------- |
| 100            | 100              | 90                | Tracking starts                             |
| 110            | 110              | 100               | New high raises the trigger                 |
| 105            | 110              | 100               | Trigger stays unchanged                     |
| 120            | 120              | 110               | New high raises the trigger again           |
| 110            | 120              | 110               | Market short is triggered to close the long |

#### Example 2: Closing a short with a percentage

You hold a short position and the mark price is at 120. You place a trailing stop with an activation price of 100 and a retracement of 10%, intending to close the short once the market stops falling. The order rests without tracking until the mark price reaches 100. From there it follows the lowest mark price reached, and triggers a market buy when the mark price rises from that low by 10%.

<figure><img src="https://223971011-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2Fjea34cXPWRf1o1Lan56O%2Fuploads%2FXPIk1C8AJxNPHdepUd1m%2Fclosing-short%20(3).png?alt=media&amp;token=0881919c-0988-401b-9dc9-389b2d68ac8f" alt=""><figcaption></figcaption></figure>

| **Mark price** | **Lowest mark** | **Trigger price** | **What happens**                            |
| -------------- | --------------- | ----------------- | ------------------------------------------- |
| 120            | -               | -                 | Waiting for activation                      |
| 100            | 100             | 110               | Tracking starts, no long is triggered       |
| 80             | 80              | 88                | New low lowers the trigger                  |
| 86             | 80              | 88                | Trigger stays unchanged                     |
| 88             | 80              | 80                | Market long is triggered to close the short |

#### Example 3: Opening a long with fixed-distance retracement

The mark price is at 120. You place a long trailing stop with an activation price of 100 and a retracement of 10, intending to open a long once the market stops falling. The order rests without tracking until the mark price reaches 100. From there it follows the lowest mark price reached, and triggers a market buy when the mark price rises from that low by 10.

<figure><img src="https://223971011-files.gitbook.io/~/files/v0/b/gitbook-x-prod.appspot.com/o/spaces%2Fjea34cXPWRf1o1Lan56O%2Fuploads%2FT6sZGLHHOjrOwhiNLonb%2Fopening-long-fixed-retracement%20(2).png?alt=media&amp;token=a0848f60-e7ce-4002-b85e-ae74855518c6" alt=""><figcaption></figcaption></figure>

| **Mark price** | **Lowest mark** | **Trigger price** | **What happens**                         |
| -------------- | --------------- | ----------------- | ---------------------------------------- |
| 120            | -               | -                 | Waiting for activation                   |
| 100            | 100             | 110               | Tracking starts, no buy is triggered     |
| 80             | 80              | 90                | New low lowers the trigger               |
| 88             | 80              | 90                | Trigger stays unchanged                  |
| 90             | 80              | 90                | Long is triggered and position is opened |
