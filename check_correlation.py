def getXY():
    from download_json import getTodaysSteamSpyData

    steam_spy_dict = getTodaysSteamSpyData()

    num_players_list = []
    num_reviews_list = []

    for appID in steam_spy_dict.keys():
        num_players = steam_spy_dict[appID]['players_forever']
        num_reviews = sum(steam_spy_dict[appID][keyword] for keyword in ['positive', 'negative'])

        num_players_list.append(num_players)
        num_reviews_list.append(num_reviews)

    return (num_players_list, num_reviews_list)


def getLogList(vec):
    from math import log10

    log_vec = [log10(1+x) for x in vec]

    return log_vec

def main():
    import matplotlib.pyplot as plt

    (num_players_list, num_reviews_list) = getXY()

    log_num_players_list = getLogList(num_players_list)
    log_num_reviews_list = getLogList(num_reviews_list)

    fig, ax = plt.subplots()
    ax.scatter(log_num_players_list, log_num_reviews_list)

    ax.set_xlabel('log(1+#players)')
    ax.set_ylabel('log(1+#reviews)')

    xmax = 8
    ymax = 7

    num_ticks = 5
    plt.xticks(range(0, xmax, int(xmax / num_ticks)))
    plt.yticks(range(0, ymax, int(ymax / num_ticks)))

    plt.xlim(0, xmax)
    plt.ylim(0, ymax)

    plt.show()


if __name__ == '__main__':
    main()
