# LDS
Decision Support Systems - Module II: LABORATORY OF DATA SCIENCE (2023/24)

The project consists in a set of assignements corresponding to a BI process: data integration, construction of an OLAP cube, qurying of a OPLAP cube and reporting.

# Dataset
Gun violence dataset provided by the professors of the [course](http://didawiki.cli.di.unipi.it/doku.php/mds/lbi/start).

[dataset](./LDS_Part1_Group_3/dataset/): this directory contains the raw data CSV file, some additional datasets for integrate some detailed information and tables derived from raw data exported into CSV prepared for loading onto the SQL Server Management Studio.
- Raw data: *Police.csv*
- Split tables: *custody.csv* · *participant.csv* · *dates.csv* · *geography.csv* · *gun.csv*
- External data: *city_country_continent.csv* · *uscities.csv*

External data source: 
- https://simplemaps.com/data/us-cities
- https://gitcode.com/mirrors/wizardcode/world-area/tree/master/children

# Tasks
- ETL and Data Warehouse building
- SQL Server Integration Services (SSIS) practice with computation on the client side
- Data Cube building and business questions answering by querying the cube using MDX in SQL Management Studio
