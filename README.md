# Correlation Between Market Sentiment and Stock Returns

This analysis investigates the relationship between sentiment and stock returns across multiple time windows. The aim is to assess whether sentiment signals influence stock price movements within different time horizons. 

The sentiment data is obtained from the comment of Stocktwits platfrom and sentiment scores are generated using VADER. Stock return data is obtained from yahoo finance. The sample includes major U.S. listed firms across multiple sectors, including technology (Apple, Microsoft, NVIDIA, AMD, Meta, Alphabet), financial services (JPMorgan Chase), energy (ExxonMobil), and consumer goods (Coca-Cola), as well as Tesla representing the electric vehicle industry. In addition, we include the Invesco QQQ Trust ETF as a proxy for the overall Nasdaq 100 market performance. Data taken are from 10 stocks and from 2024-12-31 to 2025-12-30, around 2500 rows.



There is no significant relationship between market sentiment and stock return across all the time windows. The regression results is shown in below table. All the p-value are larger than 0.1. Larger window reduces the sample size, it might also reduce the statistical power for explanation.

| Window (days) | Correlation | P-value | Sample Size |
| ------------- | ----------- | ------- | ----------- |
| 3             | -0.005      | 0.899   | 551         |
| 7             | 0.062       | 0.290   | 294         |
| 14            | 0.104       | 0.164   | 179         |
| 30            | -0.013      | 0.889   | 111         |
| 60            | 0.039       | 0.755   | 67          |
| 90            | 0.123       | 0.393   | 50          |


The correlation coefficient fluctuates between -0.005 and 0.123, the relationship between remains weak and there is no value exceeding 0.15 across all time windows. As time windows increase, the relationship become stronger, shown in the graph below. The significant level are unstable but larger than 0.05 across all time windows. 


<img width="1713" height="1137" alt="image" src="https://github.com/user-attachments/assets/cf329a27-526f-437d-9abf-29fed3d45a47" />

This finding suggests that sentiment may have a limited or indirect impact on stock prices in this sample.
