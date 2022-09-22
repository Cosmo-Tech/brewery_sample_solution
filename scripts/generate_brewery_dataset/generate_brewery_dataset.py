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
    parser.add_argument("-b", "--bars", help="Number of bars in the instance", default="10", type=int)
    parser.add_argument("-c", "--customers", help="Number of customers in the instance", default="50", type=int)
    parser.add_argument("-n", "--name", help="Name of the generated instance", default="brewery_instance")
    parser.add_argument("-l", "--locale", help="Localization of generated names (leave empty to use all names)")

    parser.add_argument("--restock", help="Restock quantity for generated bars", default="30", type=int)
    parser.add_argument("--stock", help="Stock quantity for generated bars", default="60", type=int)
    parser.add_argument("--waiters", help="Number of waiters for generated bars", default="10", type=int)

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


def generate_companies(faker_instance, count):
    companies = []
    try:
        for i in range(count):
            companies.append(faker_instance.unique.company())
    except Exception as e:
        print(e)
        sys.exit(1)
    return companies


def get_id_from_name(name):
    # chars_to_remove = [' ', "'", '.', '-', '\,']
    # return re.sub('[' + ''.join(chars_to_remove) + ']', '_', name)
    return re.sub(r'[\. \'-\,]', '_', name)


def generate_bar(company, options):
    return {
        'id': get_id_from_name(company),
        'name': company,
        'restock': options['restock'],
        'stock': options['stock'],
        'waiters': options['waiters'],
    }


def generate_bars(companies, options):
    return [generate_bar(company, options) for company in companies]


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


def generate_bars_to_customers_mapping(bars, customer_groups):
    '''
    Generate a dict similar to:
    {
      bar_id1: [customer_id1, customer_id3, customer_id6, customer_id9],
      bar_id2: [customer_id4, customer_id8],
      bar_id3: [customer_id2, customer_id5, customer_id7]
    }
    '''
    bar_to_customers = {}
    for index, bar in enumerate(bars):
        bar_to_customers[bar['id']] = customer_groups[index]
    return bar_to_customers


def generate_customers_to_customers_links(customer_groups):
    pairs = []
    for group in customer_groups:
        connection_probability = random.random()
        for pair in itertools.combinations(group, 2):
            if random.random() > connection_probability:
                pairs.append(pair)
    return pairs


def generate_bar_csv_file_content(bars):
    file_content = 'NbWaiters,RestockQty,Stock,id\n'
    for bar in bars:
        cells = [
            str(bar['waiters']),
            str(bar['restock']),
            str(bar['stock']),
            bar['id']
        ]
        file_content += ','.join(cells) + '\n'
    return file_content


def generate_customers_csv_file_content(customers):
    file_content = 'Satisfaction,SurroundingSatisfaction,Thirsty,id\n'
    for customer in customers:
        cells = [
            str(customer['satisfaction']),
            str(customer['surrounding_satisfaction']),
            str(customer['thirsty']).lower(),
            customer['id']
        ]
        file_content += ','.join(cells) + '\n'
    return file_content


def generate_bars_to_customers_csv_file_content(bar_to_customers):
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
    return file_content


def generate_csv_files_content(bars, customers, bar_to_customers, customers_to_customers_links):
    return {
        'Bar.csv': generate_bar_csv_file_content(bars),
        'Customer.csv': generate_customers_csv_file_content(customers),
        'Bar_vertex.csv': generate_bars_to_customers_csv_file_content(bar_to_customers),
        'arc_Satisfaction.csv': generate_arc_to_customers_csv_file_content(customers_to_customers_links),
    }


def export_csv_files(csv_files_content, dir_name):
    os.mkdir(dir_name)
    for file_name, file_content in csv_files_content.items():
        with open(os.path.join(dir_name, file_name), 'w') as writer:
            writer.write(file_content)


def main():
    args = parse_arguments()
    bars_options = {
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
    companies = generate_companies(faker_instance, args.bars)
    bars = generate_bars(companies, bars_options)
    customers = generate_customers(people, customers_options)

    customer_groups = generate_customers_groups(customers, len(bars))
    bar_to_customers = generate_bars_to_customers_mapping(bars, customer_groups)
    customers_to_customers_links = generate_customers_to_customers_links(customer_groups)

    csv_files_content = generate_csv_files_content(bars, customers, bar_to_customers, customers_to_customers_links)
    export_csv_files(csv_files_content, args.name)


if __name__ == "__main__":
    main()
