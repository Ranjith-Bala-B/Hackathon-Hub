# Hackathon Hub

Hackathon Hub is a comprehensive web platform designed to bridge the gap between hackathon organizers and student participants. The platform allows organizations to host, manage, and track hackathons while enabling students to discover events, form teams, and register seamlessly.

## Features

- **User Roles:** Distinct profiles and authentication for Students and Organizations.
- **Organization Dashboard:** 
  - Create and manage hackathon events with detailed specifications.
  - View registered teams, including team members' details.
  - Toggle registration status (open/close) dynamically.
- **Student Dashboard:** 
  - Browse upcoming hackathons on a centralized hub.
  - Register as a team leader and input details for all team members.
  - Track registered events and registration status.
- **Responsive UI:** A dynamic frontend built with HTML, CSS, and Vanilla JavaScript.

## Technology Stack

- **Backend:** Python, Flask
- **Frontend:** HTML5, CSS3, Vanilla JavaScript
- **Database:** SQLite3
- **Additional Libraries:** Flask-CORS, Werkzeug

## Prerequisites

Before running the project, ensure you have Python 3.x installed on your system.

## Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd hackathon-hub
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   # On Windows use: 
   venv\Scripts\activate
   # On macOS/Linux use:
   source venv/bin/activate
   ```

3. **Install the dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Running the Application

1. **Database Initialization:**
   The SQLite database (`hackathon_hub.db`) and all necessary tables will be automatically initialized when you run the application for the first time.

2. **Start the Flask server:**
   ```bash
   python app.py
   ```

3. **Access the application:**
   Open your web browser and navigate to `http://localhost:5000` or `http://127.0.0.1:5000`.

## Project Structure

- `app.py`: The main Flask application handling routing, API endpoints, authentication, and database queries.
- `index.html`: The main frontend entry point for the user interface.
- `styles.css`: Stylesheet for the web interface containing responsive layouts and design.
- `script.js`: Client-side logic, user interactions, and API communication.
- `hackathon_hub.db`: SQLite database file storing users, hackathons, teams, and registrations.
- `requirements.txt`: Python package dependencies for the backend.

## Contributing

Contributions are welcome! If you'd like to improve the project, please fork the repository and use a feature branch. Pull requests are warmly welcome.

## License

This project is open-source and available under the [MIT License](LICENSE).
