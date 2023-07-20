import time, os
from multiprocessing import Process, current_process
from get_repos_mt import get_repos

years = ['2018', '2019', '2020']
months = [str(i).zfill(2) for i in range(1, 13)]
days = [str(i).zfill(2) for i in range(1, 32)]
pages = range(1, 30)

token1 = "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"
token2 = "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"
token3 = "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"
token4 = "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"
token5 = "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"
token6 = "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"
token7 = "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"
token8 = "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"
token9 = "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"
token10 = "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"
token11 = "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"
token12 = "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"

# p1 = Process(target=get_repos([2018], ['03'], ['01'], pages, token1))
p1 = Process(target=get_repos, args=(years[0:1], months[0:3], days, pages, token1,))
p2 = Process(target=get_repos, args=(years[0:1], months[3:6], days, pages, token2,))
p3 = Process(target=get_repos, args=(years[0:1], months[6:9], days, pages, token3,))
p4 = Process(target=get_repos, args=(years[0:1], months[9:12], days, pages, token4,))
p5 = Process(target=get_repos, args=(years[1:2], months[0:3], days, pages, token5,))
p6 = Process(target=get_repos, args=(years[1:2], months[3:6], days, pages, token6,))
p7 = Process(target=get_repos, args=(years[1:2], months[6:9], days, pages, token7,))
p8 = Process(target=get_repos, args=(years[1:2], months[9:12], days, pages, token8,))
p9 = Process(target=get_repos, args=(years[2:3], months[0:3], days, pages, token9,))
p10 = Process(target=get_repos, args=(years[2:3], months[3:6], days, pages, token10,))
p11 = Process(target=get_repos, args=(years[2:3], months[6:9], days, pages, token11,))
p12 = Process(target=get_repos, args=(years[2:3], months[9:12], days, pages, token12,))
p1.start()
p2.start()
p3.start()
p4.start()
p5.start()
p6.start()
p7.start()
p8.start()
p9.start()
p10.start()
p11.start()
p12.start()
p1.join()
p2.join()
p3.join()
p4.join()
p5.join()
p6.join()
p7.join()
p8.join()
p9.join()
p10.join()
p11.join()
p12.join()
