"""
Tests for the activities list endpoint (GET /activities).
"""

def test_get_activities_returns_all_activities(client):
    """Test that GET /activities returns all available activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    
    # Verify all expected activities are present
    expected_activities = {
        "Chess Club", "Programming Class", "Gym Class", "Basketball Team",
        "Tennis Club", "Drama Club", "Art Studio", "Debate Team", "Science Club"
    }
    assert set(data.keys()) == expected_activities


def test_get_activities_response_structure(client):
    """Test that each activity has the correct structure"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    for activity_name, activity_data in data.items():
        assert "description" in activity_data
        assert "schedule" in activity_data
        assert "max_participants" in activity_data
        assert "participants" in activity_data
        
        # Verify types
        assert isinstance(activity_data["description"], str)
        assert isinstance(activity_data["schedule"], str)
        assert isinstance(activity_data["max_participants"], int)
        assert isinstance(activity_data["participants"], list)


def test_get_activities_initial_participants(client):
    """Test that activities have participants initialized correctly"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    
    # Chess Club should have 2 initial participants
    assert len(data["Chess Club"]["participants"]) == 2
    assert "michael@mergington.edu" in data["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in data["Chess Club"]["participants"]
    
    # Programming Class should have 2 initial participants
    assert len(data["Programming Class"]["participants"]) == 2


def test_get_activities_empty_response_not_empty(client):
    """Test that the activities list is not empty"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) > 0  # Should have at least one activity


def test_get_activities_max_participants_valid(client):
    """Test that max_participants are reasonable positive integers"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    for activity_name, activity_data in data.items():
        assert activity_data["max_participants"] > 0
        assert isinstance(activity_data["max_participants"], int)


def test_get_activities_participants_count_not_exceeded(client):
    """Test that participant count doesn't exceed max_participants"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    for activity_name, activity_data in data.items():
        assert len(activity_data["participants"]) <= activity_data["max_participants"]
