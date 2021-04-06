import requests, json
from django.core.management.base import BaseCommand
from celery import shared_task

from datasn.models import DatasnCategory, DatasnMake, DatasnYear



class Command(BaseCommand):
    help = "Parse Make, Category and Year Datasn tables"
    year_url = "https://datasn.io/data/api/v1/n3.datasn.io/n3a5/auto_parts_north_america_1/main/list/{}/?client_key=PLtVZ5bh631L5XRU1dCjxIKSs5l0PIIktjYDNlhO&app=json&order_by=id, ASC&limit=10000&manifest=row&tables=year"
    category_url = "https://datasn.io/data/api/v1/n3.datasn.io/n3a5/auto_parts_north_america_1/main/list/{}/?client_key=PLtVZ5bh631L5XRU1dCjxIKSs5l0PIIktjYDNlhO&app=json&order_by=id, ASC&limit=10000&manifest=row&tables=category_2"
    make_url = "https://datasn.io/data/api/v1/n3.datasn.io/n3a5/auto_parts_north_america_1/main/list/{}/?client_key=PLtVZ5bh631L5XRU1dCjxIKSs5l0PIIktjYDNlhO&app=json&order_by=id, ASC&limit=10000&manifest=row&tables=make"

    def get_pagination_data(self, url):
        r = requests.get(self.category_url)
        if r.ok:
            cdata = r.json()
            if int(cdata["meta"]["stats"]["rows_total"]) > 10000:
                return int(int(cdata["meta"]["stats"]["rows_total"]) / 10000) + 1
            return 1
        else:
            raise ValueError("Something wrong with connection, please try to parse data later")

    def get_category_data(self):
        page = 1
        total_pages = self.get_pagination_data(self.category_url.format(page))
        for page in range(total_pages):
            page += 1
            r = requests.get(self.category_url.format(page))
            if r.ok:
                cdata = r.json()
                for index, item in cdata["output"]["rows"].items():
                    save_category_data({
                        'id': item["category_2.id"],
                        'title': item["category_2.title"],
                        'slug': item['category_2.slug'],
                        'parttype': item['category_2.parttype'],
                        'description': item.get('category_2.description'),
                        'engines_url': item.get('category_2.engine_x_category_1_x_category_2')
                    })
            else:
                raise ValueError("Something wrong with connection, please try to parse data later")

        self.stdout.write(self.style.SUCCESS(f"Successfully parsed category data"))


    def get_make_data(self):
        page = 1
        total_pages = self.get_pagination_data(self.make_url.format(page))
        for page in range(total_pages):
            page += 1
            r = requests.get(self.make_url.format(page))
            if r.ok:
                cdata = r.json()
                for index, item in cdata["output"]["rows"].items():
                    save_make_data({
                        'id': item["make.id"],
                        'title': item["make.title"],
                        'slug': item["make.slug"]
                    })
            else:
                raise ValueError("Something wrong with connection, please try to parse data later")

        self.stdout.write(self.style.SUCCESS(f"Successfully parsed make data"))

    def get_year_data(self):
        page = 1
        total_pages = self.get_pagination_data(self.year_url.format(page))
        for page in range(total_pages):
            page += 1
            r = requests.get(self.year_url.format(page))
            if r.ok:
                cdata = r.json()
                for index, item in cdata["output"]["rows"].items():
                    save_year_data({
                        'id': item["year.id"],
                        'title': item["year.title"],
                        'model_url': item["year.model"]
                    }, item["make.id"])
            else:
                raise ValueError("Something wrong with connection, please try to parse data later")

        self.stdout.write(self.style.SUCCESS(f"Successfully parsed year data"))


    def handle(self, *args, **options):
        self.get_category_data()
        self.get_make_data()
        self.get_year_data()




@shared_task
def save_category_data(cdata):
    DatasnCategory.objects.update_or_create(**cdata)

@shared_task
def save_make_data(cdata):
    DatasnMake.objects.update_or_create(**cdata)

@shared_task
def save_year_data(cdata, make_id):
    year, created = DatasnYear.objects.update_or_create(**cdata)
    year.make.add(DatasnMake.objects.get(pk=make_id))
    year.save()