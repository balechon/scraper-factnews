from zenml import pipeline

from steps.etl.crawl_links import crawl_ec_verfica, crawl_lupa,merge_links


@pipeline
def digital_links():
    """Pipeline to crawl digital links"""
    # Crawl Ecuador Verifica
    ec_verfica_links = crawl_ec_verfica()
    # Crawl Lupa
    lupa_links = crawl_lupa()
    all_links = merge_links(ec_verfica_links, lupa_links)
    return all_links
