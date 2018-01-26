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


def main():
    import matplotlib.pyplot as plt

    (num_players_list, num_reviews_list) = getXY()

    fig, ax = plt.subplots()
    ax.scatter(num_players_list, num_reviews_list)

    ax.set_xlabel('#players')
    ax.set_ylabel('#reviews')

    xmax = 2 * pow(10, 6)
    ymax = 2 * pow(10, 4)

    num_ticks = 4
    plt.xticks(range(0, xmax, int(xmax / num_ticks)))
    plt.yticks(range(0, ymax, int(ymax / num_ticks)))

    plt.xlim(0, xmax)
    plt.ylim(0, ymax)

    plt.show()


if __name__ == '__main__':
    main()
