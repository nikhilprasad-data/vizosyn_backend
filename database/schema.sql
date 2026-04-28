--users, profiles, locations, skills, user_skills
CREATE SCHEMA IF NOT EXISTS master;

--teams, team_requests, team_members
CREATE SCHEMA IF NOT EXISTS collaboration;

CREATE TABLE IF NOT EXISTS master.users
(
     id             SERIAL         PRIMARY KEY,
     username       VARCHAR(50)    UNIQUE NOT NULL,
     email          VARCHAR(50)    UNIQUE NOT NULL,
     password_hash  VARCHAR        NOT NULL,
     is_active      BOOLEAN        DEFAULT true,
     created_at     TIMESTAMP      DEFAULT CURRENT_TIMESTAMP 
);

CREATE TABLE IF NOT EXISTS master.locations
(
     id        SERIAL         PRIMARY KEY,
     city      VARCHAR(50)    NOT NULL,
     state     VARCHAR        NOT NULL,
     UNIQUE(city, state)
);

CREATE TABLE IF NOT EXISTS master.profiles
(
     id             SERIAL         PRIMARY KEY,
     user_id        INT            UNIQUE REFERENCES master.users(id) ON DELETE CASCADE,
     location_id    INT            REFERENCES master.locations(id),
     full_name      VARCHAR(50)    NOT NULL,
     bio            TEXT,
     github_url     VARCHAR(100),
     linkedin_url   VARCHAR(100),
     is_active      BOOLEAN        DEFAULT true
);

CREATE TABLE IF NOT EXISTS master.skills
(
     id             SERIAL         PRIMARY KEY,
     skill_name     VARCHAR(25)    UNIQUE         NOT NULL
);

CREATE TABLE IF NOT EXISTS master.user_skills
(
     user_id   INT REFERENCES master.users(id),
     skill_id  INT REFERENCES master.skills(id),
     PRIMARY KEY(user_id, skill_id)
);

CREATE TABLE IF NOT EXISTS collaboration.teams
(
     id             SERIAL         PRIMARY KEY,
     name           VARCHAR(100)   UNIQUE    NOT NULL,
     description    TEXT,
     admin_id       INT            REFERENCES master.users(id),
     max_members    INT            DEFAULT 5,
     created_at     TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
     status         VARCHAR(20)    CHECK(status IN ('Open', 'Full')) DEFAULT 'Open',
     is_active      BOOLEAN        DEFAULT true

);

CREATE TABLE IF NOT EXISTS collaboration.team_requests
(
     id             SERIAL         PRIMARY KEY,
     team_id        INT            REFERENCES collaboration.teams(id),
     user_id        INT            REFERENCES master.users(id),
     status         VARCHAR(20)    CHECK(status IN ('Pending', 'Accepted', 'Rejected'))  DEFAULT 'Pending',
     message        TEXT,
     requested_at   TIMESTAMP      DEFAULT CURRENT_TIMESTAMP   
);

CREATE TABLE IF NOT EXISTS collaboration.team_members
(
     id        SERIAL    PRIMARY KEY,
     team_id   INT       REFERENCES collaboration.teams(id),
     user_id   INT       REFERENCES master.users(id),
     is_active BOOLEAN   DEFAULT true,
     joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);