# ⚡ VizoSyn - Skill-Based Teammate Matchmaking Backend

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-316192?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-black?style=for-the-badge&logo=JSON%20web%20tokens)

> **Live Backend API (Render):** [https://vizosyn-api.onrender.com/api](https://vizosyn-api.onrender.com/api)

> **Live Frontend (Vercel):** [https://vizosyn-frontend.vercel.app](https://vizosyn-frontend.vercel.app)

## 📖 System Architecture & Problem Statement
Finding reliable teammates during hackathons is often unstructured and chaotic. VizoSyn acts as a strict, data-driven matchmaking engine. Instead of a basic CRUD app, this backend handles complex state changes—managing users, mapping them to 10+ specific technical skills, handling team creation, and tracking the lifecycle of join requests (pending, accepted, rejected) using a highly normalized PostgreSQL schema hosted on Neon Serverless Postgres..

## 🛠️ Core Engineering Implementations (Under the Hood)
1. **Stateless JWT Ecosystem:** Secured specific routes enforcing `Depends(get_current_user)`, ensuring that actions like disbanding a team or updating a profile are strictly authorized.
2. **Complex ORM Relationships:** Leveraged SQLAlchemy to handle advanced Many-to-Many relationships (e.g., `user_skills`, `team_members`) preventing data anomalies when users switch teams or update stacks.
3. **Strict Payload Validation:** Replaced manual type-checking with Pydantic schemas, ensuring incoming data (like skill arrays or profile updates) strictly adheres to the database requirements before executing transactions.
4. **Stateful Request Handling:** Developed specialized endpoints (like `PATCH /process-request`) to handle the business logic of team building, ensuring team capacity limits and request states are managed accurately.

## 🗄️ Database Architecture
The relational database is powered by Neon Serverless PostgreSQL, segregated for logical clarity:

* **`master` Schema:**
  * `users`: Authentication and secure credential storage.
  * `profiles`: Extended demographic and professional data.
  * `locations`: Geographic data for local matching.
  * `skills` & `user_skills`: Lookup tables mapping users to specific technical proficiencies.
* **`collaboration` Schema:**
  * `teams`: Manages team identity, metadata, and capacity limits.
  * `team_members`: Tracks the active association between users and teams.
  * `team_requests`: Manages the stateful workflow (Pending/Accepted/Rejected) of users trying to join teams.

## 🚀 Local Installation & Initialization

**1. Clone the repository**
```bash
git clone https://github.com/nikhilprasad-data/vizosyn_backend.git
cd vizosyn_backend
```

**2. Virtual Environment Setup**
```bash
python -m venv venv
source venv/Scripts/activate  # Windows
```

**3. Install Dependencies**
```bash
pip install -r requirements.txt
```

**4. Environment Variables Setup**
Create a `.env` file in the root directory:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/vizosyn_db
SECRET_KEY=your_jwt_secret_key
ALGORITHM=HS256
```

**5. Database Initialization (Strict Order)**
Execute the database setup scripts via pgAdmin or psql to establish the schema and inject dummy data for local testing:
* Run `database/schema.sql` (Builds schemas and tables)
* Run `database/seed.sql` (Injects dummy users, skills, and teams)

**6. Launch the ASGI Server**
```bash
uvicorn src.main:app --reload
```

## 📡 API Endpoints (Quick Reference)
Detailed documentation is available in the Postman collection. Key endpoints include:

**Authentication & Profiles:**
* `POST /api/auth/signup` - Register a new user and hash credentials.
* `POST /api/auth/login` - Authenticate and issue Bearer token.
* `PATCH /api/profile/update-my-profile` - Update dynamic user profile data.

**Collaboration & Teams:**
* `POST /api/team/create` - Initialize a new team entity.
* `DELETE /api/team/delete-my-team` - Securely disband a team (Admin only).
* `PATCH /api/team_request/process-request` - Accept or reject a user's request to join.

---
*Engineered by [Nikhil Prasad](https://github.com/nikhilprasad-data).*