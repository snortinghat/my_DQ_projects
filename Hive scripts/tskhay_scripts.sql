--Creating the database and making it active
create database yellow_taxi;
use yellow_taxi;


--Creating dimensions and inserting data into them
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


---Main table from data, already stored in HDFS
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
partitioned by (dt string)
stored as parquet;

--Turning ON the dynamic partitioning
SET hive.exec.dynamic.partition=true;
SET hive.exec.dynamic.partition.mode=nonstrict;

---Inserting data into partitioned table
INSERT OVERWRITE TABLE taxi_data_part
PARTITION(dt)
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
        substring(tpep_pickup_datetime,0,10)
FROM   taxi_data;


--A view for the final report
create view taxi_short AS
select payment_id,
       to_date(dt) as dt,
       tip_amount,
       passenger_count
from taxi_data_part
where year(dt) = 2020
order by dt;

set hive.cli.print.header=true;


--Creating Datamart for the final report
CREATE EXTERNAL TABLE datamart
(payment_type string,
dt date,
tips_avg_amount double,
passengers_count int
)
stored as parquet;


--Inserting data into the datamart
INSERT OVERWRITE TABLE datamart
select /*+ MAPJOIN(payments) */
       p.payment_name as payment_type,
       t.dt as dt,
       round((sum(t.tip_amount) / count(t.tip_amount)),2) as tips_avg_amount,
       sum(t.passenger_count) as passengers_count
from taxi_short t join payments p
on t.payment_id = p.payment_id
where year(dt) = 2020
group by p.payment_name, t.dt
order by p.payment_name, t.dt;








