"""Tests for the Mergington High School API"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_dict(self):
        """Test that GET /activities returns a dictionary of activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        assert isinstance(response.json(), dict)

    def test_get_activities_has_required_fields(self):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()

        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_activities_list_not_empty(self):
        """Test that activities list is not empty"""
        response = client.get("/activities")
        activities = response.json()
        assert len(activities) > 0

    def test_specific_activity_exists(self):
        """Test that specific activities exist"""
        response = client.get("/activities")
        activities = response.json()
        assert "Chess Club" in activities
        assert "Programming Class" in activities


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newemail@mergington.edu"
        )
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]

    def test_signup_adds_participant(self):
        """Test that signup actually adds participant to activity"""
        email = "testuser123@mergington.edu"
        
        # Get initial count
        response = client.get("/activities")
        initial_count = len(response.json()["Basketball"]["participants"])

        # Sign up
        signup_response = client.post(
            "/activities/Basketball/signup?email=" + email
        )
        assert signup_response.status_code == 200

        # Check count increased
        response = client.get("/activities")
        new_count = len(response.json()["Basketball"]["participants"])
        assert new_count == initial_count + 1
        assert email in response.json()["Basketball"]["participants"]

    def test_signup_duplicate_email_fails(self):
        """Test that signing up with same email twice fails"""
        email = "duplicate@mergington.edu"

        # First signup
        response1 = client.post(
            "/activities/Chess%20Club/signup?email=" + email
        )
        assert response1.status_code == 200

        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Chess%20Club/signup?email=" + email
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]

    def test_signup_nonexistent_activity_fails(self):
        """Test that signup for non-existent activity fails"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]


class TestUnregisterEndpoint:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self):
        """Test successful unregister from an activity"""
        email = "unregister_test@mergington.edu"

        # First signup
        client.post("/activities/Tennis%20Club/signup?email=" + email)

        # Then unregister
        response = client.delete(
            "/activities/Tennis%20Club/unregister?email=" + email
        )
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]

    def test_unregister_removes_participant(self):
        """Test that unregister actually removes participant from activity"""
        email = "remove_test@mergington.edu"

        # Sign up
        client.post("/activities/Drama%20Club/signup?email=" + email)

        # Verify added
        response = client.get("/activities")
        assert email in response.json()["Drama Club"]["participants"]

        # Unregister
        client.delete("/activities/Drama%20Club/unregister?email=" + email)

        # Verify removed
        response = client.get("/activities")
        assert email not in response.json()["Drama Club"]["participants"]

    def test_unregister_nonexistent_email_fails(self):
        """Test that unregistering non-existent email fails"""
        response = client.delete(
            "/activities/Science%20Club/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"]

    def test_unregister_nonexistent_activity_fails(self):
        """Test that unregistering from non-existent activity fails"""
        response = client.delete(
            "/activities/Fake%20Activity/unregister?email=test@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
