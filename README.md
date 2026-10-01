# 🛍️ SADGURU KRUPA (Everything For Mens) - E-Commerce Platform

Official digital storefront and full-stack e-commerce web platform for **Sadguru Krupa**, Ahilyanagar's premier menswear showroom located at:
> **Shop No 01, Delhi Gate, Balikashram Rd, Sarjepura, Ahilyanagar (Ahmednagar), Maharashtra 414001**

Built with **Django 6**, **Tailwind CSS**, **SQLite/PostgreSQL**, and integrated with **Razorpay Payments** and **WhatsApp Commerce**.

---

## 🌟 Key Features

### 1. 👕 Menswear Catalog & Discovery
- **Extensive Collections**: Formal shirts, casual shirts, denim jeans, trousers/chinos, festive kurtas, gym & athletic training wear.
- **Interactive Multi-Image Gallery**: High-resolution garment previews with thumbnail switching.
- **Dynamic Filtering**: Filter by category, fit (*Slim, Regular, Relaxed, Tailored*), and sizes (*S, M, L, XL, XXL / 28–38*).
- **Interactive Size Guide**: Popup modal with measurements (Chest, Shoulder, Length, Waist) in inches for Indian sizing.
- **Real-Time Pincode Checker**: Validates same-day/next-day delivery for Ahilyanagar (414xxx) and express Pan-India shipping.

### 2. 💳 Multi-Channel Checkout & Payments
- **Razorpay Online Payment Gateway**: Instant card payments (Visa, MasterCard, RuPay), NetBanking, Wallets, and UPI.
- **Instant Scan & Pay UPI QR**: Dynamic QR with real-time countdown timer, pre-filled order total, and UTR transaction reference capture.
- **Cash on Delivery (COD)**: Doorstep cash settlement with order confirmation.
- **Direct WhatsApp Chat Commerce**: 1-Tap checkout with pre-formatted invoice sent directly to the store WhatsApp.
- **Promo Vouchers & Coupons**: Real-time AJAX validation for percentage discounts (e.g. `WELCOME10`, `SKF50`).
- **Official Printable Tax / Retail Invoices**: Formatted printable invoices with tax breakdown, GST placeholder, and store stamp.

### 3. ⭐ Product Reviews & Dynamic Ratings
- **1–5 Star Rating System**: Interactive star selector with live golden hover effects and rating labels (*e.g., "5 Stars — Excellent"*).
- **Verified Buyer Status**: Automatically links phone numbers with past completed purchases to award a green Verified Buyer badge.
- **Star Distribution Bar Chart**: Percentage breakdown of 5★, 4★, 3★, 2★, and 1★ customer reviews.
- **Dynamic Score Recalculation**: Automatically updates product average score and total review counters upon submission.

### 4. ❤️ Customer Wishlist ("Save for Later")
- **One-Tap Heart Buttons**: Save garments from the homepage, catalog, or product detail page.
- **Live Counter Badges**: Synchronized header and mobile bottom bar counter badges.
- **Dedicated Wishlist Page (`/wishlist/`)**: View saved garments, choose size, and click **"Move to Bag"** or order directly via WhatsApp.

### 5. 👤 Customer Accounts & "My Orders" Portal
- **Mobile Number / Email Authentication**: Fast signup and login using phone number or email with password.
- **Retrospective Order Linking**: Previous guest orders matching the customer's phone number automatically link to their account upon registration.
- **"My Orders" Dashboard**: View all past orders, live status pills (*Placed, Confirmed, Packed, In Transit, Delivered*), and payment receipts.
- **1-Click "Order Again"**: Easily re-add all garments and chosen sizes from any previous order directly back into the cart.
- **Saved Delivery Address**: Automatically pre-fills name, phone, email, and address for friction-free 1-click checkout.

### 6. 📍 Local Store Locator & Order Tracking
- **Interactive Store Locator**: Ahilyanagar Delhi Gate showroom directions, Google Maps embed, operating hours (10 AM – 10 PM), and phone dialer.
- **Live Order Tracking (`/track-order/`)**: Public search tool allowing customers to track order progress using Order ID or phone number.

---

## 🛠️ Tech Stack
- **Backend**: Python 3.12+, Django 6.1
- **Frontend**: HTML5, Tailwind CSS, FontAwesome 6, Vanilla ES6 JavaScript
- **Database**: SQLite3 (Production-ready for PostgreSQL / MySQL)
- **Payments**: Razorpay Python SDK, Dynamic UPI QR Protocol
- **Media / Assets**: Pillow (PIL), Staticfiles

---

## 🚀 Quick Setup Instructions

### 1. Clone the Repository
```bash
git clone https://github.com/mahesh04-droid/sk-fashion.git
cd sk-fashion
```

### 2. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables (Optional)
Copy `.env.example` to `.env` and fill in your keys:
```bash
cp .env.example .env
```

### 5. Apply Migrations & Seed Demo Products
```bash
python manage.py migrate
python seed_data.py
```

### 6. Run the Development Server
```bash
python manage.py runserver
```
Visit **http://127.0.0.1:8000/** in your browser.

---

## 👨‍💼 Admin Back-Office Access
Visit **http://127.0.0.1:8000/admin/**
- **Default Username**: `admin`
- **Default Password**: `admin123` *(change in production)*

---

## 📄 License
This project is proprietary to **Sadguru Krupa (Everything For Mens)**, Ahilyanagar, Maharashtra. All rights reserved.
