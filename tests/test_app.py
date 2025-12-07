"""
Tests for the Mergington High School Activities API
"""
import sys
from pathlib import Path

# Add the src directory to the path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
from fastapi.testclient import TestClient
from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state after each test"""
    initial_state = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Soccer Team": {
            "description": "Join the school soccer team and compete in matches",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["alex@mergington.edu", "lucas@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Practice basketball skills and play friendly games",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 15,
            "participants": ["mia@mergington.edu", "noah@mergington.edu"]
        },
        "Art Workshop": {
            "description": "Explore painting, drawing, and sculpture techniques",
            "schedule": "Mondays, 4:00 PM - 5:30 PM",
            "max_participants": 16,
            "participants": ["ava@mergington.edu", "liam@mergington.edu"]
        },
        "Drama Club": {
            "description": "Act, direct, and produce school plays and performances",
            "schedule": "Fridays, 3:30 PM - 5:30 PM",
            "max_participants": 20,
            "participants": ["ella@mergington.edu", "jack@mergington.edu"]
        },
        "Mathletes": {
            "description": "Compete in math competitions and solve challenging problems",
            "schedule": "Tuesdays, 4:00 PM - 5:00 PM",
            "max_participants": 10,
            "participants": ["ethan@mergington.edu", "grace@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts",
            "schedule": "Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["chloe@mergington.edu", "ben@mergington.edu"]
        }
    }
    
    # Save original state
    original_state = {k: v.copy() for k, v in activities.items()}
    
    yield
    
    # Reset to initial state after test
    activities.clear()
    activities.update({k: {**v, "participants": list(v["participants"])} for k, v in initial_state.items()})


class TestRoot:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for getting activities"""
    
    def test_get_activities_returns_dict(self, client, reset_activities):
        """Test that get_activities returns a dictionary"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
    
    def test_get_activities_contains_chess_club(self, client, reset_activities):
        """Test that activities list includes Chess Club"""
        response = client.get("/activities")
        data = response.json()
        assert "Chess Club" in data
    
    def test_get_activities_has_correct_structure(self, client, reset_activities):
        """Test that activity structure contains required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
    
    def test_get_activities_participants_is_list(self, client, reset_activities):
        """Test that participants field is a list"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        assert isinstance(activity["participants"], list)
        assert "michael@mergington.edu" in activity["participants"]


class TestSignup:
    """Tests for signing up for activities"""
    
    def test_signup_new_student(self, client, reset_activities):
        """Test signing up a new student for an activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]
    
    def test_signup_adds_participant(self, client, reset_activities):
        """Test that signup actually adds the participant to the activity"""
        initial_count = len(activities["Chess Club"]["participants"])
        
        client.post("/activities/Chess Club/signup?email=test@mergington.edu")
        
        assert len(activities["Chess Club"]["participants"]) == initial_count + 1
        assert "test@mergington.edu" in activities["Chess Club"]["participants"]
    
    def test_signup_nonexistent_activity(self, client, reset_activities):
        """Test signing up for an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_signup_already_registered(self, client, reset_activities):
        """Test that a student can't sign up twice for the same activity"""
        response = client.post(
            "/activities/Chess Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()
    
    def test_signup_multiple_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities"""
        email = "multiplejoiners@mergington.edu"
        
        response1 = client.post(f"/activities/Chess Club/signup?email={email}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response2.status_code == 200
        
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]


class TestUnregister:
    """Tests for unregistering from activities"""
    
    def test_unregister_existing_student(self, client, reset_activities):
        """Test unregistering an existing student from an activity"""
        response = client.post(
            "/activities/Chess Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        data = response.json()
        assert "Removed" in data["message"]
        assert "michael@mergington.edu" in data["message"]
    
    def test_unregister_removes_participant(self, client, reset_activities):
        """Test that unregister actually removes the participant"""
        initial_count = len(activities["Chess Club"]["participants"])
        
        client.post("/activities/Chess Club/unregister?email=michael@mergington.edu")
        
        assert len(activities["Chess Club"]["participants"]) == initial_count - 1
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    
    def test_unregister_nonexistent_activity(self, client, reset_activities):
        """Test unregistering from an activity that doesn't exist"""
        response = client.post(
            "/activities/Nonexistent Club/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_unregister_not_registered_student(self, client, reset_activities):
        """Test that unregistering a student not in the activity fails"""
        response = client.post(
            "/activities/Chess Club/unregister?email=notstudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()
    
    def test_signup_then_unregister(self, client, reset_activities):
        """Test signing up and then unregistering a student"""
        email = "tempstudent@mergington.edu"
        
        # Sign up
        response1 = client.post(f"/activities/Programming Class/signup?email={email}")
        assert response1.status_code == 200
        assert email in activities["Programming Class"]["participants"]
        
        # Unregister
        response2 = client.post(f"/activities/Programming Class/unregister?email={email}")
        assert response2.status_code == 200
        assert email not in activities["Programming Class"]["participants"]
