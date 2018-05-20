import steamreviews


def main(download_reference_hidden_gems_as_well=False):
    if download_reference_hidden_gems_as_well:
        from appids import appid_hidden_gems_reference_set

        # All the reference hidden-gems
        steamreviews.download_reviews_for_app_id_batch(appid_hidden_gems_reference_set)

    # All the remaining hidden-gem candidates, which app_ids are stored in idlist.txt
    steamreviews.download_reviews_for_app_id_batch()

    return True


if __name__ == "__main__":
    download_reference_hidden_gems_as_well = True
    main(download_reference_hidden_gems_as_well)
