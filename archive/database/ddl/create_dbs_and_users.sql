/* DDL to create users in mariadb */

create database ukmon;
create or replace user if not exists batch@localhost identified by 'Batch33mdl';
grant usage on ukmon.* to batch@localhost;
create database ukmondev;
create or replace user if not exists batchdev@localhost identified by 'Batchdev33mdl';
grant usage on ukmondev.* to batchdev@localhost;
flush privileges;
