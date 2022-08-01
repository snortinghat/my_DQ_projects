import requests
import logging
from airflow import AirflowException
from airflow.models import BaseOperator


class DinaRamSpeciesCountOperator(BaseOperator):

    template_fields = ('species_type',)
    ui_color = "#e0ffff"

    def __init__(self, species_type: str = 'Human', **kwargs) -> None:
        super().__init__(**kwargs)
        self.species_type = species_type

    def get_page_count(self, api_url: str) -> int:
        r = requests.get(api_url)
        if r.status_code == 200:
            logging.info("SUCCESS")
            page_count = r.json().get('info').get('pages')
            logging.info(f'page_count = {page_count}')
            return int(page_count)
        else:
            logging.warning("HTTP STATUS {}".format(r.status_code))
            raise AirflowException('Error in load page count')

    def get_species_count_on_page(self, result_json: list) -> int:
        species_count_on_page = 0
        for one_char in result_json:
            if one_char.get('species') == self.species_type:
                species_count_on_page += 1
        logging.info(f'     {self.species_type} count_on_page = {species_count_on_page}')
        return species_count_on_page

    def execute(self, context):
        species_count = 0
        ram_char_url = 'https://rickandmortyapi.com/api/character/?page={pg}'
        for page in range(self.get_page_count(ram_char_url.format(pg='1'))):
            r = requests.get(ram_char_url.format(pg=str(page + 1)))
            if r.status_code == 200:
                logging.info(f'PAGE {page + 1}')
                species_count += self.get_species_count_on_page(r.json().get('results'))
            else:
                logging.warning("HTTP STATUS {}".format(r.status_code))
                raise AirflowException('Error in load from Rick&Morty API')
        logging.info(f'{self.species_type} in Rick&Morty: {species_count}')
