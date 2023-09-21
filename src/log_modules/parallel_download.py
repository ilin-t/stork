from multiprocessing import Process
from get_repos_mt_node import get_repos

years = ['2018', '2019', '2020', '2021', '2022', '2023']
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
token36 = "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"
token35 = "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"
token34 = "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"
token33 = "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"
token32 = "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"
token31 = "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"
token30 = "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"
token29 = "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"
token28 = "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"
token27 = "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"
token26 = "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"
token25 = "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"
token24 = "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"
token23 = "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"
token22 = "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"
token21 = "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"
token20 = "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"
token19 = "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"
token18 = "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"
token17 = "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"
token16 = "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"
token15 = "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"
token14 = "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"
token13 = "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"


# p1 = Process(target=get_repos([2018], ['03'], ['01'], pages, token1))
p1 = Process(target=get_repos, args=(years[0:1], months[0:2], days, pages, token1,))
p2 = Process(target=get_repos, args=(years[0:1], months[2:4], days, pages, token2,))
p3 = Process(target=get_repos, args=(years[0:1], months[4:6], days, pages, token3,))
p4 = Process(target=get_repos, args=(years[0:1], months[6:8], days, pages, token4,))
p5 = Process(target=get_repos, args=(years[0:1], months[8:10], days, pages, token5,))
p6 = Process(target=get_repos, args=(years[0:1], months[10:12], days, pages, token6,))
p7 = Process(target=get_repos, args=(years[1:2], months[0:2], days, pages, token7,))
p8 = Process(target=get_repos, args=(years[1:2], months[2:4], days, pages, token8,))
p9 = Process(target=get_repos, args=(years[1:2], months[4:6], days, pages, token9,))
p10 = Process(target=get_repos, args=(years[1:2],months[6:8], days, pages, token10,))
p11 = Process(target=get_repos, args=(years[1:2], months[8:10], days, pages, token11,))
p12 = Process(target=get_repos, args=(years[1:2], months[10:12], days, pages, token12,))
p13 = Process(target=get_repos, args=(years[2:3], months[0:2], days, pages, token13,))
p14 = Process(target=get_repos, args=(years[2:3], months[2:4], days, pages, token14,))
p15 = Process(target=get_repos, args=(years[2:3], months[4:6], days, pages, token15,))
p16 = Process(target=get_repos, args=(years[2:3], months[6:8], days, pages, token16,))
p17 = Process(target=get_repos, args=(years[2:3], months[8:10], days, pages, token17,))
p18 = Process(target=get_repos, args=(years[2:3], months[10:12], days, pages, token18,))
p19 = Process(target=get_repos, args=(years[3:4], months[0:2], days, pages, token19))
p20 = Process(target=get_repos, args=(years[3:4], months[2:4], days, pages, token20))
p21 = Process(target=get_repos, args=(years[3:4], months[4:6], days, pages, token21))
p22 = Process(target=get_repos, args=(years[3:4], months[6:8], days, pages, token22,))
p23 = Process(target=get_repos, args=(years[3:4], months[8:10], days, pages, token23))
p24 = Process(target=get_repos, args=(years[3:4], months[10:12], days, pages, token24))
p25 = Process(target=get_repos, args=(years[4:5], months[0:2], days, pages, token25))
p26 = Process(target=get_repos, args=(years[4:5], months[2:4], days, pages, token26,))
p27 = Process(target=get_repos, args=(years[4:5], months[4:6], days, pages, token27))
p28 = Process(target=get_repos, args=(years[4:5], months[6:8], days, pages, token28,))
p29 = Process(target=get_repos, args=(years[4:5], months[8:10],days, pages, token29,))
p30 = Process(target=get_repos, args=(years[4:5], months[10:12], days, pages, token30,))
p31 = Process(target=get_repos, args=(years[5:], months[0:2], days, pages, token31,))
p32 = Process(target=get_repos, args=(years[5:], months[2:4], days, pages, token32,))
p33 = Process(target=get_repos, args=(years[5:], months[4:6], days, pages, token33,))
p34 = Process(target=get_repos, args=(years[5:], months[6:8], days, pages, token34,))
p35 = Process(target=get_repos, args=(years[5:], months[8:10],days, pages, token35,))
p36 = Process(target=get_repos, args=(years[5:], months[10:12], days, pages, token36,))

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
p13.start()
p14.start()
p15.start()
p16.start()
p17.start()
p18.start()
p19.start()
p20.start()
p21.start()
p22.start()
p23.start()
p24.start()
p25.start()
p26.start()
p27.start()
p28.start()
p29.start()
p30.start()
p31.start()
p32.start()
p33.start()
p34.start()
p35.start()
p36.start()

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
p13.join()
p14.join()
p15.join()
p16.join()
p17.join()
p18.join()
p19.join()
p20.join()
p21.join()
p22.join()
p23.join()
p24.join()
p25.join()
p26.join()
p27.join()
p28.join()
p29.join()
p30.join()
p31.join()
p32.join()
p33.join()
p34.join()
p35.join()
p36.join()

# def generate_new_processes(num_processes, func, **kwargs):
#     processes = []
#     for i in range(1, num_processes + 1):
#         processes.append(Process(target=func, args=(kwargs,)))
#
#     return processes
#
#
# def start_processes(processes):
#     for process in processes:
#         process.start()
#
#
# def join_processes(processes):
#     for process in processes:
#         process.join()

#
# if __name__ == '__main__':
#     main()
    # OUTPUTS_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/outputs/"
    # REPOS_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/repositories-test/"
    # PACKAGES_ROOT = "/mnt/fs00/rabl/ilin.tolovski/stork/packages/"

    # years = ['2018', '2019', '2020']
    # months = [str(i).zfill(2) for i in range(1, 13)]
    # days = [str(i).zfill(2) for i in range(1, 32)]
    # pages = range(1, 30)
    # processes = []
    # for i in range(1, 13):
    #     processes.append(Process(target=generate_requirements, args=(REPOS_ROOT, PACKAGES_ROOT,
    #                                                                  OUTPUTS_ROOT, getTotalSize(REPOS_ROOT), i, 12,)))
    # start_processes(processes)
    # join_processes(processes)
