from zenml import get_step_context, step
#import 
from modules.scraper.crawlers.ec_verfica import EcuadorVerificaScraper
import logging

@step
def crawl_ec_verfica():
    """Crawl Ecuador Verifica"""
    # Create an instance of the scraper
    scraper = EcuadorVerificaScraper()

    # Get all the links
    scraper.get_all_links(year_cutoff=2025)
    logging.info("Iniciando extracción...")
    links = scraper.links
    # step_context = get_step_context()
    # step_context.add_output_metadata(output_name="ec_verifica_links", metadata=links)
    return links
    # Save the links

@step
def crawl_lupa():
    """Crawl Lupa"""
    # Get the step context
    

    # Create an instance of the scraper
    scraper = EcuadorVerificaScraper()

    # Get all the links
    scraper.get_all_links(year_cutoff=2025)
    logging.info("Iniciando extracción...")
    links = scraper.links
    # step_context = get_step_context()
    # step_context.add_output_metadata(output_name="ec_verifica_links", metadata=links)

    return links
    # Save the links


@step
def merge_links(ec_verfica_links, lupa_links):
    """Merge the links from Ecuador Verifica and Lupa"""
    return ec_verfica_links + lupa_links