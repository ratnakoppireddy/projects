create database paylater;

use paylater;

CREATE TABLE user (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    balance DECIMAL(10, 2)
    );

CREATE TABLE merchant (
    merchant_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    fee DECIMAL(10, 2));
 
 
 CREATE TABLE transactions (
    txn_id INT AUTO_INCREMENT PRIMARY KEY,
    u_id INT, 
    m_id INT, 
    m_fee DECIMAL,
    t_date DATETIME,
    amount DECIMAL(10, 2),
        FOREIGN KEY (u_id)  
        REFERENCES user(user_id) 
            ON UPDATE CASCADE 
            ON DELETE RESTRICT,
        FOREIGN KEY (m_id)
        REFERENCES merchant(merchant_id)
            ON UPDATE CASCADE 
            ON DELETE RESTRICT);

CREATE TABLE repayments (
    repay_id INT AUTO_INCREMENT PRIMARY KEY,
    u_id INT, 
    amount DECIMAL(10, 2),
    repay_date DATETIME,
    FOREIGN KEY (u_id)  
        REFERENCES user(user_id) 
            ON UPDATE CASCADE 
            ON DELETE RESTRICT);
          



       
)            