create database yellow_taxi;
use yellow_taxi;

create external table vendors
(
    vendor_id int,
    vendor_name string
)
stored as parquet;

insert into vendors
select 1, 'Creative Mobile Technologies'
union all
select 2, 'VeriFone Inc';

create external table rates
(
    rate_id int,
    rate_name string
)
stored as parquet;

insert into rates
select 1, 'Standard rate'
union all
select 2, 'JFK'
union all
select 3, 'Newark'
union all
select 4, 'Nassau or Westchester'
union all
select 5, 'Negotiated fare'
union all
select 6, 'Group ride';


create external table payments
(
    payment_id int,
    payment_name string
)
stored as parquet;

insert into payments
select 1, 'Credit card'
union all
select 2, 'Cash'
union all
select 3, 'No charge'
union all
select 4, 'Dispute'
union all
select 5, 'Unknown'
union all
select 6, 'Voided trip';






---Main table with data
create external table taxi_data
(
vendor_id string,
tpep_pickup_datetime timestamp,
tpep_dropoff_datetime timestamp,
passenger_count int,
trip_distance double,
rate_id int,
store_and_fwd_flag string,
pulocation_id int,
dolocation_id int,
payment_id int,
fare_amount double,
extra double,
mta_tax double,
tip_amount double,
tolls_amount double,
improvement_surcharge double,
total_amount double,
congestion_surcharge double
)
row format delimited
fields terminated by ','
lines terminated by '\n'
location '/user/root/2020'
TBLPROPERTIES ("skip.header.line.count"="1");

---Main table with corrected data field
CREATE EXTERNAL TABlE taxi_cleaned
(
vendor_id string,
tpep_dropoff_datetime timestamp,
passenger_count int,
trip_distance double,
rate_id int,
store_and_fwd_flag string,
pulocation_id int,
dolocation_id int,
payment_id int,
fare_amount double,
extra double,
mta_tax double,
tip_amount double,
tolls_amount double,
improvement_surcharge double,
total_amount double,
congestion_surcharge double,
dt string
);

---Inserting data into cleaned table
INSERT OVERWRITE TABLE taxi_cleaned
SELECT
        vendor_id,
        tpep_dropoff_datetime,
        passenger_count,
        trip_distance,
        rate_id,
        store_and_fwd_flag,
        pulocation_id,
        dolocation_id,
        payment_id,
        fare_amount,
        extra,
        mta_tax,
        tip_amount,
        tolls_amount,
        improvement_surcharge,
        total_amount,
        congestion_surcharge,
        to_date(tpep_pickup_datetime)
FROM    taxi_data;


---New empty partitioned table
create external table taxi_data_part
(
vendor_id string,
tpep_dropoff_datetime timestamp,
passenger_count int,
trip_distance double,
rate_id int,
store_and_fwd_flag string,
pulocation_id int,
dolocation_id int,
payment_id int,
fare_amount double,
extra double,
mta_tax double,
tip_amount double,
tolls_amount double,
improvement_surcharge double,
total_amount double,
congestion_surcharge double
)
partitioned by (dt date);

---Options for dynamic partitioning
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;


---Inserting data into partitioned table
INSERT OVERWRITE TABLE taxi_data_part
PARTITION(dt)
SELECT *
FROM    taxi_cleaned;


---New empty partitioned table part by vendor_id
create external table part_by_vendor
(
tpep_pickup_datetime timestamp,
tpep_dropoff_datetime timestamp,
passenger_count int,
trip_distance double,
rate_id int,
store_and_fwd_flag string,
pulocation_id int,
dolocation_id int,
payment_id int,
fare_amount double,
extra double,
mta_tax double,
tip_amount double,
tolls_amount double,
improvement_surcharge double,
total_amount double,
congestion_surcharge double
)
partitioned by (vendor_id string);

---Inserting data into partitioned table (part by vendor id)
INSERT OVERWRITE TABLE part_by_vendor
PARTITION(vendor_id)
SELECT  *
FROM    taxi_data;


---Small table for the final report
create table taxi_short AS
select payment_id,
       to_date(tpep_pickup_datetime) as dt,
       tip_amount,
       passenger_count
from taxi_data
where year(tpep_pickup_datetime) = 2020
order by dt;


--Final report with MapJoin
select /*+ MAPJOIN(payments) */
       p.payment_name as payment_type,
       t.dt as dt,
       round(avg(t.tip_amount),2) as tip_avg_amount,
       sum(t.passenger_count) as passengers_count
from taxi_short t join payments p
on t.payment_id = p.payment_id
group by p.payment_name, t.dt
order by p.payment_name, t.dt
limit 100;



--- Sandbox. Checking the sum of all tips by payment type.

select payment_id,
       sum(tip_amount) as tip_sum,
       sum(passenger_count) as passengers_count
from taxi_short
group by payment_id
order by payment_id
limit 100;


--- Seems like "AVG(tip_amount)" doesn't work correctly.
--- Maybe it's better to count the sum of all tips and divide it
--- by number of rides for every payment type to get averages

select year(tpep_pickup_datetime), month(tpep_pickup_datetime), count(1)
from taxi_data
group by year(tpep_pickup_datetime), month(tpep_pickup_datetime)
limit 30;


---New version of the final report
select /*+ MAPJOIN(payments) */
       p.payment_name as payment_type,
       t.dt as dt,
       round((sum(t.tip_amount) / count(t.payment_id)),2) as tip_avg_amount,
       sum(t.passenger_count) as passengers_count
from taxi_short t join payments p
on t.payment_id = p.payment_id
where year(dt) = 2020
group by p.payment_name, t.dt
order by p.payment_name, t.dt
limit 100;






