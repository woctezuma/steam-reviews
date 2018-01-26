def replaceChineseISO(str):
    if str == 'zh-cn':
        str = 'zh'
    return str


def printLanguages(all_languages):
    import iso639

    print('## Language ISO 639-1')

    for language_iso in all_languages:
        language_name = iso639.to_name(replaceChineseISO(language_iso))
        print('* ' + replaceChineseISO(language_iso) + '\t   --->\t' + language_name)

    print()


def printRegionalRankings(all_languages, num_entries=20):
    import iso639

    for language_iso in all_languages:
        language_name = iso639.to_name(replaceChineseISO(language_iso))

        print('### Top ' + str(num_entries) + ' hidden gems for ' + language_name + ' speakers')

        filename = 'regional_rankings/hidden_gems_' + language_iso + '.md'

        with open(filename, 'r', encoding="utf8") as f:
            for i in range(num_entries):
                entry = f.readline().strip()
                print(entry)

        print()


def main():
    from analyze_language import loadAllLanguages

    language_filename = "list_all_languages.txt"
    all_languages = loadAllLanguages(language_filename)

    printLanguages(all_languages)

    num_entries = 20
    printRegionalRankings(all_languages, num_entries)


if __name__ == "__main__":
    main()
