/* DDL to create brightness-table in mariadb */

use ukmon;

create table brightness(
    CaptureNight int unsigned,
    ts double(15,3),
    bmax double(15,3),
    bave double(15,3),
    bstd double(15,3),
    camid varchar(8),
    imgname varchar(48)
);
alter ignore table ukmon.brightness add unique idx_imgname(imgname);