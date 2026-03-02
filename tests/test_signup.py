"""
Tests for the signup endpoint (POST /activities/{activity_name}/signup).
"""

import pytest


def test_signup_successful(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newtudent@mergington.edu"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "newtudent@mergington.edu" in data["message"]
    assert "Chess Club" in data["message"]


def test_signup_adds_participant(client):
    """Test that signup actually adds the participant to the activity"""
    email = "test.signup@mergington.edu"
    
    # Get initial activity state
    initial = client.get("/activities").json()
    initial_count = len(initial["Art Studio"]["participants"])
    
    # Signup
    response = client.post(
        "/activities/Art Studio/signup",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify participant was added
    updated = client.get("/activities").json()
    assert len(updated["Art Studio"]["participants"]) == initial_count + 1
    assert email in updated["Art Studio"]["participants"]


def test_signup_activity_not_found(client):
    """Test signup for non-existent activity returns 404"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_duplicate_registration(client):
    """Test that duplicate signup returns 400 error"""
    email = "michael@mergington.edu"  # Already in Chess Club
    
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": email}
    )
    assert response.status_code == 400
    
    data = response.json()
    assert "already signed up" in data["detail"].lower()


def test_signup_activity_full(client):
    """Test signup when activity is at capacity"""
    # Tennis Club has max_participants: 10, let's fill it
    initial = client.get("/activities").json()
    tennis_participants = initial["Tennis Club"]["participants"]
    
    # Fill remaining spots
    current_count = len(tennis_participants)
    max_count = initial["Tennis Club"]["max_participants"]
    
    # Add participants until full
    for i in range(max_count - current_count):
        email = f"filler{i}@mergington.edu"
        response = client.post(
            "/activities/Tennis Club/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Try to add one more when full
    full_response = client.post(
        "/activities/Tennis Club/signup",
        params={"email": "extra@mergington.edu"}
    )
    assert full_response.status_code == 400
    
    data = full_response.json()
    assert "full" in data["detail"].lower()


def test_signup_with_different_activities(client):
    """Test signup works across different activities"""
    email = "versatile.student@mergington.edu"
    
    activities = ["Chess Club", "Drama Club", "Science Club"]
    
    for activity in activities:
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify student is in all activities
    activities_data = client.get("/activities").json()
    for activity in activities:
        assert email in activities_data[activity]["participants"]


def test_signup_multiple_students_same_activity(client):
    """Test multiple different students can signup for the same activity"""
    students = [
        "john.doe@mergington.edu",
        "jane.smith@mergington.edu",
        "bob.johnson@mergington.edu"
    ]
    
    for student in students:
        response = client.post(
            "/activities/Drama Club/signup",
            params={"email": student}
        )
        assert response.status_code == 200
    
    # Verify all students are registered
    activities_data = client.get("/activities").json()
    for student in students:
        assert student in activities_data["Drama Club"]["participants"]


def test_signup_missing_email_parameter(client):
    """Test signup without email parameter"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={}
    )
    # FastAPI will return 422 for missing required parameter
    assert response.status_code == 422


def test_signup_missing_activity_name(client):
    """Test signup without activity name in path"""
    response = client.post(
        "/activities//signup",
        params={"email": "test@mergington.edu"}
    )
    # This will return 404 as the path won't match
    assert response.status_code == 404 or response.status_code == 422


def test_signup_email_case_sensitive(client):
    """Test that email addresses are case-sensitive for signup"""
    email1 = "student@mergington.edu"
    email2 = "Student@mergington.edu"  # Different case
    
    response1 = client.post(
        "/activities/Programming Class/signup",
        params={"email": email1}
    )
    assert response1.status_code == 200
    
    # Different case should be treated as different email
    response2 = client.post(
        "/activities/Programming Class/signup",
        params={"email": email2}
    )
    # This may succeed depending on business logic - we test the actual behavior
    # Based on code, emails are compared directly (case-sensitive)
    assert response2.status_code == 200  # Different email due to case


def test_signup_response_format(client):
    """Test that signup response has correct format"""
    response = client.post(
        "/activities/Gym Class/signup",
        params={"email": "format.test@mergington.edu"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data
    assert isinstance(data["message"], str)
