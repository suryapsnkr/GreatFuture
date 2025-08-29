
# ERP Backend (Django + DRF)

A simplified ERP backend that manages **Employees**, **Departments**, and **Projects** with **role-based access**, **JWT auth**, **reports**, **search/pagination**, and **CSV export**.

## Features
- Custom user model `Employee` (extends `AbstractUser`) with `role`, `department`, and `salary`
- Models: `Department`, `Employee`, `Project` (+ M2M between Project and Employee)
- CRUD for all entities via DRF `ModelViewSet`
- Role-based access:
  - **Admin**: full access
  - **Manager**: scoped to their department, limited elevated actions
  - **Employee**: can view self and assigned projects
- Reports endpoints
  - `/api/reports/?type=employees_by_department`
  - `/api/reports/?type=salary_cost_per_department`
  - `/api/reports/?type=active_projects`
- JWT authentication (SimpleJWT)
- Pagination, search & ordering
- CSV export
  - `/api/export/?type=employees_csv`
  - `/api/export/?type=projects_csv`
  - `/api/export/?type=departments_csv`

## Quickstart

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_data   # creates demo departments, users, projects

# Get a token
curl -X POST http://127.0.0.1:8000/api/auth/token/ -H "Content-Type: application/json" -d '{"username":"admin","password":"admin123"}'

python manage.py runserver
```

### Demo logins
- **Admin**: `admin` / `admin123`
- **Manager**: `manager` / `manager123` (Department: Engineering)
- **Employee**: `employee` / `employee123` (Department: Engineering)

## API Routes
- `GET/POST /api/departments/` (Admins can create/update/delete)
- `GET/POST /api/employees/` (Only Admin can create; employees can update self)
- `GET/POST /api/projects/` (Managers create projects in their own department)
- Reports & Export as above

## Search & Ordering
Add `?search=...` or `?ordering=field,-field` to list endpoints.

## Postman Collection
Import `postman_collection.json`. Update `{base_url}` variable if needed.

## Running Tests
```bash
python manage.py test
```

## Notes
- Default DB is SQLite for simplicity.
- Change `SECRET_KEY`, configure DB and CORS for production.
