/* DDL to create users in mariadb */

create database ukmon;
create user batch@localhost identified by 'Batch33mdl';
create user batch@'%' identified by 'Batch33mdl';
grant all privileges on ukmon.* to batch@'%';
grant all privileges on ukmon.* to batch@localhost;

create database ukmondev;
create user batchdev@localhost identified by 'Batchdev33mdl';
create user batchdev@'%' identified by 'Batchdev33mdl';
grant all privileges on ukmondev.* to batchdev@'%';
grant all privileges on ukmondev.* to batchdev@localhost;

grant select on ukmon.* to batchdev@localhost;
grant select on ukmon.* to batchdev@'%';
grant select on ukmondev.* to batch@localhost;
grant select on ukmondev.* to batch@'%';

flush privileges;
