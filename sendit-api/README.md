# 📦 Logistics Marketplace API

A backend API for a logistics marketplace where users can create delivery offers, carriers can submit proposals, and both parties interact through a structured workflow with real-time notifications.

---

## 🚀 Features

* 📝 Step-based offer creation (Details → Location → Pricing → Review)
* 📍 Location handling with nested data support
* 💰 Pricing calculation with platform and urgency fees
* 🚚 Carrier proposal system
* 🔔 Notification system (list, retrieve, mark as read)
* 🔐 Role-based permissions (Sender / Carrier)
* 📊 Offer state management (Draft → Posted → In Progress → Completed)

---

## 🧱 Tech Stack

* **Backend:** Django, Django REST Framework
* **Database:** PostgreSQL (recommended)
* **Filtering:** django-filter

---

## ⚙️ Installation

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo

python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

pip install -r requirements.txt

python manage.py migrate
python manage.py runserver
```

---

## 🔑 API Overview

### Offers

* `POST /offers/` → Create draft
* `PATCH /offers/{id}/details/`
* `PATCH /offers/{id}/location/`
* `PATCH /offers/{id}/pricing/`
* `POST /offers/{id}/post/`

### Proposals

* `POST /offers/{id}/proposals/`
* `POST /proposals/{id}/accept/`

### Notifications

* `GET /notifications/` → List (filterable)
* `GET /notifications/{id}/` → Retrieve (marks as read)

---

## 🧠 Core Concepts

* **Step vs Status**

  * Steps guide user input
  * Status controls business flow

* **Service Layer**

  * Business logic handled in services
  * Views remain thin and focused

* **Flexible Editing**

  * Offers can be edited at any step before acceptance

---

## 🧪 Running Tests

```bash
python manage.py test
```

---

## 📌 Future Improvements

* Real-time notifications (WebSockets)
* Background jobs (Celery)
* Geo-based matching (PostGIS)
* Caching (Redis)

---

## 📄 License

MIT License
