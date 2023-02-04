from math import log10

import matplotlib
import steamspypi

matplotlib.use('Agg')
import matplotlib.pyplot as plt


def get_mid_of_interval(interval_as_str):
    interval_as_str_formatted = [
        s.replace(',', '') for s in interval_as_str.split('..')
    ]
    lower_bound = float(interval_as_str_formatted[0])
    upper_bound = float(interval_as_str_formatted[1])
    mid_value = (lower_bound + upper_bound) / 2

    return mid_value


def get_x_y():
    steam_spy_dict = steamspypi.load()

    num_owners_list = []
    num_reviews_list = []

    for appID in steam_spy_dict:
        num_owners = steam_spy_dict[appID]['owners']
        try:
            num_owners = float(num_owners)
        except ValueError:
            num_owners = get_mid_of_interval(num_owners)
        num_reviews = sum(
            steam_spy_dict[appID][keyword] for keyword in ['positive', 'negative']
        )

        num_owners_list.append(num_owners)
        num_reviews_list.append(num_reviews)

    return num_owners_list, num_reviews_list


def get_log_list(vec):
    log_vec = [log10(1 + x) for x in vec]

    return log_vec


def main():
    (num_owners_list, num_reviews_list) = get_x_y()

    log_num_owners_list = get_log_list(num_owners_list)
    log_num_reviews_list = get_log_list(num_reviews_list)

    _, ax = plt.subplots()
    ax.scatter(log_num_owners_list, log_num_reviews_list)

    ax.set_xlabel('log(1+#owners)')
    ax.set_ylabel('log(1+#reviews)')

    xmax = 8
    ymax = 7

    num_ticks = 5
    plt.xticks(range(0, xmax, int(xmax / num_ticks)))
    plt.yticks(range(0, ymax, int(ymax / num_ticks)))

    plt.xlim(0, xmax)
    plt.ylim(0, ymax)

    plt.show()

    return True


if __name__ == '__main__':
    main()
