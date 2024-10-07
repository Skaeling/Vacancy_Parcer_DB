DROP TABLE IF EXISTS employers, vacancies CASCADE;

CREATE TABLE employers (
    employer_id INT PRIMARY KEY,
    company_name VARCHAR(100) NOT NULL,
    open_vacancies INT NOT NULL,
    location VARCHAR(50),
    employer_url TEXT
);

CREATE TABLE vacancies (
    vacancy_id INT PRIMARY KEY,
    vacancy_name VARCHAR(100) NOT NULL,
    employer_id INT NOT NULL,
    salary_min INT DEFAULT NULL,
    salary_max INT DEFAULT NULL,
    currency CHAR(5),
    vacancy_url TEXT,
    experience TEXT,
    type VARCHAR(100),
    FOREIGN KEY (employer_id) REFERENCES employers(employer_id)
);
