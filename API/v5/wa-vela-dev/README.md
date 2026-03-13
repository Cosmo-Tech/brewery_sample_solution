# wa-vela-dev

## Solution

### Run templates

| ID                                  | Parameter Groups                                                                                                                  |
| ----------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| `full_demo`                         | • bar_parameters<br>• file_upload                                                                                                 |
| `sim_no_parameters`                 | -                                                                                                                                 |
| `sim_mock_parameters`               | • basic_types<br>• dataset_parts<br>• extra_dataset_part<br>• customers<br>• events<br>• additional_parameters<br>• initial_state |
| `dynamic_values_customers`          | • dynamic_values_customers_group                                                                                                  |
| `hidden test run template`          | -                                                                                                                                 |
| `etl_zip2db`                        | • etl_param_group_bar_parameters<br>• etl_param_group_local_file                                                                  |
| `etl_instance_generator`            | • etl_param_group_instance_parameters<br>• etl_param_group_bar_parameters<br>• etl_param_group_customer_parameters                |
| `etl_with_azure_storage`            | • etl_param_group_bar_parameters<br>• etl_param_group_azure_storage                                                               |
| `etl_sub_dataset_by_filter`         | • etl_param_group_sub_dataset_by_filter                                                                                           |
| `./etl_sub_dataset_by_filter`       | • etl_param_group_sub_dataset_by_dynamic_filter                                                                                   |
| `.//etl_sub_dataset_by_filter`      | • etl_param_group_sub_dataset_by_filter_with_multiple_selection                                                                   |
| `.///etl_sub_dataset_by_filter`     | • etl_param_group_sub_dataset_by_dynamic_filter_with_multiple_selection                                                           |
| `etl_sub_dataset_by_filter_boolean` | • etl_param_group_sub_dataset_by_filter                                                                                           |
| `etl_sub_dataset_by_filter_multi`   | • etl_param_group_sub_dataset_by_dynamic_filter_with_multiple_selection                                                           |
| `standalone`                        | -                                                                                                                                 |

### Parameter groups

| ID                                                                      | Parameters                                                                                                                               |
| ----------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `bar_parameters`                                                        | • stock<br>• restock_qty<br>• nb_waiters                                                                                                 |
| `basic_types`                                                           | • currency<br>• currency_name<br>• currency_value<br>• currency_used<br>• start_date<br>• end_date<br>• average_consumption              |
| `training_dates`                                                        | • training_start_date<br>• training_end_date                                                                                             |
| `file_upload`                                                           | • initial_stock_dataset                                                                                                                  |
| `dataset_parts`                                                         | • example_dataset_part_1<br>• example_dataset_part_2                                                                                     |
| `extra_dataset_part`                                                    | • example_dataset_part_3                                                                                                                 |
| `customers`                                                             | • customers                                                                                                                              |
| `events`                                                                | • events<br>• additional_seats<br>• activated<br>• evaluation                                                                            |
| `initial_state`                                                         | • initial_state                                                                                                                          |
| `additional_parameters`                                                 | • volume_unit<br>• additional_tables<br>• comment<br>• additional_date<br>• countries<br>• scenario_to_compare                           |
| `dynamic_values_customers_group`                                        | • dynamic_values_customers_enum<br>• dynamic_values_customers_list<br>• dynamic_default_value_customers_count                            |
| `etl_param_group_bar_parameters`                                        | • etl_param_stock<br>• etl_param_restock_quantity<br>• etl_param_num_waiters                                                             |
| `etl_param_group_customer_parameters`                                   | • etl_param_satisfaction<br>• etl_param_surrounding_satisfaction<br>• etl_param_thirsty                                                  |
| `etl_param_group_instance_parameters`                                   | • etl_param_tables_count<br>• etl_param_customers_count<br>• etl_param_locale                                                            |
| `etl_param_group_local_file`                                            | • etl_param_bar_instance                                                                                                                 |
| `etl_param_group_azure_storage`                                         | • etl_param_azure_storage_co_string<br>• etl_param_az_storage_account<br>• etl_param_az_storage_container<br>• etl_param_az_storage_path |
| `etl_param_group_sub_dataset_by_filter`                                 | • etl_param_subdataset_filter_is_thirsty                                                                                                 |
| `etl_param_group_sub_dataset_by_dynamic_filter`                         | • etl_param_subdataset_filter_dynamic_customer_name                                                                                      |
| `etl_param_group_sub_dataset_by_dynamic_filter_with_multiple_selection` | • etl_param_subdataset_filter_dynamic_customers_list                                                                                     |
| `etl_param_group_sub_dataset_by_filter_with_multiple_selection`         | • etl_param_subdataset_filter_thirsty_multiselect                                                                                        |

### Parameters

| ID                                                   | Label                           | Type                           | Default Value            |
| ---------------------------------------------------- | ------------------------------- | ------------------------------ | ------------------------ |
| `stock`                                              | Stock                           | int                            | 100                      |
| `restock_qty`                                        | Restock                         | int                            | 25                       |
| `nb_waiters`                                         | Waiters                         | int                            | 5                        |
| `currency`                                           | Currency symbol                 | enum                           | USD                      |
| `currency_name`                                      | Currency name                   | string                         | EUR                      |
| `currency_value`                                     | Value                           | number                         | 1000                     |
| `currency_used`                                      | Enable currency                 | bool                           | false                    |
| `start_date`                                         | Start date                      | date                           | 2014-08-18T00:00:00.000Z |
| `end_date`                                           | End date                        | date                           | 2014-08-20T00:00:00.000Z |
| `average_consumption`                                | Average consumption             | number (SLIDER)                | 3                        |
| `additional_seats`                                   | Additional seats                | number                         | -4                       |
| `additional_tables`                                  | Additional tables               | number                         | 3                        |
| `activated`                                          | Activated                       | bool                           | false                    |
| `evaluation`                                         | Evaluation                      | string                         | Good                     |
| `volume_unit`                                        | Volume unit                     | enum (RADIO)                   | LITRE                    |
| `comment`                                            | Comment                         | string                         | None                     |
| `additional_date`                                    | Additional date                 | date                           | 2022-06-22T00:00:00.000Z |
| `initial_stock_dataset`                              | Initial stock                   | %DATASET_PART_ID_FILE%         | -                        |
| `example_dataset_part_1`                             | Example dataset part 1          | %DATASET_PART_ID_FILE%         | -                        |
| `example_dataset_part_2`                             | Example dataset part 2          | %DATASET_PART_ID_FILE%         | -                        |
| `example_dataset_part_3`                             | Example dataset part 3          | %DATASET_PART_ID_FILE%         | -                        |
| `customers`                                          | Customers                       | %DATASET_PART_ID_FILE% (TABLE) | -                        |
| `events`                                             | Events                          | %DATASET_PART_ID_FILE% (TABLE) | d-kovkq76eo1qj9          |
| `initial_state`                                      | Initial state                   | %DATASET_PART_ID_FILE% (TABLE) | -                        |
| `training_start_date`                                | Start date                      | date                           | -                        |
| `training_end_date`                                  | End date                        | date                           | -                        |
| `etl_param_stock`                                    | Stock                           | string                         | 100                      |
| `countries`                                          | Countries                       | list                           | ["FRANCE","INDIA"]       |
| `dynamic_values_customers_enum`                      | Customer (enum)                 | enum                           | -                        |
| `dynamic_values_customers_list`                      | Customers list (list)           | list                           | -                        |
| `dynamic_default_value_customers_count`              | Number of customers             | int                            | -                        |
| `etl_param_restock_quantity`                         | Restock                         | string                         | 25                       |
| `etl_param_num_waiters`                              | Waiters                         | string                         | 5                        |
| `etl_param_tables_count`                             | Number of tables                | string                         | 10                       |
| `etl_param_customers_count`                          | Number of customers             | string                         | 50                       |
| `etl_param_locale`                                   | Locale of generated names       | string                         | en                       |
| `etl_param_satisfaction`                             | Satisfaction                    | string                         | 0                        |
| `etl_param_surrounding_satisfaction`                 | Surrounding satisfaction        | string                         | 0                        |
| `etl_param_thirsty`                                  | Initial thirst                  | enum                           | NOT_THIRSTY              |
| `etl_param_bar_instance`                             | instance file                   | %DATASET_PART_ID_FILE%         | -                        |
| `etl_param_azure_storage_co_string`                  | azure storage connection string | string                         | -                        |
| `etl_param_az_storage_account`                       | azure storage account name      | string                         | -                        |
| `etl_param_az_storage_container`                     | azure storage container name    | string                         | -                        |
| `etl_param_az_storage_path`                          | azure storage path              | string                         | -                        |
| `etl_param_subdataset_filter_is_thirsty`             | Filter by                       | enum                           | -                        |
| `etl_param_subdataset_filter_thirsty_multiselect`    | Filter by                       | list                           | -                        |
| `etl_param_subdataset_filter_dynamic_customer_name`  | Filter by customer              | enum                           | -                        |
| `etl_param_subdataset_filter_dynamic_customers_list` | Filter by customers             | list                           | -                        |
| `scenario_to_compare`                                | Scenario to compare             | enum                           | -                        |
