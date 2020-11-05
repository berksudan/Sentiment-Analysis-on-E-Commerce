# Sentiment Analysis on E-Commerce

## Abstract
A program has been developed to find the desired product on the Amazon E-Commerce site, collect comments, analyze the sentiments of the comments, and also analyze the sales times of the products.

## Motivation
Comments for the products on e-commerce websites indicate the reaction of the products directly. User feedbacks can be used in order to improve the quality of the products which will be put on the market in the future and also this information can be used to ensure absolute customer satisfaction. There may be up to thousands of comments for each product and may be thousands of products in a single e-commerce website. Therefore, it’s hard for companies to examine all comments and understand if people liked the products or not.

In this project, a program is implemented to retrieve the comments for hundreds of products, analyze them in various ways and extract the useful information out of these comments. Comments are reduced to several the keywords which are provided by a dictionary dataset. With the help of the sentimental analysis, we can understand which products have positive or negative influence on customers, results in the sale strategies being improved.

## Methodology
Python programming language is used for this project, since there are plenty of handy libraries in Python which can used for statistical analysis. Sentiment analysis is applied for analyzing the comments. Therefore, a dictionary consists of words (such as hate, like, love, bad, good, awful, etc.) is used. Each word in the dictionary has a sentiment score either -1 or 1. "1" represents the positive reaction while "-1" represents the negative reaction. Dictionary words are looked up in the comments and exact matches are considered only. Moreover, a web crawler is implemented in this project in order to find the products in a given e-commerce website and retrieve all comments for the product. In addition, the crawler retrieves the date of comments and uses this information in order to find out whether the amount of the product sales change over time in terms of years, months and days.

## Used Modules
- Python 3 as programming language
- NLP (Natural Language Processing) Techniques
- PyQT4 as GUI (Graphical User Interface)
- Beautiful Soup 4 as crawler
- Matplotlib as plotter

## Build
You can build the project by executing following bash file:

```bash
./build.sh
```

Build instructions are provided for Linux only, you can use the equivalent commands for other operating-systems.

## Run
After build, you can enter the following command in your Linux Terminal to run the program:

```bash
./run.sh
```

Note that, since this module does not use Amazon API to access the website, your client can be blocked by Amazon or the HTML tags in the website can be changed in time. 

## Screenshots of GUI Screens

- Screen of Entering Product ID
![Screen of Entering Product ID](./docs/enter_screen_product_id.png)

- Screen of Entering Product URL
![Screen of Entering Product URL](./docs/enter_screen_product_url.png)

- Screen of Sentiment Results
![Screen of Sentiment Results](./docs/product_sentiment_results_screen.png)

## Folder Structure
```bash
$ tree -L 2
.
├── build.sh
├── commentAnalyzer.py
├── design.py
├── design.ui
├── dictionary_dataset.csv
├── docs
│   ├── enter_screen_product_id.png
│   ├── enter_screen_product_url.png
│   └── product_sentiment_results_screen.png
├── gui_assets
│   ├── 1.jpg
│   ├── app_logo.png
│   └── text_browser_background.png
├── main.py
├── product_files
│   ├── B071H38K22.comments_processed.csv
│   ├── B071H38K22.comments_unprocessed.csv
│   ├── B071H38K22.image.jpg
│   ├── B071H38K22.info.txt
│   ├── B071H38K22.logs
│   ├── B071H38K22.plot.png
│   └── B071H38K22.totalSentScore.txt
├── README.md
└── run.sh

4 directories, 20 files
```

## Contributors
- *Berk Sudan*, [GitHub](https://github.com/berksudan), [LinkedIn](https://linkedin.com/in/berksudan/)

## References
-  The list of English positive and negative opinion words (in file ``dictionary_dataset.csv``) was compiled starting from the paper (Hu and Liu, KDD-2004), as stated in https://www.cs.uic.edu/~liub/FBS/sentiment-analysis.html#lexicon.
