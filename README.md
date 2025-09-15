# Flask Application

This is a simple Flask web application that demonstrates the basic structure and functionality of a Flask project.

## Project Structure

```
flask-app
├── app
│   ├── __init__.py
│   ├── routes.py
│   ├── models.py
│   └── templates
│       ├── base.html
│       └── index.html
├── static
│   ├── css
│   │   └── style.css
│   └── js
│       └── main.js
├── tests
│   ├── __init__.py
│   └── test_app.py
├── requirements.txt
├── config.py
├── run.py
└── README.md
```

## Setup Instructions

1. **Clone the repository:**
   ```
   git clone <repository-url>
   cd flask-app
   ```

2. **Create a virtual environment:**
   ```
   python -m venv venv
   ```

3. **Activate the virtual environment:**
   - On Windows:
     ```
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```
     source venv/bin/activate
     ```

4. **Install the required libraries:**
   ```
   pip install -r requirements.txt
   ```

## Running the Application

To run the application, execute the following command:

```
python run.py
```

The application will be accessible at `http://127.0.0.1:5000`.

## API Endpoints

- **GET /**: Returns an HTML heading.
- **GET /api/v1/status**: Returns a JSON object with the server status and current UTC timestamp.

## Testing

To run the tests, ensure the virtual environment is activated and execute:

```
pytest
```

## License

This project is licensed under the MIT License.