create index cc_user_username on cc_user (username);

CREATE TABLE auth_user
(
  id integer, 
  username varchar(80), 
  pwdhash  varchar(100),
  ip_addr varchar(20)
);