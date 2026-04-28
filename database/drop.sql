--DROPPING SCHEMA master and all the TABLES inside master users, locations, profiles, skills, user_skills

DROP SCHEMA IF EXISTS master CASCADE;

--DROPPING SCHEMA collaboration and all the TABLES inside collaboration teams, team_requests, team_members

DROP SCHEMA IF EXISTS collaboration CASCADE;