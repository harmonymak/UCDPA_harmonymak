import json
import urllib.request
from random import randint
import time
import os

# set up multiple user agents to prevent being blocked due to frequent calls
USER_AGENTS = [
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakese/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52"
    ]


def download_url(url, path, header):
    # url: download url
    # path: local save path
    # header: set user agent
    content = urllib.request.Request(url, headers=header)
    with urllib.request.urlopen(content) as file:
        with open(path, 'wb') as outfile:
            outfile.write(file.read())


def main():
    random_agent = USER_AGENTS[randint(0, len(USER_AGENTS)-1)]
    header = {'User-Agent': random_agent}

    # get country name corresponding to country code
    if not os.path.exists("./reporterAreas.json"):
        download_url("https://comtrade.un.org/Data/cache/reporterAreas.json", "./reporterAreas.json", header)
    with open('reporterAreas.json', 'r', encoding='utf_8_sig') as f:
        data = json.load(f)
    results = data.get("results")
    id = []  # store country code
    text = []  # store country name
    for i in results:
        id.append(i.get("id"))
        text.append(i.get("text"))
        new_id = id[1:]
        new_text = text[1:]
    start_year = 2017
    stop_year = 2019
    begin_id = 0  # number of docs downloaded in current year

    # create folder to store downloaded data
    if not os.path.exists("./data"):
        os.makedirs("./data")
    for year in range(start_year, stop_year + 1):
        # store data by year
        if not os.path.exists("./data/" + str(year)):
            os.makedirs("./data/" + str(year))

        for i in range(begin_id, len(new_id)):
            random_agent = USER_AGENTS[randint(0, len(USER_AGENTS)-1)]
            print(random_agent)
            header = {'User-Agent': random_agent}
            # parameters documented on https://comtrade.un.org/data/doc/api
            url = "http://comtrade.un.org/api/get?max=100000&r=" + str(new_id[i]) + "&freq=A&ps=" + str(year) + "&px=S3&rg=2&cc=AG1&fmt=csv&type=C"
            path = "./data/" + str(year) + "/" + new_text[i] + ".csv"
            print("Downloading from " + url + " to " + path)
            download_url(url, path, header)
            print("Done")
            # since guest users can only send 100 requests per hour, need to limit speed to prevent 409 error
            time.sleep(36)


if __name__ == '__main__':
    main()
