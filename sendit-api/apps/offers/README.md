# 📚 API Documentation (What Frontend Needs)

---

## 🧱 1. DETAILS STEP

```http
PATCH /offers/{id}/steps/details/
```

### Body

```json
{
  "package_type": "small",
  "is_fragile": true,
  "description": "Glass items"
}
```

---

## 📍 2. LOCATION STEP

```http
PATCH /offers/{id}/steps/location/
```

### Body

```json
{
  "pickup_location": 1,
  "delivery_location": 2,
  "pickup_time": "2026-03-22T10:00:00Z",
  "receiver_name": "John Doe",
  "receiver_phone": "+2348000000000"
}
```

---

## 💰 3. PRICING STEP

```http
PATCH /offers/{id}/steps/pricing/
```

### Body

```json
{
  "base_price": 5000,
  "is_urgent": true
}
```

---

## 👀 4. REVIEW STEP

```http
GET /offers/{id}/steps/review/
```

### Response

```json
{
  "id": "...",
  "code": "ABC123",
  "package_type": "small",
  "pickup": { "lat": 6.5, "lng": 3.3 },
  "delivery": { "lat": 6.6, "lng": 3.4 },
  "pickup_time": "...",
  "is_urgent": true,
  "total_price": 6000,
  "status": "draft"
}
```

---

## 🚀 5. POST OFFER

```http
POST /offers/{id}/transition/
```

### Body

```json
{
  "action": "post"
}
```

---

# 🧠 7. Final Design Summary

---

## ✅ Step System

* controls **data entry**
* uses **step serializers**
* ends at `review`

---

## ✅ Review

* read-only
* uses `OfferListSerializer`

---

## ✅ Transition System

* controls **status**
* handles `POSTED`, `ACCEPTED`, etc.
* triggers notifications



## ✅ Escrow System
During transition stage `POSTED" post is made available for other to see and propose. 
Carrier makes then bid when accepted we create an escrow for the offer and the user whose offer is accepted is attached to the offer.(proposal acceptance handles that)

then the escrow is funded. the carrier when in transit 