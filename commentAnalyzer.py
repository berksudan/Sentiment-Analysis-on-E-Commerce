import collections
import math
import operator
import os
import random
import re
import socket
import time
import urllib.request
import logging
from bs4 import BeautifulSoup as BSoup
import csv
import shutil
import matplotlib.pyplot as plot

############ GLOBAL VARIABLES ############
from numpy import mean

DIR_PATH = 'product_files//'
UNPROCESSED_COMMENTS_POSTFIX = '.comments_unprocessed.csv'
PROCESSED_COMMENTS_POSTFIX = '.comments_processed.csv'
LOG_DIR_PATH_POSTFIX = '.logs//'
PROD_IMG_POSTFIX = '.image.jpg'
PROD_INFO_POSTFIX = '.info.txt'
PROD_PLOT_POSTFIX = '.plot.png'
TOTAL_SENT_SCORE_POSTFIX = '.totalSentScore.txt'

##########################################

class UrlOperations:

    @staticmethod
    def check_hostname(url):
        parsed_url = UrlOperations.parse_url(url)
        DebugOp.print_debug('Parsed URL: ' + str(parsed_url))
        hostname = str(parsed_url[1])
        try:
            host = socket.gethostbyname(hostname)
            socket.create_connection((host, 80), 2)  # connect to the host & tell us if the host is reachable
            DebugOp.print_debug('Hostname is Reachable -> \"' + str(hostname) + "\"")
            return True
        except Exception as e:
            logging.basicConfig()
            logging.error('Failed.', exc_info=e)
            DebugOp.print_debug('Hostname is NOT Reachable')
            DebugOp.exit_program(-1, "No internet Connection")

    @staticmethod
    def parse_url(url):
        parsed_url = url.split("/")
        parsed_url.__delitem__(1)  # Convert ['http:','','www..'] to ['http:','www..']

        return parsed_url

    @staticmethod
    def compute_html_content(url):
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]  # Faking user
        response = opener.open(url)
        html_content = response.read().decode('utf-8')
        return str(html_content)

    @staticmethod
    def url_to_soup(a_url):
        return BSoup(UrlOperations.compute_html_content(a_url), 'lxml')


class Review:
    def __init__(self, comment, date, star_score):
        self.comment = comment
        self.date = self.change_date_format(date)
        self.star_score = star_score

    def print(self, review_num=1):
        DebugOp.print_stars()
        print("Review #" + str(review_num) + ":")
        print("\tComment: " + "<<" + self.comment[:45] + "...>>")
        print("\tDate: " + "<<" + str(self.date) + ">>")
        print("\tStar Score: " + "<<" + str(self.star_score) + ">>")

    def change_date_format(self, date):
        date = date.split(', ')

        month = date[0].split(' ')[0]
        month = self.month_to_num(month)
        day = date[0].split(' ')[1]
        if len(day) == 1:  # if it is like '7'
            day = '0' + day  # fill with zero, e.g. '07'
        year = date[1]

        return year + '-' + month + '-' + day

    @staticmethod
    def month_to_num(month_str):
        months = {
            'January': '01',
            'February': '02',
            'March': '03',
            'April': '04',
            'May': '05',
            'June': '06',
            'July': '07',
            'August': '08',
            'September': '09',
            'October': '10',
            'November': '11',
            'December': '12'
        }
        return months[month_str]


class Product:
    def __init__(self, prod_url):
        FileOp.open_dir('product_files')

        self.prod_url = prod_url
        self.reviews = []

        self.prod_id = self.collect_prod_id(prod_url)
        self.log_dirname = Logger.get_log_dirname(self.prod_id)

        url_soup = UrlOperations.url_to_soup(prod_url)
        self.prod_name = self.construct_product_name(url_soup)
        self.avg_star_score = self.collect_avg_star_score(url_soup)
        self.prod_img_url = self.collect_prod_img_url(url_soup)

        if self.avg_star_score == '0.0':  # There are no comments.
            self.total_comment_num = 0
            self.comment_page_url = ''
        else:  # There are some comments.
            self.total_comment_num = self.collect_total_comment_num(url_soup)
            self.comment_page_url = self.compute_comment_page_url(prod_url)

    def create_logger(self):
        Logger.create_log_directory(self.prod_id)

    @staticmethod
    def collect_prod_img_url(url_soup):
        image_tag = url_soup.find('div', id='imgTagWrapperId')
        return re.search('data-old-hires=\"(.*).jpg\"', str(image_tag)).group(1) + '.jpg'

    @staticmethod
    def collect_avg_star_score(url_soup):
        avg_star_score = url_soup.find('span', class_='arp-rating-out-of-text a-color-base')

        if str(avg_star_score) == 'None':
            return '0.0'
        return avg_star_score.text[:3]

    @staticmethod
    def collect_total_comment_num(url_soup):
        return re.search('See all (.*) reviews', str(url_soup)).group(1)

    def collect_prod_attrs(self):
        tmp_str = "PRODUCTION ID: " + self.prod_id + '\n\n'
        tmp_str += "PRODUCTION NAME: \n\t" + self.prod_name + '\n\n'
        tmp_str += 'AVERAGE STAR SCORE: ' + self.avg_star_score + '\n\n'
        tmp_str += 'TOTAL NUMBER OF COMMENTS : ' + self.total_comment_num + '\n\n'
        tmp_str += 'PRODUCTION URL: \n\t' + self.prod_url + '\n\n'
        tmp_str += 'PRODUCTION COMMENT PAGE URL: \n\t' + self.comment_page_url + '\n\n'
        tmp_str += 'PRODUCTION IMAGE URL: \n\t' + self.prod_img_url + '\n\n'
        return tmp_str

    def write_attrs_to_file(self):
        # Write product info to file
        prod_info_doc_name = self.prod_id + PROD_INFO_POSTFIX
        text_to_be_written = Logger.make_head_format('PRODUCTION ATTRIBUTES')
        text_to_be_written += self.collect_prod_attrs()
        print(text_to_be_written + '\n')
        f = open(DIR_PATH + prod_info_doc_name, "w+")
        f.write(text_to_be_written + '\n')
        f.close()

    def write_reviews_to_file(self):
        # Write product comments to file
        document_name = self.prod_id + UNPROCESSED_COMMENTS_POSTFIX
        f = open(DIR_PATH + document_name, "w+")
        f.write('# Comments,Production ID,Date,Star Score,# of Words in Comments,Comment Text\n')
        for i in range(len(self.reviews)):
            f.write(self.construct_review_row(i) + '\n')

        f.close()

    def write_prod_img_to_file(self):
        # Write product image to file
        document_name = self.prod_id + PROD_IMG_POSTFIX
        urllib.request.urlretrieve(self.prod_img_url, DIR_PATH + document_name)

    def print_reviews(self):

        DebugOp.print_debug('Reviews are printing:')

        print('# Comments,Production ID,Date,Star Score,# of Words in Comments,Comment Text\n')
        for i in range(len(self.reviews)):
            print(self.construct_review_row(i))

    def construct_review_row(self, i):  # Construct row of ith review
        tmp_str = str(i + 1) + ',' + self.prod_id + ','
        tmp_str += '\"' + str(self.reviews[i].date) + '\"' + ','
        tmp_str += str(self.reviews[i].star_score) + ','
        tmp_str += str(len(self.reviews[i].comment.split(' '))) + ','
        tmp_str += '\"' + self.reviews[i].comment + '\"'
        return tmp_str

    @staticmethod
    def collect_prod_id(prod_url):
        return 'B' + re.search('/B(.*)', prod_url).group(1)[:9]

    def compute_comment_url_page_n(self, n):
        p_url = UrlOperations.parse_url(self.comment_page_url)  # parsed url

        nth_comment_url_page = p_url[0] + "//" + p_url[1] + "/" + p_url[2] + "/" + p_url[
            3] + "/" + self.prod_id + '/ref=cm_cr_arp_d_paging_btm_' + str(
            n) + '?ie=UTF8&reviewerType=all_reviews&pageNumber=' + str(n)
        return nth_comment_url_page

    def     construct_time_plot(self):
        if os.path.exists(DIR_PATH + self.prod_id + PROD_PLOT_POSTFIX):
            os.remove(DIR_PATH + self.prod_id + PROD_PLOT_POSTFIX)

        csvfile = FileOp.load_csv(DIR_PATH + self.prod_id + UNPROCESSED_COMMENTS_POSTFIX)
        date_data = FileOp.get_values_of_caption(csvfile, 'Date')

        for i in range(len(date_data)):
            date_data[i] = date_data[i][:7]
        date_data = sorted(date_data)

        freq_date_data = sorted(list(collections.Counter(date_data).items()))

        dates = []
        num_comments = []

        for data in freq_date_data:
            dates.append(data[0])
            num_comments.append(data[1])

        plot.clf()
        plot.plot(dates, num_comments, color='red', marker='o')
        plot.xticks(dates, rotation='vertical')
        plot.subplots_adjust(bottom=0.15)
        plot.title('Dates vs Number of Comments', fontsize=14)
        plot.xlabel('Dates', fontsize=14)
        plot.ylabel('Number of Comment', fontsize=14)
        plot.savefig(DIR_PATH + self.prod_id + PROD_PLOT_POSTFIX)
    def construct_review_list(self, tries, delay_period, delay_secs):
        is_fetched = False
        if self.total_comment_num == 0:
            DebugOp.print_debug('There are no comments!')
            return

        try_count = 0
        while is_fetched is False and try_count < tries:
            self.reviews = []
            # noinspection PyBroadException
            try:
                DebugOp.print_debug("COMMENTS ARE BEING FETCHED:")
                num_com_page = self.calc_num_comment_page(UrlOperations.url_to_soup(self.comment_page_url))
                for cur_page in range(num_com_page):
                    a_comment_page_url = self.compute_comment_url_page_n(cur_page + 1)
                    # DebugOp.print_debug_debug("<<" + a_comment_page_url + ">>")

                    if (cur_page + 1) % delay_period == 0:  # Wait for a while
                        self.delay(delay_secs)

                    DebugOp.print_debug("Comment Page #%d is fetching.." % (cur_page + 1))
                    url_soup = UrlOperations.url_to_soup(a_comment_page_url)
                    user_cells = url_soup.findAll("div", attrs={"data-hook": "review"})
                    for i, user_cell in enumerate(user_cells, start=1):
                        comment = self.collect_comments(user_cell).replace('\"', '\'')
                        date = self.collect_dates(user_cell)
                        star = self.collect_star_score(user_cell)

                        review = Review(comment, date, star)
                        self.reviews.append(review)

                is_fetched = True
            except:
                try_count += 1
                DebugOp.print_debug('Error occurred in fetching operation.')
                if not try_count == tries:
                    DebugOp.print_debug('Retrying fetching... (%d.times)\n' % (try_count + 1))
                else:
                    DebugOp.print_debug('Fetching operation %d times tried, but failed.' % tries)
        if not is_fetched:
            DebugOp.exit_program(-1, 'Comments cannot retrieved.')
        else:
            DebugOp.print_debug("COMMENTS ARE FETCHED SUCCESSFULLY.")
            DebugOp.print_debug("THERE ARE " + str(len(self.reviews)) + " COMMENTS IN TOTAL.")

    @staticmethod
    def compute_comment_page_url(prod_url):
        parsed_prod_url = UrlOperations.parse_url(prod_url)

        url_soup = UrlOperations.url_to_soup(prod_url)
        url_addition = url_soup.find('a', attrs={"data-hook": "see-all-reviews-link-foot"}).attrs['href']

        return parsed_prod_url[0] + '//' + parsed_prod_url[1] + url_addition

    @staticmethod
    def calc_num_comment_page(url_soup):
        tmp = url_soup.find_all('li', class_='page-button')
        if str(tmp) == '[]':
            num_comment_page = 1
        else:
            num_comment_page = int(tmp[len(tmp) - 1].text)
        return num_comment_page

    @staticmethod
    def delay(delay_count):
        for i in range(delay_count):
            DebugOp.print_debug("Waiting for delay.. " + str(delay_count - i) + "s")
            time.sleep(1)

    @staticmethod
    def construct_product_name(soup):
        title_tag = soup.find('span', attrs={'id': 'productTitle'})
        title = title_tag.text
        title = title.replace('\n', '').replace('  ', '')
        return title

    @staticmethod
    def collect_comments(url_soup):
        comment_tag = url_soup.find('span', class_='a-size-base review-text')
        return comment_tag.text

    @staticmethod
    def collect_dates(url_soup):
        date = url_soup.find("span", class_="a-size-base a-color-secondary review-date")
        return date.text

    @staticmethod
    def collect_star_score(url_soup):
        return url_soup.find("span", class_="a-icon-alt").text[:1]


class FileOp:
    @staticmethod
    def open_dir(dir_name):
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        return dir_name

    @staticmethod
    def load_csv(file_name):
        f = open(file_name, 'r')
        lines = csv.reader(f)
        dataset = list(lines)
        for i in range(len(dataset)):
            dataset[i] = [str(x) for x in dataset[i]]
        f.close()
        return dataset

    @staticmethod
    def get_values_of_caption(data_set, caption_name):

        caption_index = -1
        for i in range(len(data_set[0])):
            if data_set[0][i] == caption_name:
                caption_index = i
        if caption_index == -1:
            DebugOp.exit_program(-1, 'No caption name: ' + caption_name)

        values = []
        for row in data_set:
            values.append(row[caption_index])
        values.__delitem__(0)
        return values


class DebugOp:

    @staticmethod
    def exit_program(exit_status, exit_msg=''):
        if exit_status == 0:
            print("\nProgram terminated successfully.")
        else:
            print("\nError occurred.")

        if exit_msg:
            print("Exit message: \"" + exit_msg + "\"")

        print("Exiting with code " + str(exit_status))
        exit(exit_status)

    @staticmethod
    def print_debug(msg):
        print("DEBUG MSG [%s]: %s\n" % (DebugOp.print_debug.Debug_Counter, msg))
        DebugOp.print_debug.Debug_Counter += 1

    @staticmethod
    def print_stars(count=54):
        for i in range(count):
            print('*', end='', flush=True)
        print('')  # new line


DebugOp.print_debug.Debug_Counter = 1  # type: int


class Logger:

    @staticmethod
    def create_log_directory(prod_id):
        log_dirname = Logger.get_log_dirname(prod_id)
        if os.path.exists(log_dirname):
            shutil.rmtree(log_dirname)
        os.makedirs(log_dirname)

    @staticmethod
    def get_log_dirname(prod_id):
        return DIR_PATH + prod_id + LOG_DIR_PATH_POSTFIX

    @staticmethod
    def print_and_log(log_text, log_file_name):
        print(log_text, end='')
        f_logger = open(log_file_name + '.txt', 'a+')
        f_logger.write(log_text)

        f_logger.close()

    @staticmethod
    def make_head_format(a_str):
        head_format = len(a_str)*'=' + 10*'=' + '\n'
        head_format += 5 * '=' + a_str + 5 * '=' + '\n'
        head_format += len(a_str)*'=' + 10*'=' + '\n'
        return head_format


class SentimentScorer:
    def __init__(self, prod_id):
        self.sentiment_scores = []
        self.document_prefix = DIR_PATH + prod_id
        self.comments = self.retrieve_comments()
        self.sentiment_dict = self.construct_dictionary()

        self.log_dirname = Logger.get_log_dirname(prod_id)

    def retrieve_comments(self):
        file_name = self.document_prefix + UNPROCESSED_COMMENTS_POSTFIX
        comment_caption = 'Comment Text'
        dataset = FileOp.load_csv(file_name)
        comments = FileOp.get_values_of_caption(dataset, comment_caption)
        print('Comments are retrieved')
        return comments

    def print_comments(self, log_filename='Comments'):
        i = 0
        log_text = Logger.make_head_format('COMMENTS:')

        for comment in self.comments:
            log_text += '\t%d. <<%s>>\n' % ((i + 1), comment)
            i += 1
        Logger.print_and_log(log_text, self.log_dirname + log_filename)

    @staticmethod
    def construct_dictionary():
        dict_dataset = dict()
        dict_file_name = 'dictionary_dataset.csv'

        list_dataset = FileOp.load_csv(dict_file_name)

        list_dataset.__delitem__(0)  # Delete Captions

        for row in list_dataset:  # List to dict format
            dict_dataset[row[0]] = row[1]

        return dict_dataset

    def preprocess_comments(self):
        regex = re.compile('[^a-zA-Z ]')

        for i in range(len(self.comments)):
            tmp = self.comments[i]

            tmp = regex.sub('', tmp)  # avoid special characters
            tmp = tmp.lower()  # avoid capital letters
            while tmp.count('  ') != 0:  # avoid double spaces
                tmp = tmp.replace('  ', ' ')

            self.comments[i] = tmp

    def calc_avg_sentiment_score(self, word_list, log_filename='SentimentScoreCalculation'):
        sum_scores = 0.0
        hit_count = 0.0
        log_text = ''

        for word in word_list:
            if self.sentiment_dict.__contains__(word):
                log_text += '\t%s -> %s\n' % (word, self.sentiment_dict.get(word))

                word_sentiment_score = float(self.sentiment_dict.get(word))
                sum_scores += word_sentiment_score
                hit_count += 1

        Logger.print_and_log(log_text, self.log_dirname + log_filename)
        if hit_count == 0:
            return 0.0
        else:
            return sum_scores / hit_count

    def score_comments(self, log_filename='SentimentScoreCalculation'):
        log_text = Logger.make_head_format('COMMENT SENTIMENT ANALYSIS')

        comment_count = 1
        for comment in self.comments:
            word_list = comment.split(' ')
            log_text += 'For Comment #%d:\n' % comment_count
            comment_count += 1
            Logger.print_and_log(log_text, self.log_dirname + log_filename)
            sentiment_score = self.calc_avg_sentiment_score(word_list)

            log_text = '\t====>> SENTIMENT SCORE: %s\n' % str(round(sentiment_score, 4))

            Logger.print_and_log(log_text, self.log_dirname + log_filename)
            log_text = ''
            self.sentiment_scores.append(sentiment_score)

    def write_sent_scores_to_file(self):
        unprocessed_file = open(self.document_prefix + UNPROCESSED_COMMENTS_POSTFIX, 'r')
        processed_file = open(self.document_prefix + PROCESSED_COMMENTS_POSTFIX, 'w+')

        is_first_line = True
        i = 0
        for line in unprocessed_file:
            # print('<<%s>>' % line) # Just for debug
            line = line.replace('\n', '')
            if is_first_line:
                line += ',' + 'Sentiment Score'
                is_first_line = False
            else:
                line += ',' + str(self.sentiment_scores[i])
                i += 1
            line += '\n'
            processed_file.write(line)
        unprocessed_file.close()
        processed_file.close()
        # ***************************************************************************

    def write_avg_sent_score_to_file(self):
        total_sent_score_file = open(self.document_prefix + TOTAL_SENT_SCORE_POSTFIX, 'w+')
        avg_sentiment_score = mean(self.sentiment_scores)


        tmp_str = 'TOTAL SENTIMENT SCORE: %.4f  in range [-1,1]\n' % avg_sentiment_score
        tmp_str += 'TOTAL SENTIMENT POLARITY: '
        if avg_sentiment_score < 0:
            tmp_str += 'Negative\n'
        else:
            tmp_str += 'Positive\n'

        total_sent_score_file.write(tmp_str)
        total_sent_score_file.close()


class GuiConnections:
    def __init__(self):
        self.log_file_name = ''
        self.product_url = ''

    def set_log_file_name(self, log_file_name):
        self.log_file_name = log_file_name

    def get_log_file_name(self):
        return self.log_file_name

    def set_product_url(self, product_url):
        self.product_url = product_url


class KNNClustering:
    def __init__(self, prod_id):
        self.document_prefix = DIR_PATH + prod_id

        self.log_dirname = Logger.get_log_dirname(prod_id)

    @staticmethod
    def load_dataset(filename, split, training_set=None, test_set=None):
        if training_set is None:
            training_set = []
        if test_set is None:
            test_set = []

        csvfile = FileOp.load_csv(filename)
        col_1 = FileOp.get_values_of_caption(csvfile, 'Sentiment Score')
        col_2 = FileOp.get_values_of_caption(csvfile, '# of Words in Comments')
        col_3 = FileOp.get_values_of_caption(csvfile, 'Star Score')

        for i in range(len(col_3)):
            if col_3[i] == '4' or col_3[i] == '5':
                col_3[i] = 'pos'
            else:
                col_3[i] = 'neg'

        dataset = []
        for i in range(len(col_1)):
            dataset_row = []
            dataset_row.extend((col_1[i], col_2[i], col_3[i]))
            dataset.append(dataset_row)
        for x in range(len(dataset) - 1):
            for y in range(2):
                dataset[x][y] = float(dataset[x][y])
            if random.random() < split:
                training_set.append(dataset[x])
            else:
                test_set.append(dataset[x])

    @staticmethod
    def calc_euclidean_distance(instance1, instance2, length):
        distance = 0
        for x in range(length):
            distance += pow((instance1[x] - instance2[x]), 2)
        return math.sqrt(distance)

    def get_neighbors(self, training_set, test_instance, k):
        distances = []
        length = len(test_instance) - 1
        for x in range(len(training_set)):
            dist = self.calc_euclidean_distance(test_instance, training_set[x], length)
            distances.append((training_set[x], dist))
        distances.sort(key=operator.itemgetter(1))
        neighbors = []
        for x in range(k):
            neighbors.append(distances[x][0])
        return neighbors

    @staticmethod
    def get_response(neighbors):
        class_votes = {}
        for x in range(len(neighbors)):
            response = neighbors[x][-1]
            if response in class_votes:
                class_votes[response] += 1
            else:
                class_votes[response] = 1

        biggest_key = 0
        biggest_value = 0

        for key in class_votes:
            if class_votes.get(key) > biggest_value:
                biggest_key = key
                biggest_value = class_votes.get(key)

        return biggest_key

    @staticmethod
    def get_accuracy(test_set, predictions):
        correct = 0
        for x in range(len(test_set)):
            if test_set[x][-1] == predictions[x]:
                correct += 1
        return (correct / float(len(test_set))) * 100.0

    def calculate_knn(self, k=3, log_filename='KNearestNeighborsClustering'):
        log_text = Logger.make_head_format('KNN CLUSTERING for K = %d' % k)
        processed_file_name = self.document_prefix + PROCESSED_COMMENTS_POSTFIX
        # prepare data
        training_set = []
        test_set = []
        split = 0.67

        self.load_dataset(processed_file_name, split, training_set, test_set)
        log_text += '--> Size of Train set: %d\n' % len(training_set)
        log_text += '--> Size of Test set: %d\n' % len(test_set)
        # generate predictions
        predictions = []
        for i in range(len(test_set)):
            neighbors = self.get_neighbors(training_set, test_set[i], k)
            result = self.get_response(neighbors)
            predictions.append(result)
            log_text += '\tTest Instance #%d:\n' % (i + 1)

            log_text += '\t\t\tPredicted => \'%s\'\n' % result
            log_text += '\t\t\tActual    => \'%s\'\n' % test_set[i][-1]
        accuracy = self.get_accuracy(test_set, predictions)
        log_text += 'Accuracy: %.3f %%\n' % accuracy
        Logger.print_and_log(log_text, self.log_dirname + log_filename)


def main(gui_connection: GuiConnections):


    url = gui_connection.product_url

    UrlOperations.check_hostname(url)

    product = Product(url)
    product.create_logger()
    product.write_prod_img_to_file()

    product.construct_review_list(tries=3, delay_period=10, delay_secs=4)
    #
    product.write_attrs_to_file()
    product.write_reviews_to_file()
    product.construct_time_plot()

    ###########################################################
    prod_id = product.prod_id

    sentiment_scorer = SentimentScorer(prod_id)

    sentiment_scorer.preprocess_comments()
    sentiment_scorer.print_comments()

    sentiment_scorer.score_comments()
    sentiment_scorer.write_sent_scores_to_file()
    sentiment_scorer.write_avg_sent_score_to_file()

    ###########################################################

    knn_clustering = KNNClustering(prod_id)
    knn_clustering.calculate_knn(3)

    ##############################################################
    return gui_connection


if __name__ == "__main__":
    gui_connection = GuiConnections()
    ############## CANDIDATE URLs #############
    # 148 Comments # 'https://www.amazon.com/Goody-Ouchless-Bobby-Brown-48/dp/B00E9SP888/ref=sr_1_151?s=beauty-intl-ship&ie=UTF8&qid=1545516925&sr=1-151'
    # 38 Comment # 'https://www.amazon.com/Yunlep-Adjustable-Tactical-Military-Training/dp/B07LBKMCSV/ref=sr_1_12?s=pet-supplies&ie=UTF8&qid=1545521168&sr=1-12'
    # 31 Comment #'https://www.amazon.com/Miracliy-Decorations-Artificial-Decoration-Environments/dp/	/ref=sr_1_76?s=pet-supplies&ie=UTF8&qid=1545524140&sr=1-76'
    # 20 Comments # https://www.amazon.com/Sticker-Fheaven-Mandala-Stickers-Bedroom/dp/B071H38K22/
    ###########################################

    gui_connection.set_product_url(
        'https://www.amazon.com/Miracliy-Decorations-Artificial-Decoration-Environments/dp/B07KZ82F1R/ref=sr_1_76?s=pet-supplies&ie=UTF8&qid=1545524140&sr=1-76'
    )
    main(gui_connection)
    DebugOp.exit_program(0, "Successful.")
