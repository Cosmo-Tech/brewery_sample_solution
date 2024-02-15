#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright (c) Cosmo Tech.
# Licensed under the MIT license.


import os
import re
import sys
import random
import argparse
import itertools
from faker import Faker


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Generate a brewery instance with Bar and Customer entities, and relationships between them.'
    )
    parser.add_argument("-t", "--tables", help="Number of tables in the bar", default="10", type=int)
    parser.add_argument("-c", "--customers", help="Number of customers in the instance", default="50", type=int)
    parser.add_argument("-n", "--name", help="Name of the generated instance", default="brewery_instance")
    parser.add_argument("-l", "--locale", help="Localization of generated names (leave empty to use English)")

    parser.add_argument("--restock", help="Restock quantity for generated bar", default="30", type=int)
    parser.add_argument("--stock", help="Stock quantity for generated bar", default="60", type=int)
    parser.add_argument("--waiters", help="Number of waiters for generated bar", default="10", type=int)

    parser.add_argument("--satisfaction", help="Initial statisfaction of generated customers", default="0", type=int)
    parser.add_argument("--surrounding_satisfaction", help="Initial surrounding statisfaction of generated customers",
                        default="0", type=int)
    parser.add_argument("--thirsty", help="Value for the Thirsty attribute of generated customers", default=False,
                        type=bool)

    args = parser.parse_args()
    return args


def get_faker_instance(locale=None):
    locale = locale.split(',') if locale else None
    return Faker(locale)


def generate_people(faker_instance, count):
    people = []
    try:
        for i in range(count):
            people.append(faker_instance.unique.name())
    except Exception as e:
        print(e)
        sys.exit(1)
    return people


def get_id_from_name(name):
    return re.sub(r'[\. \'-\,]', '_', name)


def generate_bar(options):
    return {
        'id': 'MyBar',
        'name': 'MyBar',
        'restock': options['restock'],
        'stock': options['stock'],
        'waiters': options['waiters'],
    }


def generate_customer(person, options):
    return {
        'id': get_id_from_name(person),
        'name': person,
        'satisfaction': options['satisfaction'],
        'surrounding_satisfaction': options['surrounding_satisfaction'],
        'thirsty': options['thirsty'],
    }


def generate_customers(people, options):
    return [generate_customer(person, options) for person in people]


def generate_customers_groups(customers, groups_count):
    '''
    Generate an array of customer groups:
    [
      [customer_id1, customer_id3, customer_id6, customer_id9],
      [customer_id4, customer_id8],
      [customer_id2, customer_id5, customer_id7]
    ]
    Distribution is not perfect on purpose, to have groups of different sizes
    '''
    customer_groups = []
    for i in range(0, groups_count):
        customer_groups.append([])
    for customer in customers:
        group_index = random.randint(0, groups_count - 1)
        customer_groups[group_index].append(customer['id'])
    return customer_groups


def generate_bar_to_customers_mapping(bar, customers):
    '''
    Generate a dict similar to:
    {
      bar_id1: [customer_id1, customer_id3, customer_id6, customer_id9],
      bar_id2: [customer_id4, customer_id8],
      bar_id3: [customer_id2, customer_id5, customer_id7]
    }
    '''
    return {bar['id']: [customer['id'] for customer in customers]}


def generate_customers_to_customers_links(customer_groups):
    pairs = []
    for group in customer_groups:
        connection_probability = random.random()
        for pair in itertools.combinations(group, 2):
            if random.random() > connection_probability:
                pairs.append(pair)
    return pairs


def generate_bar_csv_file_content(bar):
    file_content = 'id,NbWaiters,RestockQty,Stock\n'
    cells = [
        bar['id'],
        str(bar['waiters']),
        str(bar['restock']),
        str(bar['stock'])
    ]
    file_content += ','.join(cells) + '\n'
    return file_content


def generate_customers_csv_file_content(customers):
    file_content = 'id,Satisfaction,SurroundingSatisfaction,Thirsty\n'
    for customer in customers:
        cells = [
            customer['id'],
            str(customer['satisfaction']),
            str(customer['surrounding_satisfaction']),
            str(customer['thirsty']).lower()
        ]
        file_content += ','.join(cells) + '\n'
    return file_content


def generate_bar_to_customers_csv_file_content(bar_to_customers):
    file_content = 'source,target,name\n'
    for bar, customers in bar_to_customers.items():
        for customer in customers:
            cells = [
                bar,
                customer,
                bar + '_contains_' + customer
            ]
            file_content += ','.join(cells) + '\n'
    return file_content


def generate_arc_to_customers_csv_file_content(customers_to_customers_links):
    file_content = 'source,target,name\n'
    for pair in customers_to_customers_links:
        cells = [
            pair[0],
            pair[1],
            'arc_from_' + pair[0] + '_to_' + pair[1]
        ]
        file_content += ','.join(cells) + '\n'
        cells = [
            pair[1],
            pair[0],
            'arc_from_' + pair[1] + '_to_' + pair[0]
        ]
        file_content += ','.join(cells) + '\n'
    return file_content


def generate_csv_files_content(bar, customers, bar_to_customers, customers_to_customers_links):
    return {
        'Bar.csv': generate_bar_csv_file_content(bar),
        'Customer.csv': generate_customers_csv_file_content(customers),
        'Bar_vertex.csv': generate_bar_to_customers_csv_file_content(bar_to_customers),
        'arc_Satisfaction.csv': generate_arc_to_customers_csv_file_content(customers_to_customers_links),
    }


def export_csv_files(csv_files_content, dir_name):
    os.mkdir(dir_name)
    for file_name, file_content in csv_files_content.items():
        with open(os.path.join(dir_name, file_name), 'w') as writer:
            writer.write(file_content)


def main():
    args = parse_arguments()
    bar_options = {
        'restock': args.restock,
        'stock': args.stock,
        'waiters': args.waiters,
    }
    customers_options = {
        'satisfaction': args.satisfaction,
        'surrounding_satisfaction': args.surrounding_satisfaction,
        'thirsty': args.thirsty,
    }

    faker_instance = get_faker_instance(args.locale)
    people = generate_people(faker_instance, args.customers)
    bar = generate_bar(bar_options)
    customers = generate_customers(people, customers_options)
    bar_to_customers = generate_bar_to_customers_mapping(bar, customers)

    customer_groups = generate_customers_groups(customers, args.tables)
    customers_to_customers_links = generate_customers_to_customers_links(customer_groups)

    csv_files_content = generate_csv_files_content(bar, customers, bar_to_customers, customers_to_customers_links)
    export_csv_files(csv_files_content, args.name)


if __name__ == "__main__":
    main()
