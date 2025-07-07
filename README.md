# 🍔 College Canteen Digitization App

## Project Overview

The College Canteen Digitization App is a comprehensive web-based platform designed to streamline and modernize the food ordering process for students at Narsee Monjee College of Commerce and Economics, Mumbai. It offers a seamless experience for students to browse the canteen menu, place orders, and make payments online, significantly reducing wait times.

Crucially, this system also includes a **robust order management platform** for canteen staff. It leverages **QR codes for efficient order confirmation** upon collection, and facilitates **user bill tracking and collection**, ensuring a smooth and accountable transaction process for both students and staff.

Developed with Python and the Flask web framework, this application provides an end-to-end digital solution for college canteen operations.

## Features

* **User Authentication:** Secure student login and registration system.
* **Dynamic Menu Display:** Browse current canteen offerings with item details and pricing.
* **Digital Order Placement:** Add multiple items to a cart, adjust quantities, and place orders digitally.
* **Online Payment Integration:** Seamless payment processing via **Razorpay's Python SDK**.
* **Order Tracking for Students:** Students can view their order status (e.g., pending, preparing, ready for collection).
* **Integrated Order Management Platform:** Dedicated interface for canteen staff to:
    * View and process incoming orders in real-time.
    * Update order statuses (e.g., "preparing," "ready for collection").
    * Track individual user bills.
* **QR Code Order Confirmation:** Unique QR codes generated for each order, enabling quick and secure confirmation upon collection by canteen staff.
* **User Bill Tracking & Collection:** Streamlined system for managing and confirming payment/collection of student bills.
* **Order History:** Students can review their past orders.
* **Responsive Design:** Accessible across various devices (mobile, tablet, desktop).

## Tech Stack

The application is built using the following core technologies:

* **Backend Language:** Python 3.6
* **Web Framework:** Flask
* **Database:** SQLite (for local storage and efficient data management)
* **Payment Gateway:** Razorpay (integrated via its Python SDK)
* **Frontend:** HTML5, CSS3, JavaScript (with Jinja2 templating for Flask)
* **QR Code Generation:** qrcode

## Getting Started

To get a copy of this project up and running on your local machine, follow these steps:

 **Clone the repository:**
    ```bash
    git clone [https://github.com/arnalph/nm-canteen.git]
    cd canteen-digitization-app
    ```

## Usage

* **Students:** Register an account, log in, browse the menu, add items to cart, proceed to checkout for online payment. Upon order readiness, a unique QR code will be provided for collection.
* **Canteen Staff:** Log in to the dedicated order management platform to view, process, and confirm orders using the student-provided QR codes for efficient collection and bill tracking.

## Implementation Details

For a detailed explanation of the application's architecture, database schema, payment flow, QR code mechanism, order management logic, and specific technical choices, please refer to the accompanying PowerPoint presentation:
* [Link to your PPT explaining implementation] (https://github.com/arnalph/nmcanteen-app/blob/main/canteen-digitzation-nm.pdf)

## Project Status

This project is currently Completed.

## License

This project is licensed under the MIT - see the `LICENSE` file for details.

---
