/* load data into tables */

load data local infile '/home/ec2-user/prod/data/single/singles-2022.csv' 
into table singles fields terminated by ',' ignore 1 lines;

load data local infile '/home/ec2-user/prod/data/matched/matches-full-2022.csv' 
into table matches fields terminated by ',' ignore 1 lines;

