# Skill-Based Internship & Project Matching Platform

A fair, transparent, and fully explainable web application for matching candidates with internship opportunities based on their skills and experience.

## Features

- **Candidate Registration**: Register with skills, experience, and availability
- **Internship Posting**: Companies can post internship requirements with skill weights
- **Intelligent Matching Algorithm**: Weighted competency scoring system
- **Explainability**: Detailed breakdowns of why candidates matched
- **Fair Ranking**: Based purely on competency metrics, no demographic data
- **Responsive Design**: Works on desktop and mobile devices

## Technology Stack

- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Backend**: Python Flask
- **Database**: SQLite
- **No External Dependencies** (except Flask and Flask-CORS)

## Project Structure

```
resume_builder/
├── app.py                 # Main Flask application
├── database.py            # Database setup and helpers
├── requirements.txt       # Python dependencies
├── static/
│   ├── css/
│   │   └── style.css     # All styling
│   └── js/
│       └── script.js     # Client-side JavaScript
└── templates/
    ├── index.html        # Home page
    ├── candidate_form.html   # Candidate registration
    ├── project_form.html     # Internship posting
    └── results.html      # Matching results display
```

## Installation & Setup

### Prerequisites
- Python 3.7+
- pip (Python package manager)

### Step 1: Clone or Download the Repository

```bash
cd resume_builder
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 3: Initialize the Database

```bash
python database.py
```

This will create `internship_matching.db` SQLite database with all required tables.

### Step 4: Run the Application

```bash
python app.py
```

The application will start at `http://localhost:5000`

## Usage

### For Candidates

1. Go to the home page
2. Click "Register as Candidate"
3. Fill in your details:
   - Full name and email
   - Add at least one skill with proficiency level (Beginner/Intermediate/Advanced)
   - Enter experience in months, projects completed, and certifications
   - Select availability (Full-time/Part-time)
4. Submit the form

### For Companies

1. Go to the home page
2. Click "Post an Internship"
3. Fill in your details:
   - Company name, role title, duration
   - Add required skills with:
     - Skill name
     - Weight (importance %)
     - Minimum level required
   - Optionally specify monthly stipend
4. Submit the form
5. You'll be automatically redirected to view matching candidates

### Viewing Matches

After posting an internship, you'll see:
- Candidates ranked by match score (highest first)
- Match percentage for each candidate
- Click "View Details" to see:
  - Strong matches: Skills the candidate excels at
  - Partial matches: Skills below required level
  - Missing skills: Skills not possessed
  - Detailed explanation

## Matching Algorithm

The algorithm calculates a weighted competency score:

```
For each required skill:
    If candidate has skill:
        If candidate_level >= minimum_required:
            score += (candidate_level × weight)
        Else:
            score += (candidate_level / minimum_required × weight × 0.5)
    Else:
        score += 0

Final_Score = (total_score / total_weights) × 100
```

### Score Interpretation

- **85%+**: Excellent fit
- **70-84%**: Strong candidate
- **50-69%**: Moderate fit
- **Below 50%**: May require training

## Fairness Features

✓ **No Demographic Data**: Gender, caste, religion, college name NOT collected
✓ **Skill-Based Only**: Rankings depend only on skills and experience
✓ **Transparent Scoring**: Each candidate's match is fully explained
✓ **Fairness Notice**: Displayed to all users
✓ **Explainability**: Detailed breakdowns for each match

## Database Schema

### candidates
- id (INTEGER PRIMARY KEY)
- name (TEXT)
- email (TEXT)
- experience_months (INTEGER)
- projects_completed (INTEGER)
- certifications (INTEGER)
- availability (TEXT)
- created_at (TIMESTAMP)

### candidate_skills
- id (INTEGER PRIMARY KEY)
- candidate_id (INTEGER FOREIGN KEY)
- skill_name (TEXT)
- skill_level (INTEGER: 1-3)

### projects
- id (INTEGER PRIMARY KEY)
- company_name (TEXT)
- role_title (TEXT)
- duration (TEXT)
- stipend_amount (REAL)
- created_at (TIMESTAMP)

### project_skills
- id (INTEGER PRIMARY KEY)
- project_id (INTEGER FOREIGN KEY)
- skill_name (TEXT)
- weight (REAL: 0-100)
- minimum_level (INTEGER: 1-3)

### match_results
- id (INTEGER PRIMARY KEY)
- project_id (INTEGER FOREIGN KEY)
- candidate_id (INTEGER FOREIGN KEY)
- match_score (REAL)
- strong_matches (TEXT: JSON)
- partial_matches (TEXT: JSON)
- missing_skills (TEXT: JSON)
- explanation (TEXT)
- created_at (TIMESTAMP)

## API Endpoints

### GET /
Home page with candidate and internship sections

### POST /add_candidate
Register a new candidate
```json
{
    "name": "John Doe",
    "email": "john@example.com",
    "experience_months": 6,
    "projects_completed": 3,
    "certifications": 1,
    "availability": "Full-time",
    "skills": [
        {"skill_name": "Python", "skill_level": 3},
        {"skill_name": "JavaScript", "skill_level": 2}
    ]
}
```

### POST /add_project
Post a new internship
```json
{
    "company_name": "Tech Corp",
    "role_title": "Backend Developer Intern",
    "duration": "3 months",
    "stipend_offered": true,
    "stipend_amount": 15000,
    "required_skills": [
        {"skill_name": "Python", "weight": 40, "minimum_level": 2},
        {"skill_name": "Django", "weight": 30, "minimum_level": 2},
        {"skill_name": "SQL", "weight": 30, "minimum_level": 1}
    ]
}
```

### GET /match/<project_id>
Get ranked candidates for a project

### GET /candidates
Get all registered candidates

### GET /projects
Get all posted internships

## Customization

### Modify Scoring Weights

Edit the `calculate_match_score()` function in `app.py`:

```python
score_contribution = candidate_level * weight
```

### Change Skill Levels

Skill levels are currently 1-3 (Beginner, Intermediate, Advanced). Modify in:
- HTML forms
- Database schema
- JavaScript display logic

### Adjust Styling

All CSS is in `static/css/style.css`. The design uses:
- Color scheme: Purple (#667eea) and green (#48bb78)
- Responsive grid layout
- Mobile-first approach

## Troubleshooting

### Database Already Exists
Delete `internship_matching.db` and run `python database.py` again

### Port 5000 Already in Use
Change the port in `app.py`:
```python
app.run(debug=True, port=8000)  # Use port 8000 instead
```

### CORS Issues
CORS is already enabled. If issues persist, check that Flask-CORS is installed:
```bash
pip install Flask-CORS
```

### Database Not Initializing
Ensure the current directory is writable. The database file is created in the working directory.

## Testing

### Add Sample Candidate
1. Go to `/candidate_form`
2. Fill form with sample data:
   - Name: "Alice Johnson"
   - Email: "alice@example.com"
   - Skills: Python (Advanced), JavaScript (Intermediate)
   - Experience: 12 months
   - Projects: 5
   - Certifications: 2
   - Availability: Full-time

### Add Sample Project
1. Go to `/project_form`
2. Fill form with:
   - Company: "StartupXYZ"
   - Role: "Full Stack Developer"
   - Duration: "3 months"
   - Skills: Python (weight 30%, min level 2), JavaScript (weight 40%, min level 2), React (weight 30%, min level 1)
   - Stipend: ₹20,000/month

### View Results
Click "View Matches" on the project listing to see ranking.

## Future Enhancements

- [ ] User authentication and accounts
- [ ] Candidate profiles with portfolio links
- [ ] Email notifications for matches
- [ ] Advanced filtering and search
- [ ] Admin dashboard
- [ ] Interview scheduling system
- [ ] Candidate feedback ratings
- [ ] Machine learning recommendations
- [ ] Integration with job boards

## License

This project is open-source and available for educational and commercial use.

## Support

For issues or questions, please create an issue in the GitHub repository.

---

**Built with ❤️ for fair, transparent, skill-based matching**