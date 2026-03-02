"""
Tests for the unregister endpoint (DELETE /activities/{activity_name}/participants).
"""

import pytest


def test_unregister_successful(client):
    """Test successful unregistration from an activity"""
    email = "michael@mergington.edu"  # Existing participant in Chess Club
    
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": email}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert email in data["message"]
    assert "Unregistered" in data["message"]


def test_unregister_removes_participant(client):
    """Test that unregister actually removes the participant"""
    # First signup someone
    email = "unregister.test@mergington.edu"
    client.post(
        "/activities/Basketball Team/signup",
        params={"email": email}
    )
    
    # Verify they're registered
    activities = client.get("/activities").json()
    assert email in activities["Basketball Team"]["participants"]
    
    # Unregister
    response = client.delete(
        "/activities/Basketball Team/participants",
        params={"email": email}
    )
    assert response.status_code == 200
    
    # Verify they're removed
    activities = client.get("/activities").json()
    assert email not in activities["Basketball Team"]["participants"]


def test_unregister_activity_not_found(client):
    """Test unregister from non-existent activity returns 404"""
    response = client.delete(
        "/activities/Fake Activity/participants",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_unregister_student_not_registered(client):
    """Test unregister when student is not registered returns 404"""
    response = client.delete(
        "/activities/Chess Club/participants",
        params={"email": "notregistered@mergington.edu"}
    )
    assert response.status_code == 404
    
    data = response.json()
    assert "not registered" in data["detail"].lower()


def test_unregister_from_different_activities(client):
    """Test unregister works across different activities"""
    email = "multi.activity@mergington.edu"
    
    # Signup to multiple activities
    activities = ["Chess Club", "Drama Club", "Science Club"]
    for activity in activities:
        client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
    
    # Unregister from each
    for activity in activities:
        response = client.delete(
            f"/activities/{activity}/participants",
            params={"email": email}
        )
        assert response.status_code == 200
    
    # Verify student is gone from all activities
    activities_data = client.get("/activities").json()
    for activity in activities:
        assert email not in activities_data[activity]["participants"]


def test_unregister_frees_up_spot(client):
    """Test that unregistering frees up a spot for new signups"""
    activity = "Tennis Club"
    email_to_unregister = "lucas@mergington.edu"  # Initial participant
    email_new = "new.student@mergington.edu"
    
    # Fill up the activity (Tennis Club has max 10)
    initial = client.get("/activities").json()
    max_participants = initial[activity]["max_participants"]
    current_count = len(initial[activity]["participants"])
    
    # Fill remaining spots
    for i in range(max_participants - current_count):
        filler_email = f"filler{i}@mergington.edu"
        client.post(
            f"/activities/{activity}/signup",
            params={"email": filler_email}
        )
    
    # Verify it's full
    full_activity = client.get("/activities").json()
    assert len(full_activity[activity]["participants"]) == max_participants
    
    # Unregister someone
    client.delete(
        f"/activities/{activity}/participants",
        params={"email": email_to_unregister}
    )
    
    # Now we should be able to signup
    response = client.post(
        f"/activities/{activity}/signup",
        params={"email": email_new}
    )
    assert response.status_code == 200


def test_unregister_double_unregister(client):
    """Test that unregistering twice from same activity fails on second attempt"""
    email = "double.unreg@mergington.edu"
    activity = "Art Studio"
    
    # Signup
    client.post(
        f"/activities/{activity}/signup",
        params={"email": email}
    )
    
    # First unregister should succeed
    response1 = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email}
    )
    assert response1.status_code == 200
    
    # Second unregister should fail
    response2 = client.delete(
        f"/activities/{activity}/participants",
        params={"email": email}
    )
    assert response2.status_code == 404
    assert "not registered" in response2.json()["detail"].lower()


def test_unregister_missing_email_parameter(client):
    """Test unregister without email parameter"""
    response = client.delete(
        "/activities/Chess Club/participants",
        params={}
    )
    assert response.status_code == 422


def test_unregister_missing_activity_name(client):
    """Test unregister without activity name in path"""
    response = client.delete(
        "/activities//participants",
        params={"email": "test@mergington.edu"}
    )
    assert response.status_code == 404 or response.status_code == 422


def test_unregister_response_format(client):
    """Test that unregister response has correct format"""
    email = "format.unregister@mergington.edu"
    
    # Signup first
    client.post(
        "/activities/Debate Team/signup",
        params={"email": email}
    )
    
    # Unregister
    response = client.delete(
        "/activities/Debate Team/participants",
        params={"email": email}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert "message" in data
    assert isinstance(data["message"], str)


def test_unregister_does_not_affect_other_participants(client):
    """Test that unregistering one person doesn't affect others"""
    activity = "Programming Class"
    email_to_remove = "emma@mergington.edu"  # Initial participant
    
    # Get initial participants (excluding the one we'll remove)
    initial = client.get("/activities").json()
    other_participants = [
        p for p in initial[activity]["participants"] 
        if p != email_to_remove
    ]
    
    # Unregister
    client.delete(
        f"/activities/{activity}/participants",
        params={"email": email_to_remove}
    )
    
    # Verify others are still there
    updated = client.get("/activities").json()
    for participant in other_participants:
        assert participant in updated[activity]["participants"]
    
    # Verify the removed person is gone
    assert email_to_remove not in updated[activity]["participants"]
