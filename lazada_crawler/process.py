import multiprocessing

from crawler import CommentCrawl


def crawl(url='https://www.lazada.vn/?spm=a2o4n.home.header.dhome.22f7e182U11eMP',
          n_cores=2):
    crawler = CommentCrawl()
    categories, urls = crawler.get_category_urls(url)
    step = int(len(categories) / n_cores)
    notifications = []

    for i in range(n_cores):
        notifications.append((categories[i * step: (i + 1) * step], urls[i * step: (i + 1) * step]))

    print(notifications)
    crawler.terminate()

    crawler = CommentCrawl()
    processes = multiprocessing.Pool(n_cores)
    processes.starmap(crawler.crawl_agent, notifications)

    pass


if __name__ == '__main__':
    crawl()
    pass
