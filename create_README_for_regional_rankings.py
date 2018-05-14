def replace_chinese_iso(text):
    if text == 'zh-cn':
        text = 'zh'
    return text


def print_languages(all_languages):
    import iso639

    print('## Language ISO 639-1')

    for language_iso in all_languages:
        language_name = iso639.to_name(replace_chinese_iso(language_iso))
        print('* ' + replace_chinese_iso(language_iso) + '\t   --->\t' + language_name)

    print()


def print_regional_rankings(all_languages, num_entries=20):
    import iso639

    for language_iso in all_languages:
        language_name = iso639.to_name(replace_chinese_iso(language_iso))

        print('### Top ' + str(num_entries) + ' hidden gems for ' + language_name + ' speakers')

        filename = 'regional_rankings/hidden_gems_' + language_iso + '.md'

        with open(filename, 'r', encoding="utf8") as f:
            for i in range(num_entries):
                entry = f.readline().strip()
                print(entry)

        print()


def main():
    from analyze_language import load_all_languages

    language_filename = "list_all_languages.txt"
    all_languages = load_all_languages(language_filename)

    print_languages(all_languages)

    num_entries = 20
    print_regional_rankings(all_languages, num_entries)


if __name__ == "__main__":
    main()
