CREATE SCHEMA msnoise;
CREATE USER 'msnoise'@'localhost' IDENTIFIED  BY 'msnoise';
GRANT ALL PRIVILEGES ON msnoise.* TO 'msnoise'@'localhost';